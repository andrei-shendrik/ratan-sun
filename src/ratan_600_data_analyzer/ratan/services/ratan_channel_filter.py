from abc import ABC, abstractmethod

from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanChannelFilter(ABC):

    @abstractmethod
    def filter_channels(self, obs: RatanObservation) -> RatanObservation:
        pass