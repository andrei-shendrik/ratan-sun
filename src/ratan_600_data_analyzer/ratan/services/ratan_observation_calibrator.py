from abc import ABC, abstractmethod

from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanObservationCalibrator(ABC):

    @abstractmethod
    def calibrate(self, observation: RatanObservation):
        pass