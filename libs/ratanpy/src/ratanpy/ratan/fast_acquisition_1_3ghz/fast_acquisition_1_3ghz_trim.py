
# todo
# @staticmethod
# def _trim_polarization_array(pol_array: np.ndarray, time_reduction_factor: int) -> np.ndarray:
#     # Приводит массив к размеру, кратному self.time_reduction_factor, усредняет его по времени и заменяет
#     # возможные nan интерполированными значениями
#
#     n_bands, n_points = np.shape(pol_array)
#     pol_array = pol_array[:, :(n_points // time_reduction_factor) * time_reduction_factor]
#     try:
#         pol_array = pol_array.reshape(n_bands, n_points // time_reduction_factor, -1)
#         with warnings.catch_warnings():
#             warnings.filterwarnings(action='ignore', message='Mean of empty slice')
#             pol_array = np.nanmean(pol_array, axis=2)
#         pol_array = fast_input.replace_nan(pol_array)
#     except ValueError:
#         pol_array = None
#     return pol_array