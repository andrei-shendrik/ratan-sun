from pathlib import Path

from ratanpy.ratan.factories.ratan_processor_factory import RatanProcessorFactory
from ratanpy.ratan.factories.ratan_reader_factory import RatanReaderFactory
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

FITS_OUTPUT_PATH = Path(r"D:\data\astro\ratan-600\fast-acquisition-1-3ghz\fits\sun")

class FastAcquisition1To3GHzProcessingDirector:

    @staticmethod
    def run_standard_processing(bin_file: Path) -> FastAcquisition1To3GHzObservation:

        processor = RatanProcessorFactory.create_processor(bin_file)
        if not RatanProcessorFactory.is_fast_1_3ghz_processor(processor):
            raise ValueError(f"Invalid processor type for file {bin_file.name}")

        observation = (
            processor.read()
            .remove_interference(FastAcquisition1To3GHzKurtosisInterferenceRemover())
            .drop_raw_data()
            .filter_channels(FastAcquisition1To3GHzBandFilter(config.filter_bands))
            .calibrate(FastAcquisition1To3GHzCalibratorLebedev())
            .get_observation()
        )

        # todo: add methods:
        # .convert_to_iv()
        # .trim_data() # arcsec_min, arcsec_max; NG_peaks
        # .interpolate_gaps(method="linear")
        # .time_downsample(time_reduction_factor=16) TimeDownsampler
        # .frequency_downsample(FREQUENCY_REDUCTION_FACTOR) FrequencyDownsampler

        if observation is None:
            raise RuntimeError("Processing failed: no observation created")

        if not isinstance(observation, FastAcquisition1To3GHzObservation):
            raise TypeError("Processing failed: Invalid observation type returned")

        return observation

    @staticmethod
    def explicit_processing(obs_file: Path):
        reader = RatanReaderFactory.create_reader(obs_file)
        observation = reader.read(obs_file)
        output_fits_file = Path()
        overwrite = True

        assert isinstance(observation, FastAcquisition1To3GHzObservation)

        remover = FastAcquisition1To3GHzKurtosisInterferenceRemover()
        remover.process(observation)

        calibrator = FastAcquisition1To3GHzCalibratorLebedev()
        calibrator.calibrate(observation)

        if not isinstance(observation, FastAcquisition1To3GHzObservation):
            raise TypeError("Processing failed: Invalid observation type returned")

        writer = FastAcquisition1To3GHzFitsWriter(output_fits_file, overwrite)
        writer.write(observation)