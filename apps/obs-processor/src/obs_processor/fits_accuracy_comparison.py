from datetime import datetime
from pathlib import Path

import numpy as np
from astropy.io import fits

from obs_processor.fast_acquisition_1_3ghz_processing_director import FastAcquisition1To3GHzProcessingDirector
from ratanpy.ratan.fast_acquisition_1_3ghz.config.config_instance import config
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation
from ratanpy.ratan.fast_acquisition_1_3ghz.writers.fast_acquisition_1_3ghz_fits_writer import \
    FastAcquisition1To3GHzFitsWriter
from ratanpy.utils.common_utils import time_counter


@time_counter
def compare_fits(fast_acquisition_bin_file: Path, fits_output_path: Path):

    write = True
    observation = FastAcquisition1To3GHzProcessingDirector.run_standard_processing(fast_acquisition_bin_file)

    if observation is None:
        raise Exception("No observation created")

    if write:
        overwrite = True
        output_fits_file = _get_output_fits_filename(observation, fits_output_path)
        writer = FastAcquisition1To3GHzFitsWriter(output_fits_file, overwrite=overwrite)
        writer.write(observation)
        print(f"Written to {output_fits_file}")

    if not isinstance(observation, FastAcquisition1To3GHzObservation):
        raise

    _print_header_params(observation)

    # write fits
    output_fits_file = _get_output_fits_filename(observation, fits_output_path)
    overwrite = True
    if write:
        writer = FastAcquisition1To3GHzFitsWriter(output_fits_file, overwrite)
        writer.write(observation)
        print(f"Written to {output_fits_file}")

    lhcp = observation.data.lhcp
    rhcp = observation.data.rhcp
    data_cube_bin = np.stack([lhcp, rhcp], axis=1)
    data_cube_fits = read_fits(output_fits_file)
    bin_arr = data_cube_bin[0,0,:]
    fits_arr = data_cube_fits[0, 0, :]
    print(f"Bin {data_cube_bin.shape}")
    print(f"Fits {data_cube_bin.shape}")

    time_axis = observation.metadata.coordinate_axes.time_axis
    print(time_axis)

    start = np.datetime64(observation.metadata.datetime_reg_start_utc.replace(tzinfo=None))
    deltas = (time_axis * 1e9).astype('timedelta64[ns]')
    time_axis_abs = start + deltas
    print(time_axis_abs)

    are_equal = np.array_equal(data_cube_bin, data_cube_fits)
    print(f"Are equal {are_equal}")

    #test
    # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    # plt.figure(figsize=(18, 10))  # Создаем фигуру размером 12x6 дюймов
    #
    # # Рисуем первый массив
    # plt.plot(bin_arr , label='Bin', color='blue', linewidth=1.5)
    #
    # # Рисуем второй массив на той же фигуре
    # plt.plot(fits_arr, label='Fits', color='red', linestyle='--', linewidth=1)
    #
    # # Добавляем элементы для наглядности
    # plt.title('Сравнение массивов для частоты [0] и поляризации [0]')
    # plt.xlabel('Индекс отсчета')
    # plt.ylabel('Амплитуда')
    # plt.legend()  # Показывает метки 'Массив 1' и 'Массив 2'
    # plt.grid(True)  # Включаем сетку
    # plt.tight_layout()  # Оптимизируем поля
    # #plt.show()

    #test2
    difference_data = data_cube_bin - data_cube_fits
    difference = difference_data[0, 0, :]

    # 3. Строим график разницы
    # plt.figure(figsize=(12, 6))
    #
    # plt.plot(difference, label='Diff', color='green')
    #
    # # Добавим горизонтальную линию на уровне нуля для наглядности
    # plt.axhline(0, color='black', linestyle='--', linewidth=0.8, label='Нулевой уровень')
    #
    # # Добавляем элементы
    # plt.title('Разница между массивами для частоты [0] и поляризации [0]')
    # plt.xlabel('Индекс отсчета')
    # plt.ylabel('Разница амплитуд')
    # plt.legend()
    # plt.grid(True)
    # plt.tight_layout()

    # Показываем график
    #plt.show()

    mean_diff = np.mean(difference)
    std_diff = np.std(difference)
    max_diff = np.max(difference)
    min_diff = np.min(difference)

    print("\n--- Статистика разницы ---")
    print(f"Среднее значение разницы: {mean_diff:.16f}")
    print(f"Стандартное отклонение разницы: {std_diff:.16f}")
    print(f"Максимальная разница: {max_diff:.16f}")
    print(f"Минимальная разница: {min_diff:.16f}")

    # test3
    # start_index = 10000
    # end_index = 10100
    #
    # # Извлекаем срезы в этом диапазоне
    # x_axis = np.arange(start_index, end_index)
    # data1_zoom = data_cube_bin[0, 0, start_index:end_index]
    # data2_zoom = data_cube_fits[0, 0, start_index:end_index]
    # diff_zoom = data2_zoom - data1_zoom
    #
    # # --- Создаем комплексный график: сравнение + разница ---
    # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    #
    # # Верхний график: Сравнение сигналов точками
    # # Используем plt.plot с маркерами, это очень быстро
    # ax1.plot(x_axis, data1_zoom, linestyle='none', marker='.', markersize=4, label='Массив 1 (точки)')
    # ax1.plot(x_axis, data2_zoom, linestyle='none', marker='.', markersize=4, label='Массив 2 (точки)',
    #          alpha=0.5)  # alpha - прозрачность
    # ax1.set_title(f'Детальное сравнение точками (участок {start_index}-{end_index})')
    # ax1.set_ylabel('Амплитуда')
    # ax1.legend()
    # ax1.grid(True)
    #
    # # Нижний график: Разница
    # ax2.plot(x_axis, diff_zoom, linestyle='none', marker='o', markersize=3, color='green')
    # ax2.axhline(0, color='black', linestyle='--', linewidth=0.8)
    # ax2.set_title('Разница на детальном участке')
    # ax2.set_xlabel(f'Индекс отсчета (смещение {start_index})')
    # ax2.set_ylabel('Разница')
    # ax2.grid(True)
    #
    # plt.tight_layout()
    # plt.show()

    # figure
    # data = observation.data
    # lhcp = data.lhcp
    # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    # plt.figure(figsize=(14, 8))
    # for freq_idx in range(lhcp.shape[0]):
    #     plt.plot(lhcp[freq_idx, :],
    #             alpha=0.5,
    #             linewidth = 1,
    #             marker = 'o',
    #             markersize = 2
    #     )
    # plt.grid(alpha=0.3)
    # plt.tight_layout()
    # plt.show()

@time_counter
def read_fits(fits_file: Path):

    try:
        with fits.open(fits_file) as hdul:
            print(hdul.info())
            primary_hdu = hdul[0]
            compressed_image_hdu = hdul[1]
            table_hdu = hdul[2]

            header = primary_hdu.header
            data_array = compressed_image_hdu.data
            table_data = table_hdu.data
    except FileNotFoundError:
        print(f"Fits file ''{fits_file}'' not found")
    except Exception as e:
        print(f"Error {e}")

    for card in header.cards:
        print(f"{card.keyword}  {card.value} // {card.comment}")

    column_names = table_data.columns.names
    print(column_names)
    frequencies = table_data['freq']
    # print(f"Frequencies: {frequencies}")
    if 'cal_p0' in table_hdu.columns.names:
        calibr_coeff_p0 = table_data['cal_p0']
        calibr_coeff_p1 = table_data['cal_p1']
        # print(f"Calibration coefficients: {calibr_coeff_p0}")
        # print(f"Calibration coefficients: {calibr_coeff_p1}")

    num_frequencies = header['NFREQS']
    num_samples = header['NSAMPLES']
    ref_time = header['REF_TIME']
    arcsec_per_second = header['ARCPSEC']
    az = header['AZIMUTH']
    az = f'{round(az):+d}'

    datetime_obs = header['CULM_FEE']
    datetime_obs = datetime.strptime(datetime_obs, '%Y-%m-%dT%H:%M:%S.%f%z')
    datatime_str = datetime_obs.strftime('%Y-%m-%d %H:%M:%S %Z')
    frequency_axis = np.linspace(config.freq_min, config.freq_max, num=num_frequencies, dtype=np.float64)

    time_axis = np.arange(num_samples) / config.samples_per_second
    arcsec_axis = - (time_axis - ref_time) * arcsec_per_second

    polarization = 0
    if polarization == 0:
        pol = "LHCP"
    if polarization == 1:
        pol = "RHCP"

    data = data_array[:,polarization,:]

    # построение спектрограммы
    # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    # fig, ax = plt.subplots()
    # # im = ax.pcolormesh(full_arcsec_scale, freq_selection, pol0_data_selection_calibrated,
    # #                    shading='gouraud', cmap='Spectral_r')
    # contour = ax.contourf(arcsec_axis, frequency_axis, data, levels=100,
    #                       cmap='Spectral_r')
    # ax.set_xlabel('x, arcsec')
    # ax.set_ylabel('Frequency, MHz')
    # ax.set_title(f"{datatime_str} Az {az}\nSpectrogram {pol}")
    # fig.colorbar(contour, ax=ax, label='s.f.u.')
    # #plt.show()

    #data_array[data_array == 2] = np.nan
    #data_array[data_array == 1] = np.nan


    # построение сканов
    # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    # plt.figure(figsize=(12, 7))
    # for freq_idx in range(data_array.shape[0]):
    #     plt.plot(arcsec_axis, data_array[freq_idx, polarization, :],
    #             alpha=0.5,
    #             linewidth = 1,
    #             marker = 'o',
    #             markersize = 2
    #     )
    # plt.grid(alpha=0.3)
    # plt.xlabel('x, arcsec')
    # plt.ylabel('flux, s.f.u.')
    # plt.title(f"{datatime_str} Az {az}\n{pol}")
    # plt.tight_layout()
    # plt.show()
    return data_array

def _get_output_fits_filename(observation: FastAcquisition1To3GHzObservation, fits_output_path: Path) -> Path:
    culm_efr = observation.metadata.datetime_culmination_efrat_utc
    year = culm_efr.year
    month_str = f"{culm_efr.month:02d}"
    obs_file = observation.metadata.obs_file
    base_filename = obs_file.name.split('.', 1)[0]
    output_fits_file = Path(fits_output_path / f"{year}" / month_str / f"{base_filename}.fits")
    return output_fits_file

def _print_header_params(observation: FastAcquisition1To3GHzObservation):
    metadata = observation.metadata
    print(f"Time start: {metadata.datetime_reg_start_utc}")
    print(f"Culmination Efrat: {metadata.datetime_culmination_efrat_utc}")
    print(f"Culmination horn: {metadata.datetime_culmination_feed_horn_utc}")
    print(f"Time stop: {metadata.datetime_reg_stop_utc}")
    print(f"Record duration, sec: {metadata.record_duration_seconds}")
    print(f"Time reduction factor: {metadata.time_reduction_factor}")
    print(f"Number of samples: {metadata.num_samples}")
    print(f"Samples per second: {metadata.samples_per_second}")
    print(f"Arcsec per second: {metadata.arcsec_per_second}")
    print(f"Arcsec per sample: {metadata.arcsec_per_sample}")
    print(f"Ref time: {metadata.ref_time}")
    print(
        f"До кульминации: {(metadata.datetime_culmination_feed_horn_utc - metadata.datetime_reg_start_utc).total_seconds()}")
    print(
        f"После кульминации: {(metadata.datetime_reg_stop_utc - metadata.datetime_culmination_feed_horn_utc).total_seconds()}")
    print(f"Ref sample {metadata.ref_sample}")
    print(f"arcsec L {- metadata.ref_sample * metadata.arcsec_per_sample}")
    print(
        f"arcsec last sample {metadata.num_samples * metadata.arcsec_per_sample - metadata.ref_sample * metadata.arcsec_per_sample}")
    print(f"time resolution: {metadata.time_resolution}")
    print(f"switch polarization time: {metadata.switch_polarization_time}")

    # print(f"До 1го импульса: {metadata.start_pulse_edge_time - metadata.datetime_reg_start_utc}")
    # print(f"От 1го импульса: {metadata.datetime_culmination_feed_horn_utc - metadata.start_pulse_edge_time}")
    # print(f"До 2го импульса: {metadata.stop_pulse_edge_time - metadata.datetime_culmination_feed_horn_utc}")
    # print(f"После 2го импульса: {metadata.datetime_reg_stop_utc - metadata.stop_pulse_edge_time}")