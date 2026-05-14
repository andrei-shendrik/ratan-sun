import copy
import logging
from typing import Tuple

import numpy as np

from ratan_600_data_analyzer.ratan.fast_acquisition_1_3ghz.calibrators.fast_acquisition_1_3ghz_calibration_coefficients import \
    FastAcquisitionCalibrationCoefficients
from ratan_600_data_analyzer.ratan.fast_acquisition_1_3ghz.calibrators.fast_acquisition_1_3ghz_calibrator import \
    FastAcquisition1To3GHzCalibrator
from ratan_600_data_analyzer.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_configuration import config
from ratan_600_data_analyzer.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import \
    FastAcquisition1To3GHzObservation
from ratan_600_data_analyzer.ratan.polarization_type import PolarizationType

logger = logging.getLogger(__name__)


class FastAcquisition1To3GHzCalibratorLebedev(FastAcquisition1To3GHzCalibrator):
    """
        Калибровка, предложенная М.К.Лебедевым и Н.Е.Овчинниковой
    """

    def calibrate(self, observation: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:

        data = observation.data
        lhcp = data.lhcp
        rhcp = data.rhcp
        if lhcp.shape != rhcp.shape:
            raise ValueError(
                f"Polarization arrays has different sizes: {lhcp.shape} != {rhcp.shape}.")

        # поиск координаты спокойного солнца
        qsc_arcsec = self._find_quiet_sun_coordinate(observation)

        # поиск ближайших индексов для каждой из поляризаций
        arcsec_axis = observation.metadata.coordinate_axes.arcsec_axis
        qsc_lhcp_idx = self._find_quiet_sun_coordinate_index(observation.data.lhcp, arcsec_axis, qsc_arcsec)
        qsc_rhcp_idx = self._find_quiet_sun_coordinate_index(observation.data.rhcp, arcsec_axis, qsc_arcsec)

        # калибровка каждой из поляризаций
        interp_flux_dm = self._get_interpolated_flux_dm(observation)

        calibrated_lhcp, coeffs_lhcp = self._calibrate_polarization(
            pol_data=observation.data.lhcp,
            qsc_idx=qsc_lhcp_idx,
            flux_dm=interp_flux_dm
        )

        calibrated_rhcp, coeffs_rhcp = self._calibrate_polarization(
            pol_data=observation.data.rhcp,
            qsc_idx=qsc_rhcp_idx,
            flux_dm=interp_flux_dm
        )

        # сохранение результатов
        observation.data.pol_channel0 = calibrated_lhcp
        observation.data.pol_channel1 = calibrated_rhcp

        metadata = observation.metadata
        metadata.is_calibrated = True
        metadata._quiet_sun_point_arcsec = qsc_arcsec
        metadata._unit = "s.f.u."

        polarization_to_attribute = {
            PolarizationType.LHCP.value: 'lhcp',
            PolarizationType.RHCP.value: 'rhcp'
        }
        channel_mapping = {
            'pol_channel0': polarization_to_attribute[config.pol_ch0],
            'pol_channel1': polarization_to_attribute[config.pol_ch1],
        }

        cal_coeffs = FastAcquisitionCalibrationCoefficients(channel_mapping=channel_mapping)
        cal_coeffs.calibration_coefficients_pol_channel0 = coeffs_lhcp
        cal_coeffs.calibration_coefficients_pol_channel1 = coeffs_rhcp

        metadata.calibration_coefficients = cal_coeffs
        return observation

    @staticmethod
    def _get_interpolated_flux_dm(observation: FastAcquisition1To3GHzObservation) -> np.ndarray:
        frequency_axis = observation.metadata.coordinate_axes.frequency_axis
        freqs_dm, flux_dm = np.loadtxt(config.flux_dm_file, comments='#', unpack=True)

        freq_min, freq_max = frequency_axis[0], frequency_axis[-1]
        xp = np.linspace(freq_min, freq_max, flux_dm.shape[0])
        return np.asarray(np.interp(frequency_axis, xp, flux_dm))

    def _find_quiet_sun_coordinate(self, observation: FastAcquisition1To3GHzObservation) -> float:
        arcsec_axis = observation.metadata.coordinate_axes.arcsec_axis
        lhcp = observation.data.lhcp

        # сужение до [-700; 700]
        narrow_mask = (arcsec_axis >= config.arcsec_min) & (arcsec_axis <= config.arcsec_max)
        arcsec_narrow = arcsec_axis[narrow_mask]

        lhcp_narrow = lhcp[:, narrow_mask].astype(float)

        # значение меньше определенного уровня отбрасываем
        lhcp_narrow[lhcp_narrow < config.raw_data_threshold] = np.nan

        # интерполяция
        lhcp_narrow = self._interpolate_gaps(lhcp_narrow)

        # усреднение по частотам
        avg_scan = np.nansum(lhcp_narrow, axis=0)
        avg_scan[avg_scan == 0.0] = np.inf

        local_min_idx = int(np.argmin(avg_scan))
        found_arcsec = float(arcsec_narrow[local_min_idx])

        # если на краю возвращаем 0
        if abs(found_arcsec) >= (config.arcsec_max - config.edge_tolerance_arcsec):
            found_arcsec = 0.0

        logger.debug(f"Quiet sun coordinate {found_arcsec} arcsec")
        return found_arcsec

    def _find_quiet_sun_coordinate_index(self, raw_data: np.ndarray, arcsec_axis: np.ndarray, target_arcsec: float) -> int:
        active_mask = raw_data > config.raw_data_threshold
        valid_columns_count = np.sum(active_mask, axis=0)
        valid_indices = np.where(valid_columns_count > 0)[0]

        if len(valid_indices) == 0:
            return int(self._val2idx(arcsec_axis, target_arcsec))

        valid_arcsecs = arcsec_axis[valid_indices]
        closest_valid_idx = int(np.argmin(np.abs(valid_arcsecs - target_arcsec)))
        return int(valid_indices[closest_valid_idx])

    def _calibrate_polarization(self, pol_data: np.ndarray, qsc_idx: int, flux_dm: np.ndarray) -> Tuple[
        np.ndarray, np.ndarray]:
        qsc_column = pol_data[:, qsc_idx].astype(float)

        coeffs = np.zeros_like(flux_dm)

        valid_mask = qsc_column >= config.raw_data_threshold
        coeffs[valid_mask] = flux_dm[valid_mask] / qsc_column[valid_mask]

        calibrated_data = pol_data * coeffs[:, np.newaxis]

        special_values_mask = (pol_data == 1) | (pol_data == 2)
        calibrated_data[special_values_mask] = pol_data[special_values_mask] / 100.0
        return calibrated_data, coeffs

    def calibrate_old(self, observation: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:
        qsp = self._find_qsp_coord(observation)
        # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
        # plt.figure(figsize=(14, 8))
        # for freq_idx in range(pol0_data_selection_calibrated.shape[0]):
        #     plt.plot(pol0_data_selection_calibrated[freq_idx, :],
        #             alpha=0.5,
        #             linewidth = 1,
        #             marker = 'o',
        #             markersize = 2
        #     )
        # plt.grid(alpha=0.3)
        # plt.tight_layout()
        # plt.show()

        # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
        # plt.figure(figsize=(12, 7))
        # #shape = pol0_data_selection_calibrated.shape
        # x_min = full_arcsec_scale[-1]
        # x_max = full_arcsec_scale[0]
        # y_min = frequency_scale[0]
        # y_max = frequency_scale[-1]
        #
        # plt.imshow(pol0_data_selection_calibrated, cmap='jet', aspect='auto', origin='lower',
        #            extent=(x_min, x_max, y_min, y_max))
        #
        # plt.colorbar(label="")
        # plt.title("Spectrogram")
        # plt.xlabel("Xscale")
        # plt.ylabel("Frequency")
        # plt.show()

        # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
        # fig = plt.figure(figsize=(10, 7))
        # ax = fig.add_subplot(111, projection='3d')
        # X, Y = np.meshgrid(full_arcsec_scale, freq_selection)
        # surf = ax.plot_surface(X, Y, pol0_data_selection_calibrated, cmap='Spectral_r', edgecolor='none')
        # ax.set_xlabel('x, arcsec')
        # ax.set_ylabel('Frequency, MHz')
        # ax.set_title('Pol0')
        # fig.colorbar(surf, ax=ax, label='s.f.u.')
        # plt.show()
        return observation

    def _find_qsp_coord(self, observation: FastAcquisition1To3GHzObservation) -> int:
        metadata = observation.metadata
        data = observation.data
        lhcp = data.lhcp
        rhcp = data.rhcp
        if lhcp.shape != rhcp.shape:
            metadata.is_bad = True
            raise ValueError(
                f"Polarization arrays has different sizes: {lhcp.shape} != {rhcp.shape}. Observation marked as bad.")

        frequency_axis = metadata.coordinate_axes.frequency_axis
        time_axis = metadata.coordinate_axes.time_axis
        arcsec_axis = metadata.coordinate_axes.arcsec_axis

        lhcp_copy = copy.copy(lhcp)
        rhcp_copy = copy.copy(rhcp)

        threshold = 10
        lhcp_copy[lhcp_copy < threshold] = np.nan
        rhcp_copy[rhcp_copy < threshold] = np.nan

        lhcp_interpolated = self._interpolate(lhcp_copy)
        rhcp_interpolated = self._interpolate(rhcp_copy)

        ref_time = metadata.ref_time

        idx = (arcsec_axis > config.arcsec_min) & (arcsec_axis < config.arcsec_max)
        narrowed_arcsec_axis = arcsec_axis[idx]
        narrowed_time_axis = time_axis[idx]
        narrowed_lhcp = lhcp_interpolated[:, idx]
        narrowed_rhcp = rhcp_interpolated[:, idx]

        # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
        # plt.figure(figsize=(14, 8))
        # plt.plot(narrowed_arcsec_axis, narrowed_lhcp[0],
        #          alpha=0.5,
        #          linewidth=1,
        #          marker='o',
        #          markersize=2
        #          )
        # plt.grid(alpha=0.3)
        # plt.tight_layout()
        # plt.show()

        arr = copy.copy(narrowed_lhcp)
        x_scale = copy.copy(narrowed_arcsec_axis)
        avg_scan = np.nansum(arr, axis=0)

        idx_x_min = self._val2idx(x_scale, -700)
        idx_x_max = self._val2idx(x_scale, 700)
        avg_scan = avg_scan[idx_x_max:idx_x_min]
        x_scale = x_scale[idx_x_max:idx_x_min]

        # Арксекунды развернуты
        suggested_qsp_idx = np.argmin(avg_scan)
        suggested_qsp_coord = x_scale[suggested_qsp_idx]

        # lhcp
        arr_lhcp = copy.copy(lhcp[:,idx])
        arr_lhcp = arr_lhcp[:, idx_x_max:idx_x_min]
        avg_scan_lhcp = np.nansum(arr_lhcp, axis=0)
        lhcp_not_nan_indices = np.where(avg_scan_lhcp != 0)[0]
        lhcp_not_nan_arcsec = x_scale[lhcp_not_nan_indices]

        #qsp_lhcp = suggested_qsp
        #qsp_lhcp_idx = np.argmin(np.abs(arcsec_axis - qsp_lhcp))
        #print(f"QSP {suggested_qsp}")

        # rhcp
        arr_rhcp = copy.copy(rhcp[:, idx])
        arr_rhcp = arr_rhcp[:, idx_x_max:idx_x_min]
        avg_scan_rhcp = np.nansum(arr_rhcp, axis=0)
        rhcp_not_nan_indices = np.where(avg_scan_rhcp != 0)[0]
        rhcp_not_nan_arcsec = x_scale[rhcp_not_nan_indices]

        all_not_nan_coords = np.concatenate([lhcp_not_nan_arcsec, rhcp_not_nan_arcsec])
        distances_to_target = np.abs(all_not_nan_coords - suggested_qsp_coord)
        best_overall_coord = all_not_nan_coords[np.argmin(distances_to_target)]

        if best_overall_coord in lhcp_not_nan_arcsec:
            qsp_coord_lhcp = best_overall_coord
            distances_to_anchor = np.abs(rhcp_not_nan_arcsec - qsp_coord_lhcp)
            qsp_coord_rhcp = rhcp_not_nan_arcsec[np.argmin(distances_to_anchor)]
        else:
            qsp_coord_rhcp = best_overall_coord
            distances_to_anchor = np.abs(lhcp_not_nan_arcsec - qsp_coord_rhcp)
            qsp_coord_lhcp = lhcp_not_nan_arcsec[np.argmin(distances_to_anchor)]

        qsp_lhcp_idx = np.argmin(np.abs(arcsec_axis - qsp_coord_lhcp))
        qsp_rhcp_idx = np.argmin(np.abs(arcsec_axis - qsp_coord_rhcp))

        flux_dm_file = config.flux_dm_file
        freqs_dm, flux_dm = np.loadtxt(
            flux_dm_file,
            comments='#',
            unpack=True
        )

        # Таблица потоков спокойного Солнца на некоторой сетке частот
        fp = flux_dm
        # Интерполяция здесь нужна, поскольку таблица значений потоков FLUX_DM есть только для одной сетки частот,
        # которая может отличаться от использованной в наблюдении - все зависит от усреднения по частотам
        freq_min = frequency_axis[0]
        freq_max = frequency_axis[-1]
        xp = np.linspace(freq_min, freq_max, fp.shape[0])
        interp_flux = np.interp(frequency_axis, xp, fp)
        cal_coeffs0 = interp_flux / lhcp[:, qsp_lhcp_idx]
        pol0_calibrated = (lhcp.T * cal_coeffs0).T
        for el in config.filter_bands:
            idx = (frequency_axis >= el[0]) & (frequency_axis <= el[1])
            pol0_calibrated[idx] = 0

        cal_coeffs1 = interp_flux / rhcp[:, qsp_rhcp_idx]
        pol1_calibrated = (rhcp.T * cal_coeffs1).T
        for el in config.filter_bands:
            idx = (frequency_axis >= el[0]) & (frequency_axis <= el[1])
            pol1_calibrated[idx] = 0

        # todo
        mask0 = (lhcp == 1) | (lhcp == 2)
        pol0_calibrated[mask0] = lhcp[mask0] / 100

        mask1 = (rhcp == 1) | (rhcp == 2)
        pol1_calibrated[mask1] = rhcp[mask1] / 100

        observation.data.pol_channel0 = pol0_calibrated
        observation.data.pol_channel1 = pol1_calibrated

        metadata.is_calibrated = True
        metadata._quiet_sun_point_arcsec = suggested_qsp_coord.value
        metadata._unit = "s.f.u."

        polarization_to_attribute = {
            PolarizationType.LHCP.value: 'lhcp',
            PolarizationType.RHCP.value: 'rhcp'
        }
        channel_mapping = {
            'pol_channel0': polarization_to_attribute[config.pol_ch0],
            'pol_channel1': polarization_to_attribute[config.pol_ch1],
        }
        cal_coeffs = FastAcquisitionCalibrationCoefficients(channel_mapping=channel_mapping)
        cal_coeffs.calibration_coefficients_pol_channel0 = cal_coeffs0
        cal_coeffs.calibration_coefficients_pol_channel1 = cal_coeffs1
        observation.metadata.calibration_coefficients = cal_coeffs
        observation.metadata = metadata

        # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
        # plt.figure(figsize=(14, 8))
        # plt.plot(pol0_calibrated[0],
        #          alpha=0.5,
        #          linewidth=1,
        #          marker='o',
        #          markersize=2
        #          )
        # plt.grid(alpha=0.3)
        # plt.tight_layout()
        # plt.show()

        # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
        # fig, ax = plt.subplots()
        # # im = ax.pcolormesh(full_arcsec_scale, freq_selection, pol0_data_selection_calibrated,
        # #                    shading='gouraud', cmap='Spectral_r')
        # contour = ax.contourf(arcsec_axis, frequency_axis, pol0_calibrated, levels=100,
        #                       cmap='Spectral_r')
        # ax.set_xlabel('x, arcsec')
        # ax.set_ylabel('Frequency, MHz')
        # ax.set_title('Spectrogram Pol0')
        # fig.colorbar(contour, ax=ax, label='s.f.u.')
        # plt.show()

        return 0

    # def calibrate_old(self) -> FastAcquisition1To3GHzObservation:
    #
    #     metadata = self._observation.metadata
    #     pol_chan_data = self._observation.data.pol_channels_data
    #     pol0_data = np.hstack((np.fliplr(pol_chan_data.c0p0_data), pol_chan_data.c1p0_data)).T
    #     pol1_data = np.hstack((np.fliplr(pol_chan_data.c0p1_data), pol_chan_data.c1p1_data)).T
    #
    #     # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     # plt.figure(figsize=(14, 8))
    #     # plt.plot(pol0_data[0],
    #     #          alpha=0.5,
    #     #          linewidth=1,
    #     #          marker='o',
    #     #          markersize=2
    #     #          )
    #     # plt.grid(alpha=0.3)
    #     # plt.tight_layout()
    #     # plt.show()
    #
    #     f0, t0 = pol0_data.shape[:2]
    #     f1, t1 = pol1_data.shape[:2]
    #     if f0 != f1:
    #         raise ValueError(f"Pol data arrays are not equal")
    #
    #     spectrum_length = f0
    #     frequency_scale = np.linspace(config.freq_min, config.freq_max, spectrum_length)
    #
    #     # selection
    #     selection = [config.freq_min, config.freq_max]
    #     #selection = [1100, 1700]
    #     selection_indexes = (selection[0] <= frequency_scale) & (
    #             frequency_scale <= selection[1])
    #     freq_selection = frequency_scale[selection_indexes]
    #     if pol0_data is not None:
    #         pol0_data_selection = pol0_data[selection_indexes]
    #     if pol1_data is not None:
    #         pol1_data_selection = pol1_data[selection_indexes]
    #
    #     pol0_data_selection_orig = copy.deepcopy(pol0_data_selection)
    #     pol1_data_selection_orig = copy.deepcopy(pol1_data_selection)
    #
    #     threshold = 10
    #     pol0_data_selection[pol0_data_selection < threshold] = np.nan
    #     pol1_data_selection[pol1_data_selection < threshold] = np.nan
    #
    #     pol0_data_selection = self._interpolate(pol0_data_selection)
    #     pol1_data_selection = self._interpolate(pol1_data_selection)
    #
    #     # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     # plt.figure(figsize=(14, 8))
    #     # plt.plot(pol0_data_selection[0],
    #     #          alpha=0.5,
    #     #          linewidth=1,
    #     #          marker='o',
    #     #          markersize=2
    #     #          )
    #     # plt.grid(alpha=0.3)
    #     # plt.tight_layout()
    #     # plt.show()
    #
    #     pol0_time_scale = np.arange(t0) / SAMPLES_PER_SECOND
    #     pol1_time_scale = np.arange(t1) / SAMPLES_PER_SECOND
    #
    #
    #     # Таблица потоков спокойного Солнца на некоторой сетке частот
    #     fp = FLUX_DM
    #     # Интерполяция здесь нужна, поскольку таблица значений потоков FLUX_DM есть только для одной сетки частот,
    #     # которая может отличаться от использованной в наблюдении - все зависит от усреденения по частотам
    #     xp = np.linspace(FREQ_MIN, FREQ_MAX, fp.shape[0])
    #     interp_flux = np.interp(frequency_scale, xp, fp)
    #
    #     # todo temp
    #     ref_time = metadata.ref_time
    #     if pol0_time_scale is not None:
    #         arcsec_scale = - (pol0_time_scale - ref_time) * metadata.arcsec_per_second
    #         full_arcsec_scale = copy.deepcopy(arcsec_scale)
    #         idx = (arcsec_scale > ARCSEC_MIN) & (arcsec_scale < ARCSEC_MAX)
    #         pol0_arcsec_scale = arcsec_scale[idx]
    #         pol0_time_scale = pol0_time_scale[idx]
    #         pol0_data = pol0_data[:, idx]
    #     if pol1_time_scale is not None:
    #         arcsec_scale = - (pol1_time_scale - ref_time) * metadata.arcsec_per_second
    #         idx = (arcsec_scale > ARCSEC_MIN) & (arcsec_scale < ARCSEC_MAX)
    #         pol1_arcsec_scale = arcsec_scale[idx]
    #         pol1_time_scale = pol1_time_scale[idx]
    #         pol1_data = pol1_data[:, idx]
    #
    #     arcsec_per_second = metadata.arcsec_per_second
    #     arcsec_scale = - (pol0_time_scale - ref_time) * arcsec_per_second
    #
    #     print("Arcsec:")
    #     print(f"size {full_arcsec_scale.shape}, F {full_arcsec_scale[0]} , L {full_arcsec_scale[-1]}")
    #     # for val in full_arcsec_scale:
    #     #     print(val)
    #
    #     print(pol0_data[0].shape) # (24964,)
    #     print(pol0_data_selection[0].shape) # (63296,)
    #     print(pol0_data_selection_orig[0].shape) # (63296,)
    #
    #     # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     # plt.figure(figsize=(14, 8))
    #     # plt.plot(full_arcsec_scale, pol0_data_selection[0],
    #     #          alpha=0.5,
    #     #          linewidth=1,
    #     #          marker='o',
    #     #          markersize=2
    #     #          )
    #     # plt.grid(alpha=0.3)
    #     # plt.tight_layout()
    #     #plt.show()
    #
    #     # todo temp0
    #     if pol0_data_selection is not None:
    #         arr = pol0_data_selection
    #         x_scale = pol0_arcsec_scale
    #         print(f"G {arr.shape} {x_scale.shape}")
    #     elif pol1_data_selection is not None:
    #         arr = pol1_data_selection
    #         x_scale = pol1_arcsec_scale
    #     else:
    #         arr = None
    #         x_scale = None
    #
    #     #try:
    #         #avg_scan = arr.sum(axis=0)
    #     avg_scan = np.nansum(arr, axis=0)
    #     x_scale = full_arcsec_scale # важно !!!
    #     print(f"{x_scale.shape} {avg_scan.shape} {arcsec_scale.shape}")
    #
    #     idx_x_min = self._val2idx(x_scale, -700)
    #     idx_x_max = self._val2idx(x_scale, 700)
    #     avg_scan = avg_scan[idx_x_max:idx_x_min]
    #     x_scale = x_scale[idx_x_max:idx_x_min]
    #
    #     # Арксекунды развернуты
    #     suggested_qsp_idx = np.argmin(avg_scan)
    #     suggested_qsp = x_scale[suggested_qsp_idx]
    #     #except ValueError:
    #     #    suggested_qsp = 0
    #
    #     # for num in x_scale:
    #     #     print(f"{num:.2f}")
    #
    #     qsp = suggested_qsp
    #     print(f"QSP {suggested_qsp}")
    #     #
    #
    #     interp_flux_selection = interp_flux[selection_indexes]
    #     if pol0_data_selection is not None:
    #         print(f"00 {pol0_data_selection.shape}")
    #         print(f"000 {pol0_arcsec_scale.shape}")
    #         qsp_idx = np.argmin(np.abs(full_arcsec_scale - qsp))
    #         print(f"F {pol0_arcsec_scale.shape}")
    #         print(f"qsp ind {qsp_idx}")
    #         cal_coeffs = interp_flux_selection / pol0_data_selection[:, qsp_idx]
    #         print(f"cal coeffs {cal_coeffs}")
    #         pol0_data_selection_calibrated = (pol0_data_selection.T * cal_coeffs).T
    #         metadata._calibr_coeff_p0 = cal_coeffs
    #         for el in FILTER_BANDS:
    #             idx = (freq_selection >= el[0]) & (freq_selection <= el[1])
    #             pol0_data_selection_calibrated[idx] = 0
    #     if pol1_data_selection is not None:
    #         qsp_idx = np.argmin(np.abs(full_arcsec_scale - qsp))
    #         cal_coeffs = interp_flux_selection / pol1_data_selection[:, qsp_idx]
    #         pol1_data_selection_calibrated = (pol1_data_selection.T * cal_coeffs).T
    #         metadata._calibr_coeff_p1 = cal_coeffs
    #         for el in FILTER_BANDS:
    #             idx = (freq_selection >= el[0]) & (freq_selection <= el[1])
    #             pol1_data_selection_calibrated[idx] = 0
    #
    #     mask0 = (pol0_data_selection_orig == 1) | (pol0_data_selection_orig == 2)
    #     pol0_data_selection_calibrated[mask0] = pol0_data_selection_orig[mask0]
    #
    #     mask1 = (pol1_data_selection_orig == 1) | (pol1_data_selection_orig == 2)
    #     pol1_data_selection_calibrated[mask1] = pol1_data_selection_orig[mask1]
    #
    #     # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     # plt.figure(figsize=(14, 8))
    #     # plt.plot(pol0_data_selection_calibrated,
    #     #          alpha=0.5,
    #     #          linewidth=1,
    #     #          marker='o',
    #     #          markersize=2
    #     #          )
    #     # plt.grid(alpha=0.3)
    #     # plt.tight_layout()
    #     # plt.show()
    #     #
    #     # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     # plt.figure(figsize=(14, 8))
    #     # plt.plot(pol0_data_selection[0],
    #     #          alpha=0.5,
    #     #          linewidth=1,
    #     #          marker='o',
    #     #          markersize=2
    #     #          )
    #     # plt.grid(alpha=0.3)
    #     # plt.tight_layout()
    #     # plt.show()
    #
    #     array_3d = np.stack([pol0_data_selection_calibrated, pol1_data_selection_calibrated], axis=1)
    #     self._observation.data.array_3d = array_3d
    #
    #     # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     # plt.figure(figsize=(14, 8))
    #     # for freq_idx in range(pol0_data_selection_calibrated.shape[0]):
    #     #     plt.plot(pol0_data_selection_calibrated[freq_idx, :],
    #     #             alpha=0.5,
    #     #             linewidth = 1,
    #     #             marker = 'o',
    #     #             markersize = 2
    #     #     )
    #     # plt.grid(alpha=0.3)
    #     # plt.tight_layout()
    #     # plt.show()
    #
    #     # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     # plt.figure(figsize=(12, 7))
    #     # #shape = pol0_data_selection_calibrated.shape
    #     # x_min = full_arcsec_scale[-1]
    #     # x_max = full_arcsec_scale[0]
    #     # y_min = frequency_scale[0]
    #     # y_max = frequency_scale[-1]
    #     #
    #     # plt.imshow(pol0_data_selection_calibrated, cmap='jet', aspect='auto', origin='lower',
    #     #            extent=(x_min, x_max, y_min, y_max))
    #     #
    #     # plt.colorbar(label="")
    #     # plt.title("Spectrogram")
    #     # plt.xlabel("Xscale")
    #     # plt.ylabel("Frequency")
    #     # plt.show()
    #
    #     matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     fig, ax = plt.subplots()
    #     # im = ax.pcolormesh(full_arcsec_scale, freq_selection, pol0_data_selection_calibrated,
    #     #                    shading='gouraud', cmap='Spectral_r')
    #     contour = ax.contourf(full_arcsec_scale, freq_selection, pol0_data_selection_calibrated, levels=100, cmap='Spectral_r')
    #     ax.set_xlabel('x, arcsec')
    #     ax.set_ylabel('Frequency, MHz')
    #     ax.set_title('Spectrogram Pol0')
    #     fig.colorbar(contour, ax=ax, label='s.f.u.')
    #     plt.show()
    #
    #     # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    #     # fig = plt.figure(figsize=(10, 7))
    #     # ax = fig.add_subplot(111, projection='3d')
    #     # X, Y = np.meshgrid(full_arcsec_scale, freq_selection)
    #     # surf = ax.plot_surface(X, Y, pol0_data_selection_calibrated, cmap='Spectral_r', edgecolor='none')
    #     # ax.set_xlabel('x, arcsec')
    #     # ax.set_ylabel('Frequency, MHz')
    #     # ax.set_title('Pol0')
    #     # fig.colorbar(surf, ax=ax, label='s.f.u.')
    #     # plt.show()
    #
    #
    #     return self._observation

    @staticmethod
    def _val2idx(a, v):
        return np.argmin(np.abs(np.array(a) - v))

    @staticmethod
    def _interpolate_gaps(array: np.ndarray) -> np.ndarray:
        for i in range(array.shape[0]):
            row = array[i]
            nan_indices = np.isnan(row)
            if not np.any(nan_indices) or np.all(nan_indices):
                continue

            x_interp = np.flatnonzero(nan_indices)
            x_known = np.flatnonzero(~nan_indices)
            array[i, x_interp] = np.interp(x_interp, x_known, row[x_known])

        return array

    # @staticmethod
    # def _interpolate(array: np.ndarray) -> np.ndarray:
    #
    #     interp_array = copy.deepcopy(array)
    #     n_rows = interp_array.shape[0]
    #     for i in range(n_rows):
    #         row = interp_array[i]
    #         nan_indices = np.isnan(row)
    #         non_nan_indices = ~nan_indices
    #
    #         if not np.any(non_nan_indices) or not np.any(nan_indices):
    #             continue
    #
    #         x_interp = np.flatnonzero(nan_indices)
    #         x_known = np.flatnonzero(non_nan_indices)
    #         y_known = row[x_known]
    #         y_interp = np.interp(x_interp, x_known, y_known)
    #
    #         interp_array[i, x_interp] = y_interp
    #
    #     return interp_array