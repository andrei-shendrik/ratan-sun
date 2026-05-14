from abc import ABC, abstractmethod
from pathlib import Path

from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation


class RatanObservationWriter(ABC):

    @abstractmethod
    def write(self, observation: RatanObservation):
        pass

    @staticmethod
    @abstractmethod
    def supports(data_receiver: DataReceiver, file_type: str) -> bool:
        pass