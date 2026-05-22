from abc import abstractmethod, ABC

from ratanpy.ratan.ratan_observation import RatanObservation


class RatanInterferenceRemover(ABC):

    @abstractmethod
    def process(self, observation: RatanObservation):
        pass