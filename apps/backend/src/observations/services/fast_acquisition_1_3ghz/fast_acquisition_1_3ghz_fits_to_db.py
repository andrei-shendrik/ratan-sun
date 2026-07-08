import logging

from django.db import transaction
from ratanpy.physics.fits_reader import FitsHeaderReader

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.models import ProcessingJobBin2FitsFastAcquisition1To3GHz, FitsObservationFastAcquisition1To3GHz

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzFitsToDB:
    def __init__(self, settings: FastAcquisition1To3GHzSettings):
        self.settings = settings

    def execute(self, job_id: str) -> bool:
        job = ProcessingJobBin2FitsFastAcquisition1To3GHz.objects.select_related('raw_observation').get(id=job_id)
        raw = job.raw_observation

        # Получаем пути (заглушка, используй свою логику)
        fits_filename = raw.filename.replace('.bin.gz', '.fits').replace('.bin', '.fits').lower()
        fits_path = self.settings.fits_archive / "2026" / "05" / fits_filename

        if not fits_path.exists():
            logger.error(f"FITS file not found for metadata extraction: {fits_path}")
            return False

        try:
            # Читаем заголовки без загрузки тяжелой даты в оперативную память
            # todo
            headers = FitsHeaderReader.read_headers(fits_path)

            with transaction.atomic():
                # Обновляем или создаем запись в БД
                FitsObservationFastAcquisition1To3GHz.objects.update_or_create(
                    raw_observation=raw,
                    defaults={
                        'fits_path_filename': str(fits_path),
                        'fits_filename': fits_filename,
                        'datetime_culmination_feed_horn_utc': headers.get('datetime_culmination_feed_horn_utc'),
                        'datetime_culmination_efrat_utc': headers.get('datetime_culmination_efrat_utc'),
                        # ... пробрасываем все 40 полей ...
                        'data_values': headers.get('data_values'),
                        'pol_ch0': headers.get('pol_ch0'),
                        'num_samples': headers.get('num_samples'),
                        'num_frequencies': headers.get('num_frequencies')
                    }
                )
            logger.info(f"[{fits_filename}] Metadata successfully saved to DB")
            return True

        except Exception as e:
            logger.error(f"[{fits_filename}] Metadata extraction failed: {e}", exc_info=True)
            return False