import logging
import warnings

import numpy as np

from ratanpy.ratan.fast_acquisition_1_3ghz.downsamplers.fast_acquisition_1_3ghz_downsampler import \
    FastAcquisition1To3GHzDownsampler
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_metadata import FastAcquisition1To3GHzMetadata
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation


logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzFrequencyAxisDownsampler(FastAcquisition1To3GHzDownsampler):
    """
    """

    def __init__(self, target_frequencies: int, validity_threshold: float = 0.3):
        """
        :param target_frequencies:
        :param validity_threshold: доля непустых каналов в блоке (0.3 = 30%)
        Если в усредняемом блоке доля каналов (не NaN) меньше этого порога,
        итоговый канал тоже станет NaN
        """
        self._target_frequencies = target_frequencies
        self._threshold = validity_threshold

    # todo обновить верхнюю частоту из-за обрезки длины массива частот (деление нацело)
    def process(self, observation: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:

        observation.data.pol_channel0 = self._downsample_matrix(observation.data.pol_channel0)
        observation.data.pol_channel1 = self._downsample_matrix(observation.data.pol_channel1)

        observation.metadata.coordinate_axes.frequency_axis = self._downsample_axis(
            observation.metadata.coordinate_axes.frequency_axis)

        self._update_metadata(observation.metadata)

        return observation

    def _downsample_matrix(self, data_matrix: np.ndarray) -> np.ndarray:
        """
        Сжимает матрицу [N_freqs, N_times] по оси частот
        """
        num_frequencies, num_samples = data_matrix.shape

        if num_frequencies <= self._target_frequencies:
            logger.warning(f"Current frequencies ('{num_frequencies}') less than target ('{self._target_frequencies}'). Skipping downsampling")
            return data_matrix

        block_size = num_frequencies // self._target_frequencies
        usable_len = self._target_frequencies * block_size

        # обрезка каналов сверху спектра (чтобы делилось нацело)
        trimmed_data = data_matrix[:usable_len, :]

        reshaped = trimmed_data.reshape(self._target_frequencies, block_size, num_samples)

        # подсчет NaN в каждом блоке (для каждой точки времени)
        nan_counts = np.isnan(reshaped).sum(axis=1)

        # доля не-NaN
        not_nan_ratio = (block_size - nan_counts) / block_size

        # усреднение игнорируя NaN
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Mean of empty slice")
            downsampled = np.nanmean(reshaped, axis=1)

        # проверка порога валидности.
        downsampled[not_nan_ratio < self._threshold] = np.nan

        return downsampled

    def _downsample_axis(self, axis: np.ndarray) -> np.ndarray:
        """
        Сжимает ось координат
        """

        current_frequencies = len(axis)
        # factor
        block_size = current_frequencies // self._target_frequencies
        usable_len = self._target_frequencies * block_size

        reshaped = axis[:usable_len].reshape(self._target_frequencies, block_size)
        return np.nanmean(reshaped, axis=1)

    def _update_metadata(self, metadata: FastAcquisition1To3GHzMetadata):
        if metadata.num_frequencies <= self._target_frequencies:
            return

        block_size = metadata.num_frequencies // self._target_frequencies

        metadata.num_frequencies = self._target_frequencies

        if metadata.frequency_resolution is not None:
            metadata.frequency_resolution = metadata.frequency_resolution * block_size