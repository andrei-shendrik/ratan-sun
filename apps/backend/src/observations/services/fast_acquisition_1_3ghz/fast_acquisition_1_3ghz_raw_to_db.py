import logging
from datetime import datetime
from pathlib import Path

from dateutil.relativedelta import relativedelta
from django.core.cache import cache

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.models import RawObservationFastAcquisition1To3GHz
from observations.services.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_filename_parser import \
    FastAcquisition1To3GHzFilenameParser
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.observation_file_filter import ObservationFileFilter
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_file_scanner import FastAcquisition1To3GHzFileScanner

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzRawToDB:
    """
    Сервис отслеживает поддиректории текущего и предыдущего месяца архива сырых данных
    комплекса Fast Acquisition 1-3 GHz и добавляет новые наблюдения в БД.
    """

    def __init__(self, settings: FastAcquisition1To3GHzSettings):
        self._settings = settings
        self._service_name = "Fast Acquisition 1-3 GHz Raw to DB"
        self._cache_key = f"service_state_{self.__class__.__name__}"
        self._raw_base_path = self._settings.bin_archive.resolve()

    def _get_target_dirs(self) -> list[Path]:
        """
        поиск директорий по паттерну YYYY/MM на любом уровне вложенности от базовой директории,
        для отслеживания берутся директории текущего и предыдущего месяца
        """
        today = datetime.today()
        prev_month = today - relativedelta(months=1)

        date_paths = [
            f"{prev_month.year}/{prev_month.month:02d}",
            f"{today.year}/{today.month:02d}"
        ]

        target_dirs = []
        for suffix in date_paths:
            for matched_dir in self._raw_base_path.glob(f"**/{suffix}"): # на любой глубине
                if matched_dir.is_dir():
                    target_dirs.append(matched_dir)
        return target_dirs

    def _log_state_changes(self, current_dirs: list[Path]):
        """
        Пишет инфо при старте сервиса и при смене директорий.

        Должен быть прописан cache в settings.py
        """

        relative_paths = []
        for d in current_dirs:
            if d.is_relative_to(self._raw_base_path):
                relative_paths.append(d.relative_to(self._raw_base_path).as_posix())
            else:
                relative_paths.append(d.as_posix())

        def get_absolute_log_string(rel_paths_str: list[str]) -> str:
            if not rel_paths_str:
                return "None"
            abs_paths = [str(self._raw_base_path / rel_path) for rel_path in rel_paths_str]
            return ", ".join(abs_paths)

        # пути в строки для сериализации в redis
        current_dirs_str = sorted(relative_paths)
        # current_dirs_str = sorted([str(d) for d in current_dirs])

        # чтение прошлого состояние из redis
        previous_dirs_str = cache.get(self._cache_key)

        if previous_dirs_str is None:
            # если значения нет в кэше, значит это первый запуск
            logger.info(f"Service '{self._service_name}' has started")
            logger.info(f"Monitoring directories: {get_absolute_log_string(current_dirs_str)}")
            # logger.info(f"Monitoring directories: {', '.join(current_dirs_str) if current_dirs_str else 'None'}")
            cache.set(self._cache_key, current_dirs_str, timeout=None) # вечное хранение
        elif current_dirs_str != previous_dirs_str:
            # logger.info(
            #     f"[{self._service_name}] Monitored directories have been changed: {', '.join(current_dirs_str)}")
            logger.info(
                f"[{self._service_name}] Monitored directories have been changed: {get_absolute_log_string(current_dirs_str)}")
            cache.set(self._cache_key, current_dirs_str, timeout=None) # вечное хранение

    def _find_new_files(self, target_dirs: list[Path]) -> list[Path]:
        """ сканирует директории и сверяет с БД. Возвращает только те файлы, которых нет в БД. """

        file_filter = ObservationFileFilter(
            self._settings.file_filters.allowed_patterns,
            self._settings.file_filters.forbidden_patterns
        )
        scanner = FastAcquisition1To3GHzFileScanner(file_filter)

        found_files = []
        for d in target_dirs:
            if d.exists():
                found_files.extend(list(scanner.scan(d)))

        if not found_files:
            return []

        existing_filenames = set(RawObservationFastAcquisition1To3GHz.objects.filter(
            filename__in=[f.name for f in found_files]
        ).values_list('filename', flat=True))

        return [f for f in found_files if f.name not in existing_filenames]

    def _register_files_in_db(self, new_files: list[Path]) -> int:
        """ Парсит имена и сохраняет файлы в базу. Возвращает количество созданных задач. """
        added_count = 0

        for file_path in new_files:
            resolved_file = file_path.resolve()
            parent_dir = resolved_file.parent
            if not parent_dir.is_relative_to(self._raw_base_path):
                logger.error(f"File {resolved_file.name}: outside base path")
                continue

            relative_dir_str = parent_dir.relative_to(self._raw_base_path).as_posix()
            if relative_dir_str == ".":
                relative_dir_str = ""

            try:
                parsed = FastAcquisition1To3GHzFilenameParser.parse(resolved_file.name)
            except ValueError as e:
                logger.warning(f"Failed to parse filename {resolved_file.name}: {e}. Skipping.")
                continue

            try:
                raw, created = RawObservationFastAcquisition1To3GHz.objects.get_or_create(
                    filename=file_path.name,
                    defaults={
                        'relative_path': relative_dir_str,
                        'datetime_obs_utc': parsed.datetime_utc,
                        'object_of_observation': parsed.object_of_observation,
                        'azimuth': parsed.azimuth
                    }
                )
                logger.info(f"New file '{file_path.name}' successfully added to DB")
                if created:
                    added_count += 1
                    logger.info(f"Created processing bin2fits job for '{file_path.name}'")

            except Exception as e:
                logger.critical(f"Database error saving {file_path.name}: {e}", exc_info=True)
        return added_count

    def execute(self) -> int:
        """
        защита от пустого монтирования docker:
        если базовая директория пуста, то прерывание работы
        """
        if not any(self._raw_base_path.iterdir()):
            logger.critical(f"Base path {self._raw_base_path} is empty. Mount failure?")
            return 0

        target_dirs = self._get_target_dirs()
        self._log_state_changes(target_dirs)

        new_files = self._find_new_files(target_dirs)
        if not new_files:
            return 0

        return self._register_files_in_db(new_files)