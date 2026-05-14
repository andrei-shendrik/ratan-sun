# todo
# def interpolate_gaps(self, method: str) -> FastAcquisition1To3GHzBuilder:
#     if method == "linear":
#         """
#             replace_nan заполняет nan значениями, полученными линейной интерполяцией между крайними значениями соседних
#             промежутков. В fast_input есть функция replace_nan_interp, которая вычисляет средние по соседним промежуткам
#             и интерполирует между этими средними, что кажется более корректным; кроме того, она может добавлять к
#             интерполированным значениям гауссовский шум с мощностью, равной среднему арифметическому мощности шума в
#             соседних промежутках. Естественно, все это работает гораздо медленнее.
#         """
#
#         pol_chan_data = self._data.pol_channels_data
#
#         ch0_pol0 = fast_input.replace_nan(pol_chan_data.c0p0_data)
#         ch0_pol1 = fast_input.replace_nan(pol_chan_data.c0p1_data)
#         ch1_pol0 = fast_input.replace_nan(pol_chan_data.c1p0_data)
#         ch1_pol1 = fast_input.replace_nan(pol_chan_data.c1p1_data)
#
#         pol_chan_data.c0p0_data = ch0_pol0
#         pol_chan_data.c0p1_data = ch0_pol1
#         pol_chan_data.c1p0_data = ch1_pol0
#         pol_chan_data.c1p1_data = ch1_pol1
#
#         joined_channels_0 = np.hstack(
#             (np.fliplr(pol_chan_data.c0p0_data), pol_chan_data.c1p0_data)).T  # 1-3 GHz pol0
#         joined_channels_1 = np.hstack(
#             (np.fliplr(pol_chan_data.c0p1_data), pol_chan_data.c1p1_data)).T  # 1-3 GHz pol1
#         array_3d = np.stack([joined_channels_0, joined_channels_1], axis=1)
#
#         fast_acq_data = FastAcquisition1To3GHzData()
#         fast_acq_data.pol_channels_data = pol_chan_data
#         fast_acq_data.kurtosis_data = self._data.kurtosis_data
#         fast_acq_data.gen_state_data = self._data.gen_state_data
#         fast_acq_data.array_3d = array_3d
#
#         bin_file = self._metadata.bin_file
#         desc_file = self._metadata.desc_file
#         fast_acq_metadata = FastAcquisition1To3GHzMetadataBinLoader.load(desc_file, bin_file, fast_acq_data)
#
#         self._metadata = fast_acq_metadata
#         self._data = fast_acq_data
#         return self
#     raise ValueError(f"Interpolation method {method} not found.")