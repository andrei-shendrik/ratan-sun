from abc import ABC, abstractmethod

from ratanpy.ratan.data_receiver import DataReceiver
from ratanpy.ratan.ratan_observation import RatanObservation


class RatanObservationWriter(ABC):

    @abstractmethod
    def write(self, observation: RatanObservation):
        pass

    @staticmethod
    @abstractmethod
    def supports(data_receiver: DataReceiver, file_type: str) -> bool:
        pass