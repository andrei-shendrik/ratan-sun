from typing import List, Type

from ratan_600_data_analyzer.ratan.fast_acquisition_1_3ghz import \
    FastAcquisition1To3GHzFitsWriter
from ratan_600_data_analyzer.ratan.ratan_observation import RatanObservation
from ratan_600_data_analyzer.ratan.services.ratan_observation_writer import RatanObservationWriter


class RatanWriterFactory:

    WRITER_CLASSES: List[Type[RatanObservationWriter]] = [
        FastAcquisition1To3GHzFitsWriter
    ]

    @staticmethod
    def create_writer(observation: RatanObservation, file_type: str) -> RatanObservationWriter:

        for writer_class in RatanWriterFactory.WRITER_CLASSES:
            writer = writer_class(observation)
            if writer.supports(observation.metadata.data_receiver, file_type):
                return writer
        raise ValueError(f"No suitable writer found for observation: {observation.metadata.file}")