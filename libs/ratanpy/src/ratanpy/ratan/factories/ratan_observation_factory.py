from abc import ABC, abstractmethod
from pathlib import Path

from ratanpy.ratan.ratan_observation import RatanObservation
from ratanpy.ratan.ratan_observation_processor import RatanObservationBuilder
from ratanpy.ratan.services.ratan_observation_calibrator import RatanObservationCalibrator
from ratanpy.ratan.services.ratan_observation_reader import RatanObservationReader
from ratanpy.ratan.services.ratan_observation_writer import RatanObservationWriter


class RatanObservationFactory(ABC):

    @abstractmethod
    def create_reader(self, file: Path) -> RatanObservationReader:
        pass

    @abstractmethod
    def create_calibrator(self) -> RatanObservationCalibrator:
        pass

    @abstractmethod
    def create_writer(self, observation: RatanObservation, file_type: str) -> RatanObservationWriter:
        pass

    @abstractmethod
    def create_builder(self, file: Path) -> RatanObservationBuilder:
        pass
