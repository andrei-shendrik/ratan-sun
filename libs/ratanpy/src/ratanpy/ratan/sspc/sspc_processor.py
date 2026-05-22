from __future__ import annotations
from pathlib import Path

from ratanpy.ratan.data_receiver import DataReceiver
from ratanpy.ratan.ratan_observation_processor import RatanObservationProcessor
from ratanpy.ratan.factories.ratan_reader_factory import RatanReaderFactory
from ratanpy.ratan.sspc.sspc_observation import SSPCObservation


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