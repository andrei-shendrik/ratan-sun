from pathlib import Path

import matplotlib
import numpy as np
from matplotlib import pyplot as plt, cm

from obs_processor.fast_acquisition_1_3ghz_processing_director import FastAcquisition1To3GHzProcessingDirector
from ratanpy.ratan.polarization_type import PolarizationType


def draw_charts():
    fast_acquisition_bin_file = Path(
        r"D:\data\astro\obs\ratan-600\fast-acquisition-1-3ghz\raw\sun\2024\08\2024-08-01_121957_sun+00.bin.gz")

    director = FastAcquisition1To3GHzProcessingDirector()
    observation = director.run_standard_processing(fast_acquisition_bin_file)

    # which polarization draw
    pol = PolarizationType.LHCP

    # extract metadata
    arcsec_axis = observation.metadata.coordinate_axes.arcsec_axis
    frequency_axis = observation.metadata.coordinate_axes.frequency_axis
    datetime_obs = observation.metadata.datetime_culmination_feed_horn_utc
    datatime_str = datetime_obs.strftime('%Y-%m-%d %H:%M:%S %Z')
    az = observation.metadata.azimuth

    # extract data
    data = None
    if pol == PolarizationType.LHCP:
        data = observation.data.lhcp
    if pol == PolarizationType.RHCP:
        data = observation.data.rhcp
    if data is None:
        raise Exception("No data")

    frequencies = np.linspace(1000, 3000, data.shape[0])

    num_lines = 50
    target_indices = np.linspace(0, data.shape[0] - 1, num_lines, dtype=int)

    matplotlib.use('TkAgg')

    plt.figure(figsize=(12, 7))

    colors = cm.jet(np.linspace(0, 1, num_lines))
    for i, freq_idx in enumerate(target_indices):
        # Получаем точное значение частоты для легенды
        current_freq = frequencies[freq_idx]

        plt.plot(
            arcsec_axis,
            data[freq_idx, :],
            color=colors[i],  # Назначаем цвет из палитры
            alpha=0.7,  # Чуть больше прозрачности для наложения
            linewidth=1.5,
            # Убрал marker='o', см. примечание ниже!
            label=f"{current_freq:.1f} MHz"  # Текст для легенды
        )

    plt.grid(alpha=0.3)
    plt.xlabel('x, arcsec', fontsize=12)
    plt.ylabel('Flux, s.f.u.', fontsize=12)
    plt.title(f"{datatime_str} Az {az}\n{pol}", fontsize=14)

    # 3. Добавляем легенду
    # Выносим её за пределы графика вправо, чтобы она не перекрывала линии
    # plt.legend(title="Frequencies", bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.tight_layout()
    plt.show()

    # все частоты
    # # draw spectrogram
    # matplotlib.use('TkAgg')  # 'Qt5Agg', 'WxAgg'
    # fig, ax = plt.subplots()
    # contour = ax.contourf(arcsec_axis, frequency_axis, data, levels=100,
    #                       cmap='Spectral_r')
    # ax.set_xlabel('x, arcsec')
    # ax.set_ylabel('Frequency, MHz')
    # ax.set_title(f"{datatime_str} Az {az}\nSpectrogram {pol}")
    # fig.colorbar(contour, ax=ax, label='s.f.u.')
    # # plt.show()
    #
    # # draw multiple scans plot
    # plt.figure(figsize=(12, 7))
    # for freq_idx in range(data.shape[0]): # Member 'None' of 'Any | None' does not have attribute 'shape' Почему?
    #     plt.plot(arcsec_axis, data[freq_idx, :],
    #              alpha=0.5,
    #              linewidth=1,
    #              marker='o',
    #              markersize=2
    #              )
    # plt.grid(alpha=0.3)
    # plt.xlabel('x, arcsec')
    # plt.ylabel('flux, s.f.u.')
    # plt.title(f"{datatime_str} Az {az}\n{pol}")
    # plt.tight_layout()
    # plt.show()