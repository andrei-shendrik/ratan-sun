from abc import ABC

from ratan_600_data_analyzer.ratan.fast_acquisition_1_3ghz.channel_filters.fast_acquisition_1_3ghz_channel_filter import \
    FastAcquisition1To3GHzChannelFilter
from ratan_600_data_analyzer.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation


class FastAcquisition1To3GHzBandFilter(FastAcquisition1To3GHzChannelFilter):

    def __init__(self, filter_bands: tuple):
        self._filter_bands = filter_bands

    def filter_channels(self, observation: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:
        frequency_axis = observation.metadata.coordinate_axes.frequency_axis
        pol0_data = observation.data.pol_channel0
        pol1_data = observation.data.pol_channel1
        for el in self._filter_bands:
            idx = (frequency_axis >= el[0]) & (frequency_axis <= el[1])
            pol0_data[idx] = 0
            pol1_data[idx] = 0
        return observation