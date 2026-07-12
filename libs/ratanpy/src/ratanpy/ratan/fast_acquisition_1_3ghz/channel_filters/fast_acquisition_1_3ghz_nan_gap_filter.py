import numpy as np

from ratanpy.ratan.fast_acquisition_1_3ghz.channel_filters.fast_acquisition_1_3ghz_channel_filter import \
    FastAcquisition1To3GHzChannelFilter
from ratanpy.ratan.fast_acquisition_1_3ghz.config.fast_acquisition_1_3ghz_configuration import \
    FastAcquisition1To3GHzConfiguration
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation


class FastAcquisition1To3GHzNaNGapFilter(FastAcquisition1To3GHzChannelFilter):

    def __init__(self, config: FastAcquisition1To3GHzConfiguration, max_gap_length: int = 200):
        """
            :param max_gap_length: Максимально допустимое количество NaN подряд.
            Если больше - весь канал обнуляется (NaN)
        """
        self._max_gap_length = max_gap_length
        self._config = config
        self._missing_value_replacement = None

    def filter_channels(self, observation: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:

        if observation.metadata.is_calibrated:
            self._missing_value_replacement = self._config.calibr_missing_value_replacement
        else:
            self._missing_value_replacement = self._config.raw_missing_value_replacement
        self.process_matrix(observation.data.pol_channel0)
        self.process_matrix(observation.data.pol_channel1)

        return observation

    def process_matrix(self, data_matrix: np.ndarray) -> np.ndarray:
        gap_mask = np.isnan(data_matrix) | (data_matrix < 0)

        if not np.any(gap_mask):
            return data_matrix

        # False по краям для корректной работы np.diff
        padded = np.pad(gap_mask, pad_width=((0, 0), (1, 1)), mode='constant', constant_values=False)
        diffs = np.diff(padded.astype(int), axis=1)

        # diffs == 1 (начало пустоты), diffs == -1 (конец пустоты)
        starts_y, starts_x = np.where(diffs == 1)
        ends_y, ends_x = np.where(diffs == -1)

        # длины всех пустот
        gap_lengths = ends_x - starts_x

        # индексы пустот, которые больше лимита
        bad_gaps_mask = gap_lengths > self._max_gap_length

        # каналы, которым принадлежат пустоты
        bad_channels = np.unique(starts_y[bad_gaps_mask])

        # заполнение отрицательными значениями только для плохих каналов
        if len(bad_channels) > 0:
            data_matrix[bad_channels, :] = self._missing_value_replacement

        return data_matrix