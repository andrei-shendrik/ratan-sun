from abc import abstractmethod

from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratanpy.ratan.services.ratan_observation_calibrator import RatanObservationCalibrator


class FastAcquisition1To3GHzCalibrator(RatanObservationCalibrator):

    @abstractmethod
    def calibrate(self, observation: FastAcquisition1To3GHzObservation):
        pass