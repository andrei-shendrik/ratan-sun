import gc
import logging

from pathlib import Path

from ratanpy.ratan.factories.ratan_processor_factory import RatanProcessorFactory
from ratanpy.ratan.fast_acquisition_1_3ghz.calibrators.fast_acquisition_1_3ghz_calibrator_lebedev import \
    FastAcquisition1To3GHzCalibratorLebedev
from ratanpy.ratan.fast_acquisition_1_3ghz.channel_filters.fast_acquition_1_3ghz_bands_filter import \
    FastAcquisition1To3GHzBandFilter
from ratanpy.ratan.fast_acquisition_1_3ghz.config.config_instance import config
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation
from ratanpy.ratan.fast_acquisition_1_3ghz.interference_removers import \
    FastAcquisition1To3GHzKurtosisInterferenceRemover
from ratanpy.ratan.fast_acquisition_1_3ghz.writers.fast_acquisition_1_3ghz_fits_writer import \
    FastAcquisition1To3GHzFitsWriter

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzObservationProcessingDirector:
    """
        Обработка наблюдения
    """
    @staticmethod
    def execute(bin_file: Path, output_fits_file: Path, overwrite: bool) -> None:
        logger.info(f"[{bin_file.name}] Started processing")

        processor = RatanProcessorFactory.create_processor(bin_file)
        if not RatanProcessorFactory.is_fast_1_3ghz_processor(processor):
            raise ValueError(f"Invalid processor type for file {bin_file.name}")

        observation = (
            processor.read()
            .remove_interference(FastAcquisition1To3GHzKurtosisInterferenceRemover())
            .drop_raw_data()
            .filter_channels(FastAcquisition1To3GHzBandFilter(config.filter_bands))
            .calibrate(FastAcquisition1To3GHzCalibratorLebedev())
            .write(FastAcquisition1To3GHzFitsWriter(output_fits_file, overwrite))
            .get_observation()
        )

        if observation is None:
            raise RuntimeError("Processing failed: no observation created")

        if not isinstance(observation, FastAcquisition1To3GHzObservation):
            raise TypeError("Processing failed: Invalid observation type returned")

        del observation
        gc.collect()