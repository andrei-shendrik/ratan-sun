from pathlib import Path
from typing import TypeGuard, Union

from ratanpy.ratan.data_receiver import DataReceiver
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_processor import \
    FastAcquisition1To3GHzProcessor
from ratanpy.ratan.ratan_observation_processor import RatanObservationProcessor
from ratanpy.ratan.sspc.sspc_processor import SSPCProcessor


class RatanProcessorFactory:

    @staticmethod
    def create_processor(file: Path) -> Union[FastAcquisition1To3GHzProcessor, SSPCProcessor]:

        extensions = file.suffixes
        if (extensions == ['.bin', '.gz']) or (extensions == ['.bin']):
            processor = FastAcquisition1To3GHzProcessor(file)
            processor.receiver = DataReceiver.FAST_ACQUISITION_1_3GHZ
            return processor
        if extensions == '.fits':
            processor = SSPCProcessor(file)
            processor.receiver = DataReceiver.SSPC
            return processor
        raise ValueError(f"No suitable processors found for file: {file}")

    @staticmethod
    def is_fast_1_3ghz_processor(processor: RatanObservationProcessor) -> TypeGuard[FastAcquisition1To3GHzProcessor]:
        return processor.receiver == DataReceiver.FAST_ACQUISITION_1_3GHZ

    @staticmethod
    def is_sspc_processor(processor: RatanObservationProcessor) -> TypeGuard[SSPCProcessor]:
        result = ((processor.receiver == DataReceiver.SSPC_16) or
                  (processor.receiver == DataReceiver.SSPC))
        return result