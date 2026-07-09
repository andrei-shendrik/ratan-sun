import logging

from celery import shared_task

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.enums import ProcessingJobStatus
from observations.models import ProcessingJobBin2FitsFastAcquisition1To3GHz
from observations.services.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_bin2fits_converter import FastAcquisition1To3GHzBin2FitsConverter
from observations.services.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_bin2fits_scheduler import \
    FastAcquisition1To3GHzJobScheduler
from observations.services.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_fits_to_db import \
    FastAcquisition1To3GHzFitsToDB
from observations.services.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_raw_to_db import \
    FastAcquisition1To3GHzRawToDB

logger = logging.getLogger(__name__)

@shared_task
def beat_fast_acq_1_3ghz_raw_to_db():
    """ поиск новых сырых файлов Fast Acq 1-3 GHz и добавление их в БД """
    # загрузка кэшированных настроек
    settings = FastAcquisition1To3GHzSettings.load()
    raw_to_db = FastAcquisition1To3GHzRawToDB(settings)
    added_count = raw_to_db.execute()
    if added_count > 0:
        task_fast_acq_1_3ghz_schedule_bin2fits_jobs.delay()

@shared_task
def task_fast_acq_1_3ghz_schedule_bin2fits_jobs():
    """ создание задач bin2fits в БД только для новых файлов """
    settings = FastAcquisition1To3GHzSettings.load()
    scheduler = FastAcquisition1To3GHzJobScheduler(settings)

    created_count = scheduler.execute()

    # если задачи были созданы, оповещение об этом диспетчера, чтобы он отправил их в redis и раздал на обработку воркерам
    if created_count > 0:
        task_fast_acq_1_3ghz_dispatch_bin2fits_jobs.delay()

@shared_task
def task_fast_acq_1_3ghz_dispatch_bin2fits_jobs():
    """ поиск абсолютно всех задач bin2fits со статусом UNPROCESSED и постановка их в очередь redis """

    jobs = ProcessingJobBin2FitsFastAcquisition1To3GHz.objects.filter(
        status=ProcessingJobStatus.UNPROCESSED.value
    )[:100] # отправка пачками по 100

    for job in jobs:
        task_fast_acq_1_3ghz_bin2fits.delay(str(job.id))

@shared_task(bind=True, max_retries=10)
def task_fast_acq_1_3ghz_bin2fits(self, job_id: str):
    """ конвертирование bin2fits """
    settings = FastAcquisition1To3GHzSettings.load()
    converter = FastAcquisition1To3GHzBin2FitsConverter(settings)

    try:
        is_success = converter.execute(job_id)

        if is_success:
            task_fast_acq_1_3ghz_fits_to_db.delay(job_id)
    except MemoryError:
        """
        если свободной памяти недостаточно, возврат задачи в очередь на 60 секунд.
        статус в БД остался неизменным (UNPROCESSED)
        """
        raise self.retry(countdown=60)

@shared_task
def task_fast_acq_1_3ghz_fits_to_db(job_id: str):
    """ добавление fits наблюдения в БД """
    settings = FastAcquisition1To3GHzSettings.load()
    fits_to_db = FastAcquisition1To3GHzFitsToDB(settings)

    is_success = fits_to_db.execute(job_id)
#     if is_success:
#         task_fast_acq_1_3ghz_create_visualization_data.delay(job_id)
#
# @shared_task(bind=True, max_retries=5)
# def task_fast_acq_1_3ghz_create_visualization_data(self, job_id: str):
#     """ создание JSON и thumbnails """
#     settings = FastAcquisition1To3GHzSettings.load()
#     service = VisualizationService(settings)
#
#     try:
#         service.execute(job_id)
#     except MemoryError:
#         raise self.retry(countdown=60)