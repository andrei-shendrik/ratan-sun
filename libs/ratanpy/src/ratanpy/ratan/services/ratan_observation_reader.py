from abc import ABC, abstractmethod
from pathlib import Path

from ratanpy.observation.observation_reader import ObservationReader
from ratanpy.ratan.ratan_observation import RatanObservation


class RatanObservationReader(ObservationReader, ABC):

    @abstractmethod
    def can_read(self, file: Path) -> bool:
        pass

    @abstractmethod
    def read(self, file: Path) -> RatanObservation:
        pass

    @abstractmethod
    def read_metadata(self, file: Path) -> RatanObservation:
        pass