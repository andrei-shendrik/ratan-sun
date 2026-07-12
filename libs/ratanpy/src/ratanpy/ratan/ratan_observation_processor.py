from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ratanpy.ratan.data_receiver import DataReceiver
from ratanpy.ratan.ratan_interpolator import RatanInterpolator
from ratanpy.ratan.ratan_observation import RatanObservation
from ratanpy.ratan.services.ratan_channel_filter import RatanChannelFilter
from ratanpy.ratan.services.ratan_interference_remover import RatanInterferenceRemover
from ratanpy.ratan.services.ratan_observation_calibrator import RatanObservationCalibrator


class RatanObservationProcessor(ABC):
    def __init__(self, file: Path):
        self._file = file
        self._receiver = None
        self._observation = None

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def calibrate(self, calibrator: RatanObservationCalibrator):
        pass

    @abstractmethod
    def remove_interference(self, remover: RatanInterferenceRemover):
        pass

    @abstractmethod
    def filter_channels(self, channel_filter: RatanChannelFilter):
        pass

    @abstractmethod
    def interpolate(self, interpolator: RatanInterpolator):
        pass

    @abstractmethod
    def get_observation(self) -> RatanObservation:
        pass

    @property
    @abstractmethod
    def receiver(self) -> DataReceiver:
        pass

    @receiver.setter
    @abstractmethod
    def receiver(self, value):
        pass