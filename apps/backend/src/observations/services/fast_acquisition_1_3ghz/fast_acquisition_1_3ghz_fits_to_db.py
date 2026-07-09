import logging

from django.db import transaction

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.enums import ObservationMode, DataValues, PolarizationType
from observations.models import ProcessingJobBin2FitsFastAcquisition1To3GHz, FitsObservationFastAcquisition1To3GHz
from observations.utils.enum_mapper import EnumMapper
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
                        'object_of_observation': metadata.object_of_observation,
                        'azimuth': metadata.azimuth,
                        'obs_start_utc': metadata.datetime_reg_start_utc,
                        'datetime_obs_utc': metadata.datetime_obs_utc,
                        'obs_stop_utc': metadata.datetime_reg_stop_utc,

                        # поля fits fast acquisition 1-3ghz
                        'datetime_culmination_efrat_utc': metadata.datetime_culmination_efrat_utc,
                        'datetime_culmination_feed_horn_utc': metadata.datetime_culmination_feed_horn_utc,

                        'obs_mode': EnumMapper.map_enum_to_db_choices(metadata.observation_mode, ObservationMode),

                        'altitude': metadata.altitude.value if hasattr(metadata.altitude, 'value') else metadata.altitude,
                        'declination': metadata.declination.value if hasattr(metadata.declination, 'value') else metadata.declination,
                        'right_ascension': metadata.right_ascension.value if hasattr(metadata.right_ascension, 'value') else metadata.right_ascension,
                        'solar_r': metadata.solar_r.value if hasattr(metadata.solar_r, 'value') else metadata.solar_r,
                        'solar_p': metadata.solar_p.value if hasattr(metadata.solar_p, 'value') else metadata.solar_p,
                        'solar_b': metadata.solar_b.value if hasattr(metadata.solar_b, 'value') else metadata.solar_b,
                        'scan_angle': metadata.scan_angle.value if hasattr(metadata.scan_angle, 'value') else metadata.scan_angle,

                        # каналы
                        'data_values': EnumMapper.map_enum_to_db_choices(metadata.data_values, DataValues),
                        'pol_chan0': EnumMapper.map_enum_to_db_choices(metadata.polarization_channel0, PolarizationType),
                        'pol_chan1': EnumMapper.map_enum_to_db_choices(metadata.polarization_channel1, PolarizationType),

                        'num_samples': metadata.num_samples,
                        'num_frequencies': metadata.num_frequencies,
                        'ref_time': metadata.ref_time,
                        'ref_sample': metadata.ref_sample,

                        'samples_per_second': metadata.samples_per_second,
                        'arcsec_per_sample': metadata.arcsec_per_sample,
                        'arcsec_per_second': metadata.arcsec_per_second.value if hasattr(metadata.arcsec_per_second, 'value') else metadata.arcsec_per_second,

                        'record_duration_seconds': metadata.record_duration_seconds,
                        'time_reduction_factor': metadata.time_reduction_factor,
                        'frequency_resolution': metadata.frequency_resolution,
                        'time_resolution': metadata.time_resolution,
                        'arcsec_resolution': metadata.arcsec_resolution,
                        'switch_polarization_time': metadata.switch_polarization_time,

                        'feed_horn_offset': metadata.feedhorn_offset,
                        'feed_horn_offset_time': metadata.feedhorn_offset_time,

                        'attenuator_common': metadata.attenuator_common,
                        'attenuator_1_2ghz': metadata.attenuator_1_2ghz,
                        'attenuator_2_3ghz': metadata.attenuator_2_3ghz,

                        'half_width_kurtosis_interval': metadata.half_width_kurtosis_interval,

                        'is_bad': metadata.is_bad,
                        'is_calibrated': metadata.is_calibrated,

                        'unit': metadata.unit,
                        'quiet_sun_point_arcsec': metadata.quiet_sun_point_arcsec,
                    }
                )

            logger.info(f"[{fits_filename}] Metadata successfully saved to DB")
            return True

        except Exception as e:
            logger.error(f"Database error while saving metadata for '{fits_filename}': {e}", exc_info=True)
            return False