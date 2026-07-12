from __future__ import annotations

import gc
from pathlib import Path

from ratanpy.ratan.data_receiver import DataReceiver
from ratanpy.ratan.fast_acquisition_1_3ghz.calibrators.fast_acquisition_1_3ghz_calibrator import \
    FastAcquisition1To3GHzCalibrator
from ratanpy.ratan.fast_acquisition_1_3ghz.channel_filters.fast_acquisition_1_3ghz_channel_filter import \
    FastAcquisition1To3GHzChannelFilter
from ratanpy.ratan.fast_acquisition_1_3ghz.downsamplers.fast_acquisition_1_3ghz_downsampler import \
    FastAcquisition1To3GHzDownsampler
from ratanpy.ratan.fast_acquisition_1_3ghz.interpolators.fast_acquisition_1_3ghz_interpolator import \
    FastAcquisition1To3GHzInterpolator
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratanpy.ratan.fast_acquisition_1_3ghz.interference_removers.fast_acquisition_1_3ghz_interference_remover import \
    FastAcquisition1To3GHzInterferenceRemover
from ratanpy.ratan.fast_acquisition_1_3ghz.writers.fast_acquisition_1_3ghz_fits_writer import \
    FastAcquisition1To3GHzFitsWriter
from ratanpy.ratan.ratan_observation_processor import RatanObservationProcessor
from ratanpy.ratan.factories.ratan_reader_factory import RatanReaderFactory


class FastAcquisition1To3GHzProcessor(RatanObservationProcessor):
    def __init__(self, file: Path):
        super().__init__(file)
        self._observation = None

    @property
    def receiver(self) -> DataReceiver:
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        self._receiver = value

    def get_observation(self) -> FastAcquisition1To3GHzObservation:
        return self._observation

    def read(self) -> FastAcquisition1To3GHzProcessor:
        reader = RatanReaderFactory.create_reader(self._file)
        observation = reader.read(self._file)
        self._observation = observation
        return self

    def remove_interference(self, remover: FastAcquisition1To3GHzInterferenceRemover) -> FastAcquisition1To3GHzProcessor:
        self._observation = remover.process(self._observation)
        return self

    def write(self, writer: FastAcquisition1To3GHzFitsWriter) -> FastAcquisition1To3GHzProcessor:
        writer.write(self._observation)
        return self

    def calibrate(self, calibrator: FastAcquisition1To3GHzCalibrator) -> FastAcquisition1To3GHzProcessor:
        observation = calibrator.calibrate(self._observation)
        self._observation = observation
        return self

    def filter_channels(self, chan_filter: FastAcquisition1To3GHzChannelFilter) -> FastAcquisition1To3GHzProcessor:
        observation = chan_filter.filter_channels(self._observation)
        self._observation = observation
        return self

    def drop_raw_data(self):
        if self._observation.raw_data is not None:
            self._observation.raw_data = None
            gc.collect()
        return self

    def interpolate(self, interpolator: FastAcquisition1To3GHzInterpolator) -> FastAcquisition1To3GHzProcessor:
        observation = interpolator.process(self._observation)
        self._observation = observation
        return self

    def downsample(self, downsampler: FastAcquisition1To3GHzDownsampler) -> FastAcquisition1To3GHzProcessor:
        observation = downsampler.process(self._observation)
        self._observation = observation
        return self