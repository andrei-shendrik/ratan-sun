from abc import abstractmethod

from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratanpy.ratan.services.ratan_channel_filter import RatanChannelFilter


class FastAcquisition1To3GHzChannelFilter(RatanChannelFilter):

    @abstractmethod
    def filter_channels(self, obs: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:
        pass