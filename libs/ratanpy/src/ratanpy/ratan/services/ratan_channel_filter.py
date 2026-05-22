from abc import ABC, abstractmethod

from ratanpy.ratan.ratan_observation import RatanObservation


class RatanChannelFilter(ABC):

    @abstractmethod
    def filter_channels(self, obs: RatanObservation) -> RatanObservation:
        pass