from abc import abstractmethod

from ratan_600_data_analyzer.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.services.ratan_interference_remover import RatanInterferenceRemover


class FastAcquisition1To3GHzInterferenceRemover(RatanInterferenceRemover):

    @abstractmethod
    def process(self, observation: FastAcquisition1To3GHzObservation):
        pass