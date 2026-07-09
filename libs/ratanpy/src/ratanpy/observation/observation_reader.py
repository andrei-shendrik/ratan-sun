from abc import ABC, abstractmethod
from pathlib import Path

from ratanpy.observation.observation import Observation
from ratanpy.observation.observation_metadata import ObservationMetadata


class ObservationReader(ABC):

    @abstractmethod
    def can_read(self, file_path: Path) -> Observation:
        pass

    @abstractmethod
    def read(self, file_path: Path) -> Observation:
        pass

    @abstractmethod
    def read_metadata(self, file_path: Path) -> ObservationMetadata:
        pass