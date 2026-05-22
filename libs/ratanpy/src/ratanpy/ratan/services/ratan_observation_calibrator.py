from abc import ABC, abstractmethod

from ratanpy.ratan.ratan_observation import RatanObservation


class RatanObservationCalibrator(ABC):

    @abstractmethod
    def calibrate(self, observation: RatanObservation):
        pass