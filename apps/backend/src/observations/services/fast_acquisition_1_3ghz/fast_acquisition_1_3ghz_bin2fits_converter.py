import logging

import psutil
from django.db import transaction

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.enums import ProcessingJobStatus
from observations.models import ProcessingJobBin2FitsFastAcquisition1To3GHz
from observations.services.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_processing_director import \
    FastAcquisition1To3GHzObservationProcessingDirector
from ratanpy.logging_conf.logger_configurator import ListLogHandler
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.domain import ProcessingStatus
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.processing_wrapper import FastAcquisition1To3GHzProcessingWrapper

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzBin2FitsConverter:
    def __init__(self, settings: FastAcquisition1To3GHzSettings):
        self._settings = settings

    def execute(self, job_id: str) -> bool:
        """
        Конвертация bin2fits. Возврат true в случае успешного выполнения.
        Выбрасывает MemoryError, если RAM не удовлетворяет требованию минимальной
        свободной памяти (используется для возврата задачи в очередь)
        """
        job = ProcessingJobBin2FitsFastAcquisition1To3GHz.objects.select_related('raw_observation').get(id=job_id)

        # если в задаче БД задан min_free_ram_gb, используется он, иначе берется из настроек
        min_ram_gb = job.min_free_ram_gb if job.min_free_ram_gb is not None else self._settings.resources.min_free_ram_gb
        max_worker_ram_gb = job.max_worker_ram_gb if job.max_worker_ram_gb is not None else self._settings.resources.worker_max_ram_gb

        # проверка RAM
        available_gb = psutil.virtual_memory().available / (1024 ** 3)
        if available_gb < min_ram_gb:
            logger.warning(f"Job {job_id}: System RAM low ({available_gb:.1f}GB < {min_ram_gb}GB). Waiting...")
            # выброс ошибки: celery должен отложить задачу и отправить обратно в redis
            raise MemoryError(f"Insufficient RAM: {available_gb:.1f}GB < {min_ram_gb}GB")

        # блокировка записи в БД (защита от параллельного запуска)
        with transaction.atomic():
            # select_for_update ставит Row-Level Lock в PostgreSQL
            locked_job = ProcessingJobBin2FitsFastAcquisition1To3GHz.objects.select_for_update().get(id=job_id)

            if locked_job.status != ProcessingJobStatus.UNPROCESSED.value:
                logger.warning(f"Job {job_id} is no longer UNPROCESSED (Current: {locked_job.status}). Skipping.")
                return False

            # смена статуса на PROCESSING, чтобы другой воркер не взял эту задачу
            locked_job.status = ProcessingJobStatus.PROCESSING.value
            locked_job.save(update_fields=['status'])

        """
        изоляция логов для текущего процесса
        чтобы логи этого файла не смешались с другими, они будут копиться в памяти
        """
        list_handler = ListLogHandler()
        list_handler.setLevel(self._settings.log_level.upper())

        worker_logger = logging.getLogger("parallel_worker")

        # перехватчик
        worker_logger.addHandler(list_handler)

        raw_file = job.raw_observation.absolute_path_filename

        # обработка
        fits_base_dir = self._settings.fits_archive
        try:
            worker_logger.info(f"=== Starting processing for [{raw_file.name}] ===")

            director = FastAcquisition1To3GHzObservationProcessingDirector()
            wrapper = FastAcquisition1To3GHzProcessingWrapper(director)

            result = wrapper.process(raw_file, fits_base_dir, overwrite=True)
        finally:
            # важно: открепить хэндлер, чтобы не было утечки памяти
            worker_logger.removeHandler(list_handler)

        # сброс логов в общий поток
        if list_handler:
            for record in list_handler.records:
                logger.handle(record)

        # обновление записи в БД
        job.time_taken_sec = result.time_taken_sec
        job.peak_memory_mb = result.peak_memory_mb

        if result.status == ProcessingStatus.SUCCESS:
            job.status = ProcessingJobStatus.SUCCESS.value
            job.comment = None
            logger.info(
                f"[{raw_file.name}] {job.status}. Time: {result.time_taken_sec:.1f}s | Peak RAM: {result.peak_memory_mb:.1f} MB")
        else:
            job.status = ProcessingJobStatus.FAILED.value
            job.comment = result.error_message
            logger.error(f"[{raw_file.name}] {job.status}: {result.error_message}")

        job.save(update_fields=['status', 'comment', 'time_taken_sec', 'peak_memory_mb', 'updated_at'])

        return result.status == ProcessingJobStatus.SUCCESS