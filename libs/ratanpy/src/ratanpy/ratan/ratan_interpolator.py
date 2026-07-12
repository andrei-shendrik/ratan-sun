from abc import ABC, abstractmethod

from ratanpy.ratan.ratan_observation import RatanObservation


class RatanInterpolator(ABC):

    @abstractmethod
    def process(self, observation: RatanObservation):
        pass