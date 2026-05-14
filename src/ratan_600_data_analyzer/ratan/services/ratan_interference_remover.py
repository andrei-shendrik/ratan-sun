from abc import abstractmethod, ABC

from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanInterferenceRemover(ABC):

    @abstractmethod
    def process(self, observation: RatanObservation):
        pass