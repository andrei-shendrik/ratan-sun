import logging

from django.db import transaction

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.models import ProcessingJobBin2FitsFastAcquisition1To3GHz, FitsObservationFastAcquisition1To3GHz
from ratanpy.ratan.fast_acquisition_1_3ghz.readers.fast_acquisition_1_3ghz_fits_reader import \
    FastAcquisition1To3GHzFitsReader

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzFitsToDB:
    def __init__(self, settings: FastAcquisition1To3GHzSettings):
        self._settings = settings

    def execute(self, job_id: str) -> bool:
        try:
            job = ProcessingJobBin2FitsFastAcquisition1To3GHz.objects.select_related('raw_observation').get(id=job_id)
        except ProcessingJobBin2FitsFastAcquisition1To3GHz.DoesNotExist:
            logger.error(f"Job {job_id} not found in DB.")
            return False
        raw = job.raw_observation

        fits_base_dir = self._settings.fits_archive
        relative_path = raw.relative_path
        fits_filename = raw.filename.replace('.bin.gz', '.fits').replace('.bin', '.fits').lower()

        fits_file = fits_base_dir / relative_path / fits_filename

        if not fits_file.exists():
            logger.error(f"FITS file not found: '{fits_file}'")
            return False

        reader = FastAcquisition1To3GHzFitsReader()
        try:
            metadata = reader.read_metadata(fits_file)
        except Exception as e:
            logger.error(f"Failed to read metadata from '{fits_filename}': {e}", exc_info=True)
            return False

        try:
            with transaction.atomic():
                FitsObservationFastAcquisition1To3GHz.objects.update_or_create(
                    raw_observation=raw,
                    defaults={
                        # поля abstract observation
                        'relative_path': relative_path,
                        'filename': fits_filename,

                        # поля abstract ratan observation
                        'obs_mode': metadata.observation_mode.value if metadata.observation_mode else None, # observation_mode взять из моделей!
                        'object_of_observation': metadata.object_of_observation,
                        'azimuth': metadata.azimuth,

                        'obs_start_utc': metadata.datetime_reg_start_utc,
                        'datetime_obs_utc': metadata.datetime, # добавить в мета datetime_obs_utc
                        'obs_stop_utc': metadata.datetime_reg_stop_utc,
                        'datetime_culmination_efrat_utc': metadata.datetime_culmination_efrat_utc,
                        'datetime_culmination_feed_horn_utc': metadata.datetime_culmination_feed_horn_utc,

                        'altitude': metadata.altitude,
                        'declination': metadata.declination,
                        'right_ascension': metadata.right_ascension,
                        'solar_r': metadata.solar_r.value if hasattr(metadata.solar_r, 'value') else metadata.solar_r,
                        'solar_p': metadata.solar_p.value if hasattr(metadata.solar_p, 'value') else metadata.solar_p,
                        'solar_b': metadata.solar_b.value if hasattr(metadata.solar_b, 'value') else metadata.solar_b,
                        'scan_angle': metadata.scan_angle if hasattr(metadata.scan_angle, 'value') else metadata.scan_angle,

                        # каналы
                        'data_values': metadata.data_values.value if metadata.data_values else None,
                        'pol_chan0': metadata.pol_ch0.value if metadata.pol_ch0 else None,
                        'pol_chan1': metadata.pol_ch1.value if metadata.pol_ch1 else None,

                        'num_samples': metadata.num_samples,
                        'num_frequencies': metadata.num_frequencies,
                        'ref_time': metadata.ref_time,
                        'ref_sample': metadata.ref_sample,


                        'is_bad': metadata.is_bad,
                        'is_calibrated': metadata.is_calibrated,
                    }
                )

            logger.info(f"[{fits_filename}] Metadata successfully saved to DB")
            return True

        except Exception as e:
            logger.error(f"Database error while saving metadata for '{fits_filename}': {e}", exc_info=True)
            return False