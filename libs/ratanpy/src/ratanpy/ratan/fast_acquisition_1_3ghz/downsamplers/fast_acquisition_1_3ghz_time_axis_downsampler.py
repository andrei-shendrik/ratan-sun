import logging
import warnings

import numpy as np

from ratanpy.ratan.fast_acquisition_1_3ghz.downsamplers.fast_acquisition_1_3ghz_downsampler import \
    FastAcquisition1To3GHzDownsampler
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata import FastAcquisition1To3GHzMetadata
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation


logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzTimeAxisDownsampler(FastAcquisition1To3GHzDownsampler):
    """

    """

    def __init__(self, target_samples: int = 1000):
        self._target_samples = target_samples

    def process(self, observation: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:

        observation.data.pol_channel0 = self._downsample_matrix(observation.data.pol_channel0)
        observation.data.pol_channel1 = self._downsample_matrix(observation.data.pol_channel1)

        observation.metadata.coordinate_axes.time_axis = self._downsample_axis(
            observation.metadata.coordinate_axes.time_axis)
        observation.metadata.coordinate_axes.arcsec_axis = self._downsample_axis(
            observation.metadata.coordinate_axes.arcsec_axis)

        self._update_metadata(observation.metadata)

        return observation

    def _downsample_matrix(self, data_matrix: np.ndarray) -> np.ndarray:
        """
        сжимает матрицу [N_freqs, N_times] по оси времени
        """
        num_freqs, current_samples = data_matrix.shape

        if current_samples <= self._target_samples:
            logger.warning("Current samples less than target. Skipping downsampling")
            return data_matrix

        # factor
        # размер блока для усреднения
        block_size = current_samples // self._target_samples

        # обрезка массива чтобы он делился нацело на размер блока
        usable_len = self._target_samples * block_size
        trimmed_data = data_matrix[:, :usable_len]

        # изменение формы массива
        reshaped = trimmed_data.reshape(num_freqs, self._target_samples, block_size)

        # усреднение по последней оси (внутри каждого блока)
        # nanmean: если в блоке есть NaN, он их проигнорирует. Если весь блок состоит из NaN, результат будет NaN

        # чтобы не было предупреждений
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Mean of empty slice")
            downsampled = np.nanmean(reshaped, axis=2)

        return downsampled

    def _downsample_axis(self, axis: np.ndarray) -> np.ndarray:
        """
        сжимает ось координат
        """

        current_samples = len(axis)
        # factor
        block_size = current_samples // self._target_samples
        usable_len = self._target_samples * block_size

        reshaped = axis[:usable_len].reshape(self._target_samples, block_size)
        return np.nanmean(reshaped, axis=1)

    def _update_metadata(self, metadata: FastAcquisition1To3GHzMetadata):

        if metadata.num_samples <= self._target_samples:
            return

        # размер блока
        block_size = metadata.num_samples // self._target_samples

        metadata.time_reduction_factor = metadata.time_reduction_factor * block_size

        if metadata.ref_sample is not None:
            metadata.ref_sample = int(metadata.ref_sample / block_size)
        if metadata.start_pulse_edge_sample is not None:
            metadata.start_pulse_edge_sample = int(metadata.start_pulse_edge_sample / block_size)
        if metadata.stop_pulse_edge_sample is not None:
            metadata.stop_pulse_edge_sample = int(metadata.stop_pulse_edge_sample / block_size)

        if metadata.samples_per_second is not None:
            metadata.samples_per_second = metadata.samples_per_second / block_size

        if metadata.arcsec_per_sample is not None:
            metadata.arcsec_per_sample = metadata.arcsec_per_sample * block_size
        if metadata.time_resolution is not None:
            metadata.time_resolution = metadata.time_resolution * block_size

        """
        num_samples % target_samples
        отрезали кусочек от оригинальной записи (время окончания),
        длина записи стала чуть короче
        начало записи не изменилось
        """
        usable_samples = self._target_samples * block_size

        if metadata.record_duration_seconds is not None and metadata.samples_per_second is not None:
            metadata.record_duration_seconds = self._target_samples / metadata.samples_per_second

            if metadata.datetime_reg_stop_utc and metadata.datetime_reg_start_utc:
                from datetime import timedelta
                metadata.datetime_reg_stop_utc = metadata.datetime_reg_start_utc + timedelta(
                    seconds=metadata.record_duration_seconds)
                metadata.datetime_reg_stop_local = metadata.datetime_reg_start_local + timedelta(
                    seconds=metadata.record_duration_seconds)

        metadata.num_samples = self._target_samples


    # def time_downsample(self, time_reduction_factor: int) -> FastAcquisition1To3GHzBuilder:
    #
    #     pol_chan_data = self._observation.data.pol_channels_data
    #     joined_channels_0 = np.hstack((np.fliplr(pol_chan_data.c0p0_data), pol_chan_data.c1p0_data)).T  # 1-3 GHz pol0
    #     joined_channels_1 = np.hstack((np.fliplr(pol_chan_data.c0p1_data), pol_chan_data.c1p1_data)).T  # 1-3 GHz pol1
    #
    #     pol0_data = self._trim_polarization_array(joined_channels_0, time_reduction_factor = time_reduction_factor)
    #     pol1_data = self._trim_polarization_array(joined_channels_1, time_reduction_factor = time_reduction_factor)
    #
    #     array_3d = np.stack([pol0_data, pol1_data], axis=1)
    #
    #     fast_acq_data = FastAcquisition1To3GHzData()
    #     fast_acq_data.pol_channels_data = pol_chan_data
    #     fast_acq_data.kurtosis_data = self._data.kurtosis_data
    #     fast_acq_data.gen_state_data = self._data.gen_state_data
    #     fast_acq_data.array_3d = array_3d
    #
    #     bin_file = self._metadata.bin_file
    #     fast_acq_metadata = FastAcquisition1To3GHzMetadataBinLoader.load(bin_file, fast_acq_data)
    #
    #     self._metadata = fast_acq_metadata
    #     self._data = fast_acq_data
    #     return self

    # @staticmethod
    # def _trim_polarization_array(pol_array: np.ndarray, time_reduction_factor: int) -> np.ndarray:
    #     # Приводит массив к размеру, кратному self.time_reduction_factor, усредняет его по времени и заменяет
    #     # возможные nan интерполированными значениями
    #
    #     n_bands, n_points = np.shape(pol_array)
    #     pol_array = pol_array[:, :(n_points // time_reduction_factor) * time_reduction_factor]
    #     try:
    #         pol_array = pol_array.reshape(n_bands, n_points // time_reduction_factor, -1)
    #         with warnings.catch_warnings():
    #             warnings.filterwarnings(action='ignore', message='Mean of empty slice')
    #             pol_array = np.nanmean(pol_array, axis=2)
    #         pol_array = fast_input.replace_nan(pol_array)
    #     except ValueError:
    #         pol_array = None
    #     return pol_array