import logging
import zoneinfo
from datetime import datetime, timezone

import numpy as np
from astropy.coordinates import Angle
from astropy.io import fits
import astropy.units as u
from astropy.units import Quantity

from ratanpy.ratan.channel_mapper import ChannelMapper
from ratanpy.ratan.coordinate_axes import CoordinateAxes
from ratanpy.ratan.data_receiver import DataReceiver
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata import FastAcquisition1To3GHzMetadata
from ratanpy.ratan.polarization_type import PolarizationType
from ratanpy.ratan.services.ratan_metadata_loader import RatanMetadataLoader


logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzMetadataFitsLoader(RatanMetadataLoader):

    # местное время обсерватории
    LOCAL_TZ = zoneinfo.ZoneInfo("Europe/Moscow")

    @classmethod
    def _parse_iso_datetime(cls, dt_str: str) -> datetime | None:
        """ Парсинг ISO формата: 2026-06-18T09:14:47.190000+00:00 """
        if not dt_str: return None
        try:
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError as e:
            logger.warning(f"Failed to parse ISO datetime '{dt_str}': {e}")
            return None

    @classmethod
    def _parse_date_time_obs(cls, date_str: str, time_str: str) -> tuple[datetime | None, datetime | None]:
        """ склеивает DATE-OBS и TIME-OBS (местное время) и возвращает кортеж [datetime_obs_local, datetime_obs_utc] """
        if not date_str or not time_str:
            return None, None

        try:
            naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            datetime_obs_local = naive_dt.replace(tzinfo=cls.LOCAL_TZ)

            datetime_obs_utc = datetime_obs_local.astimezone(timezone.utc)

            return datetime_obs_local, datetime_obs_utc

        except ValueError as e:
            logger.warning(f"Failed to parse DATE-OBS/TIME-OBS '{date_str} {time_str}': {e}")
            return None, None

    @classmethod
    def _get_bool(cls, header: fits.Header, key: str, default: bool = False) -> bool:
        """ Fits boolean True/False 'T'/'F' """
        val = header.get(key)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().upper() == 'T'
        return default

    @classmethod
    def load(cls, header: fits.Header) -> FastAcquisition1To3GHzMetadata: # (header: fits.Header, table_hdu: fits.BinTableHDU)

        metadata = FastAcquisition1To3GHzMetadata()

        metadata.telescope = header.get('TELESCOP')
        metadata.data_receiver = DataReceiver.from_string(header.get('RECEIVER'))
        metadata.observation_mode = DataReceiver.from_string(header.get('OBS-MODE'))

        metadata.object_of_observation = header.get('OBJECT')
        metadata.azimuth = header.get('AZIMUTH')

        metadata.altitude = Angle(header.get('ALTITUDE'), unit=u.deg)
        metadata.right_ascension = Angle(header.get('SOL_RA'), unit=u.deg)
        metadata.declination = Angle(header.get('SOL_DEC'), unit=u.deg)

        metadata.scan_angle = Angle(header.get('SCAN_ANG'), unit=u.deg)

        metadata.solar_r = Angle(header.get('SOLAR_R'), unit=u.arcsec)
        metadata.solar_p = Angle(header.get('SOLAR_P'), unit=u.deg)
        metadata.solar_b = Angle(header.get('SOLAR_B'), unit=u.deg)

        metadata.feed_offset = header.get('FEED_OFF')
        metadata.feed_offset_time = header.get('FE_OFF_T').total_seconds()

        metadata.arcsec_per_sample = header.get('ARCPSAM')
        metadata.arcsec_per_second = Quantity(header.get('ARCPSEC'), unit=u.arcsec / u.s)

        metadata.num_samples = header.get('NSAMPLES')
        metadata.num_frequencies = header.get('NFREQS')

        metadata.ref_time = header.get('REF_TIME')
        metadata.ref_sample = header.get('REF_SAMP')

        metadata.time_resolution = header.get('DTIME')
        metadata.switch_polarization_time = header.get('DACTIME')
        metadata.frequency_resolution = header.get('DFREQ')

        metadata.polarization_channel0 = PolarizationType.from_string(header.get('POL_CH0'))
        metadata.polarization_channel1 = PolarizationType.from_string(header.get('POL_CH1'))

        metadata.half_width_kurtosis_interval = header.get('KURTOSIS')
        metadata.attenuator_common = header.get('ATT1')
        metadata.attenuator_1_2ghz = header.get('ATT2')
        metadata.attenuator_2_3ghz = header.get('ATT3')

        metadata.is_calibrated = cls._get_bool(header, 'CALIBR')
        metadata.quiet_sun_point_arcsec = header.get('QSP')
        metadata.unit = header.get('UNIT')
        metadata.clean = cls._get_bool(header, 'CLEAN')

        metadata.channel_mapping = ChannelMapper.get_channel_mapping(
            metadata.polarization_channel0,
            metadata.polarization_channel1
        )

        metadata.datetime_obs_local, metadata.datetime_obs_utc = cls._parse_date_time_obs(header.get('DATE-OBS'), header.get('TIME-OBS'))

        metadata.datetime_reg_start_utc = cls._parse_iso_datetime(header.get('T_START'))
        if metadata.datetime_reg_start_utc is not None:
            metadata.datetime_reg_start_local = metadata.datetime_reg_start_utc.astimezone(cls.LOCAL_TZ)

        metadata.datetime_culmination_efrat_utc = cls._parse_iso_datetime(header.get('CULM_EFR'))
        if metadata.datetime_culmination_efrat_utc is not None:
            metadata.datetime_culmination_efrat_local = metadata.datetime_culmination_efrat_utc.astimezone(cls.LOCAL_TZ)

        metadata.datetime_culmination_feed_horn_utc = cls._parse_iso_datetime(header.get('CULM_FEE'))
        if metadata.datetime_culmination_feed_horn_utc is not None:
            metadata.datetime_culmination_feed_horn_local = metadata.datetime_culmination_feed_horn_utc.astimezone(cls.LOCAL_TZ)

        metadata.datetime_reg_stop_utc = cls._parse_iso_datetime(header.get('T_STOP'))
        if metadata.datetime_reg_stop_utc is not None:
            metadata.datetime_reg_stop_local = metadata.datetime_reg_stop_utc.astimezone(cls.LOCAL_TZ)

        metadata.freq_min_mhz = header.get('FREQ_MIN')
        metadata.freq_max_mhz = header.get('FREQ_MAX')

        metadata.samples_per_second = header.get('SAMPSEC')

        metadata.record_duration_seconds = header.get('REC_DUR')

        metadata.record_duration_seconds = header.get('ARCS_RES')
        metadata.record_duration_seconds = header.get('DOWNSAMP')

        # todo создание вместо чтения
        # try:
        #     freq_axis = table_hdu.columns['freq'].array
        # except KeyError as e:
        #     logger.error(f"Missing column in FITS table: {e}")
        #     raise ValueError(f"Invalid FITS table format: {e}")

        frequency_axis = np.linspace(
            metadata.freq_min_mhz / 1000,
            metadata.freq_max_mhz / 1000,
            num=metadata.num_frequencies,
            dtype=np.float64
        )
        polarization_axis = [PolarizationType.LHCP, PolarizationType.RHCP]

        metadata.frequencies = frequency_axis
        metadata.polarizations = polarization_axis

        time_axis = np.arange(metadata.num_samples) / metadata.samples_per_second
        arcsec_axis = - (time_axis - metadata.ref_time) * metadata.arcsec_per_second

        coordinate_axes = CoordinateAxes()
        coordinate_axes.frequency_axis = frequency_axis
        coordinate_axes.time_axis = time_axis
        coordinate_axes.arcsec_axis = arcsec_axis
        metadata.coordinate_axes = coordinate_axes

        return metadata