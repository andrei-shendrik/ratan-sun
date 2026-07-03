import logging
import signal
import sys
import time
from pathlib import Path

import psutil

from bin2fits_fast_acquisition_1_3ghz_nodb.services.fast_acquisition_1_3ghz_processing_director import \
    FastAcquisition1To3GHzObservationProcessingDirector
from bin2fits_fast_acquisition_1_3ghz_nodb.settings.bin2fits_fast_acquisition_1_3ghz_settings import \
    Bin2FitsFastAcquisition1To3GHzSettings
from ratanpy.logging_conf.logger_configurator import LoggerConfigurator
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.domain import ProcessingResult
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.processing_wrapper import FastAcquisition1To3GHzProcessingWrapper


class ParallelWorker:
    """ Класс для выполнения задачи внутри дочернего процесса. """

    @staticmethod
    def init_pool(worker_max_ram_gb: float):
        """
        Вызывается при старте каждого дочернего процесса в пуле.
        Приказывает игнорировать сигнал ctrl+c (чтобы доделать текущий файл,
        пока главный процесс управляет мягкой остановкой пула)
        """
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        if sys.platform != 'win32':
            import resource
            bytes_limit = int(worker_max_ram_gb * 1024 * 1024 * 1024)
            try:
                # RLIMIT_AS (Address Space) - общий объем виртуальной памяти процесса
                resource.setrlimit(resource.RLIMIT_AS, (bytes_limit, bytes_limit))
            except ValueError:
                pass

    def __init__(self, settings: Bin2FitsFastAcquisition1To3GHzSettings):
        self._settings = settings
        director = FastAcquisition1To3GHzObservationProcessingDirector()
        self._wrapper = FastAcquisition1To3GHzProcessingWrapper(director)

    def _wait_for_ram(self, filename: str, logger: logging.Logger):
        """ Ожидание RAM """
        min_ram_gb = self._settings.resources.min_free_ram_gb
        while True:
            available_gb = psutil.virtual_memory().available / (1024 ** 3)
            if available_gb > min_ram_gb:
                break
            logger.warning(f"[{filename}] System RAM low ({available_gb:.1f}GB). Waiting...")
            time.sleep(5)

    def run(self, bin_file: Path, fits_dir: Path, overwrite: bool, file_index: int, total_files: int) -> ProcessingResult:
        # 1. Изоляция логов
        configurator = LoggerConfigurator(self._settings.logging)
        list_handler = configurator.configure(is_worker=True)
        logger = logging.getLogger("parallel_worker")

        logger.info(f"=== [File {file_index} of {total_files}] === [{bin_file.name}] ===")

        # 2. Проверка ресурсов
        self._wait_for_ram(bin_file.name, logger)

        # 3. Выполнение
        result = self._wrapper.process(bin_file, fits_dir, overwrite)

        # 4. Логирование итогов
        if result.status.value == 'success':
            logger.info \
                (f"[{bin_file.name}] Stats -> Time: {result.time_taken_sec:.1f}s | Peak RAM: {result.peak_memory_mb:.1f} MB")

        if list_handler: result.log_records = list_handler.records
        return result

# Точка входа для ProcessPoolExecutor (т.к. метод экземпляра класса не всегда хорошо сериализуется)
def execute_worker_task(bin_file: Path, fits_dir: Path, overwrite: bool, index: int, total: int, settings: Bin2FitsFastAcquisition1To3GHzSettings) -> ProcessingResult:
    worker = ParallelWorker(settings)
    return worker.run(bin_file, fits_dir, overwrite, index, total)