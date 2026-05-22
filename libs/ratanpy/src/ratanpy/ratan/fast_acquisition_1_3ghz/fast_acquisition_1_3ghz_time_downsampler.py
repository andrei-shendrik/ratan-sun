
# todo
# def time_downsample(self, time_reduction_factor: int) -> FastAcquisition1To3GHzBuilder:
#
#     pol_chan_data = self._observation.data.pol_channels_data
#     joined_channels_0 = np.hstack((np.fliplr(pol_chan_data.c0p0_data), pol_chan_data.c1p0_data)).T  # 1-3 GHz pol0
#     joined_channels_1 = np.hstack((np.fliplr(pol_chan_data.c0p1_data), pol_chan_data.c1p1_data)).T  # 1-3 GHz pol1
#
#     pol0_data = self._trim_polarization_array(joined_channels_0, time_reduction_factor = time_reduction_factor)
#     pol1_data = self._trim_polarization_array(joined_channels_1, time_reduction_factor = time_reduction_factor)
#
#     array_3d = np.stack([pol0_data, pol1_data], axis=1)
#
#     fast_acq_data = FastAcquisition1To3GHzData()
#     fast_acq_data.pol_channels_data = pol_chan_data
#     fast_acq_data.kurtosis_data = self._data.kurtosis_data
#     fast_acq_data.gen_state_data = self._data.gen_state_data
#     fast_acq_data.array_3d = array_3d
#
#     bin_file = self._metadata.bin_file
#     fast_acq_metadata = FastAcquisition1To3GHzMetadataBinLoader.load(bin_file, fast_acq_data)
#
#     self._metadata = fast_acq_metadata
#     self._data = fast_acq_data
#     return self