from __future__ import annotations
from pathlib import Path

from ratan_600_data_analyzer.ratan.data_receiver import DataReceiver
from ratan_600_data_analyzer.ratan.ratan_observation_processor import RatanObservationProcessor
from ratan_600_data_analyzer.ratan.factories.ratan_reader_factory import RatanReaderFactory
from ratan_600_data_analyzer.ratan.sspc.sspc_observation import SSPCObservation


class SSPCProcessor(RatanObservationProcessor):
    def __init__(self, file: Path):
        super().__init__(file)
        self._observation = None

    def read(self) -> SSPCProcessor:
        reader = RatanReaderFactory.create_reader(self._file)
        observation = reader.read(self._file)
        self._observation = observation
        return self

    def calibrate(self):
        # todo
        pass

    def remove_interference(self):
        # todo
        pass

    def get_observation(self) -> SSPCObservation:
        return self._observation

    @property
    def receiver(self) -> DataReceiver:
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        self._receiver = value