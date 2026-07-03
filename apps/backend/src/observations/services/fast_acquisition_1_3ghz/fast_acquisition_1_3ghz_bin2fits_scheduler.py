import logging

from dateutil.relativedelta import relativedelta

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from datetime import datetime, timezone

from observations.enums import ProcessingJobStatus
from observations.models import RawObservationFastAcquisition1To3GHz, ProcessingJobBin2FitsFastAcquisition1To3GHz

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzJobScheduler:
    """
    сканирует БД на наличие новых сырых файлов комплекса Fast Acquisition 1-3 GHz без задач конвертации и ставит их в очередь
    """
    def __init__(self, settings: FastAcquisition1To3GHzSettings):
        self._settings = settings

    def execute(self) -> int:
        cutoff_date = datetime.now(timezone.utc) - relativedelta(days=self._settings.monitoring_days)

        # поиск файлов, у которых нет связанного processing_bin2fits_job и которые новее cutoff_date
        orphaned_raw_records = RawObservationFastAcquisition1To3GHz.objects.filter(
            datetime_obs_utc__gte=cutoff_date,
            job_bin2fits__isnull=True
        )

        raw_list = list(orphaned_raw_records)
        if not raw_list:
            return 0

        jobs_to_create = []
        for raw in raw_list:
            jobs_to_create.append(
                ProcessingJobBin2FitsFastAcquisition1To3GHz(
                    raw_observation=raw,
                    status=ProcessingJobStatus.UNPROCESSED.value
                )
            )
            logger.info(f"Created processing bin2fits job for '{raw.filename}'")

        ProcessingJobBin2FitsFastAcquisition1To3GHz.objects.bulk_create(jobs_to_create, ignore_conflicts=True)

        created_count = len(jobs_to_create)
        # logger.info(f"Scheduled {created_count} new processing bin2fits jobs for Fast Acquisition 1-3 GHz")

        return created_count