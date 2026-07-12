from abc import abstractmethod

from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation
from ratanpy.ratan.ratan_interpolator import RatanInterpolator


class FastAcquisition1To3GHzInterpolator(RatanInterpolator):

    @abstractmethod
    def process(self, observation: FastAcquisition1To3GHzObservation):
        pass