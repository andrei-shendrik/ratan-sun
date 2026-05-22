import numpy as np

from ratanpy.ratan.fast_acquisition_1_3ghz.config.config_instance import config
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratanpy.ratan.fast_acquisition_1_3ghz.interference_removers.fast_acquisition_1_3ghz_interference_remover import \
    FastAcquisition1To3GHzInterferenceRemover

class FastAcquisition1To3GHzKurtosisInterferenceRemover(FastAcquisition1To3GHzInterferenceRemover):

    def process(self, observation: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:
        raw_data = observation.raw_data
        if raw_data is None:
            raise ValueError("Raw data is None")

        pol_chan_raw_data = raw_data.polarization_channels_data
        kurtosis_data = raw_data.kurtosis_data
        # original
        # pol_chan_data.c0p0_data[kurtosis_data.c0p0_kurt <= KURT_THRESHOLD] = np.nan
        # pol_chan_data.c0p1_data[kurtosis_data.c0p1_kurt <= KURT_THRESHOLD] = np.nan
        # pol_chan_data.c1p0_data[kurtosis_data.c1p0_kurt <= KURT_THRESHOLD] = np.nan
        # pol_chan_data.c1p1_data[kurtosis_data.c1p1_kurt <= KURT_THRESHOLD] = np.nan
        """
            kurtosis replace by 1
        """
        # pol_chan_raw_data.c0p0_data[(kurtosis_data.c0p0_kurt <= config.kurt_threshold)
        #                             & (
        #                                     pol_chan_raw_data.c0p0_data != config.raw_missing_value_replacement)] = config.raw_kurtosis_value_replacement
        # pol_chan_raw_data.c0p1_data[(kurtosis_data.c0p1_kurt <= config.kurt_threshold)
        #                             & (
        #                                     pol_chan_raw_data.c0p1_data != config.raw_missing_value_replacement)] = config.raw_kurtosis_value_replacement
        # pol_chan_raw_data.c1p0_data[(kurtosis_data.c1p0_kurt <= config.kurt_threshold)
        #                             & (
        #                                     pol_chan_raw_data.c1p0_data != config.raw_missing_value_replacement)] = config.raw_kurtosis_value_replacement
        # pol_chan_raw_data.c1p1_data[(kurtosis_data.c1p1_kurt <= config.kurt_threshold)
        #                             & (
        #                                     pol_chan_raw_data.c1p1_data != config.raw_missing_value_replacement)] = config.raw_kurtosis_value_replacement
        self._apply_kurtosis_mask(pol_chan_raw_data.c0p0_data, kurtosis_data.c0p0_kurt)
        self._apply_kurtosis_mask(pol_chan_raw_data.c0p1_data, kurtosis_data.c0p1_kurt)
        self._apply_kurtosis_mask(pol_chan_raw_data.c1p0_data, kurtosis_data.c1p0_kurt)
        self._apply_kurtosis_mask(pol_chan_raw_data.c1p1_data, kurtosis_data.c1p1_kurt)

        joined_channels_0 = np.hstack(
            (np.fliplr(pol_chan_raw_data.c0p0_data), pol_chan_raw_data.c1p0_data)).T  # 1-3 GHz pol0
        joined_channels_1 = np.hstack(
            (np.fliplr(pol_chan_raw_data.c0p1_data), pol_chan_raw_data.c1p1_data)).T  # 1-3 GHz pol1

        fast_acq_data = observation.data
        fast_acq_data.pol_channel0 = joined_channels_0
        fast_acq_data.pol_channel1 = joined_channels_1
        observation.data = fast_acq_data
        return observation

    @staticmethod
    def _apply_kurtosis_mask(data_array, kurt_array):
        mask = kurt_array <= config.kurt_threshold
        mask &= (data_array != config.raw_missing_value_replacement)
        data_array[mask] = config.raw_kurtosis_value_replacement