from abc import abstractmethod

from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation
from ratanpy.ratan.ratan_downsampler import RatanDownsampler


class FastAcquisition1To3GHzDownsampler(RatanDownsampler):

    @abstractmethod
    def process(self, observation: FastAcquisition1To3GHzObservation):
        pass