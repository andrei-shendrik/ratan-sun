import logging

import numpy as np
from scipy.ndimage import gaussian_filter1d, median_filter, minimum_filter1d
from scipy.interpolate import PchipInterpolator

from ratanpy.ratan.fast_acquisition_1_3ghz.interpolators.fast_acquisition_1_3ghz_interpolator import \
    FastAcquisition1To3GHzInterpolator
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_observation import FastAcquisition1To3GHzObservation

logger = logging.getLogger(__name__)

from numba import njit


@njit(cache=True)
def pivot_mirrored_tile_numba(donor_vals, target_length):
    """
    @njit Numba Just-In-Time
    компилирует в машинный код c/с++

    паттерн создания шума для заполнения промежутков:
    берет донорский шум из соседнего участка (donor_vals): [A, B, C, D],
    отзеркаливает его: [D, C, B, A],
    растягивает на нужную длину (target_length) зацикливая (повторяя) гармошкой (зеркально/прямо)
    и избегает дублирования крайних точек: [D, C, B, A, B, C, D, ...]
    отрезает первую точку для приклеивания [C, B, A, B, C, D, ...] (чтобы не было двойных значений)
    возвращает результат

    склейка с данными будет такой: [A, B, C, D, C, B, A, B, C, D, ...]
    """
    n = len(donor_vals)
    out = np.empty(target_length, dtype=np.float64)
    # нет донора или донор из 1 точки
    if n == 0:
        for k in range(target_length): out[k] = 0.0
        return out
    if n == 1:
        for k in range(target_length): out[k] = donor_vals[0]
        return out

    # длина одного цикла (без дублирования крайних точек)
    cycle_len = 2 * n - 2
    cycle_vals = np.empty(cycle_len, dtype=np.float64)

    idx = 0
    # обратный ход (отзеркаливание) [C, B, A]
    for k in range(n - 2, -1, -1):
        cycle_vals[idx] = donor_vals[k]
        idx += 1
    # прямой ход: [B, C, D]
    for k in range(1, n):
        cycle_vals[idx] = donor_vals[k]
        idx += 1

    # заполняет итоговый массив, зацикливая паттерн с помощью остатка от деления (%)
    for k in range(target_length):
        out[k] = cycle_vals[k % cycle_len]
    return out

@njit(cache=True) # parallel=True
def fill_noise_fast(pure_noise, valid_mask, donor_size=50):
    """
    заполнение пропусков шумом
    Использует концепцию "Конечного автомата" (State Machine), чтобы на лету
    находить начала и концы пропусков любой длины за один проход по массиву.
    """
    num_channels, num_samples = pure_noise.shape
    borrowed_noise = np.full((num_channels, num_samples), np.nan, dtype=np.float64)

    # for i in prange(num_channels): # prange параллельно на всех ядрах процессора
    for i in range(num_channels): # range однопоточное выполнение
        # поиск индексов, где есть данные
        valid_indices = np.empty(num_samples, dtype=np.int32)
        v_count = 0
        for j in range(num_samples):
            if valid_mask[i, j]:
                valid_indices[v_count] = j
                v_count += 1

        if v_count == 0:
            continue

        # in_gap = True если движемся по интервалам пропусков данных
        in_gap = False
        gap_start = 0
        v_idx_at_start = 0 # индекс в массиве valid_indices перед началом пустоты
        current_v_idx = 0

        # прохождение от 0 до num_samples включительно, чтобы закрыть пропуск
        for j in range(num_samples + 1):
            is_valid = False if j == num_samples else valid_mask[i, j]

            # если наткнулись на пустоту и еще не в пустоте = это начало пустоты
            if not is_valid and not in_gap:
                in_gap = True
                gap_start = j
                v_idx_at_start = current_v_idx

            # если наткнулись на данные, когда были в пустоте = конец пустоты
            elif is_valid and in_gap:
                in_gap = False
                gap_end = j
                gap_len = gap_end - gap_start

                # определение положения в массиве валидных данных
                idx_start_pos = v_idx_at_start
                idx_end_pos = current_v_idx

                # проверка, есть ли данные слева и справа от пустоты для взятия доноров
                has_left = idx_start_pos > 0
                has_right = idx_end_pos < v_count

                left_donor = np.empty(0, dtype=np.float64)
                right_donor = np.empty(0, dtype=np.float64)
                right_n = 0

                """
                перекрестное заполнение интервала пустоты шумом:
                используются два донора, слева и справа от пустоты
                """
                # проверка, есть ли донор слева
                if has_left:
                    left_start = max(0, idx_start_pos - donor_size)
                    left_n = idx_start_pos - left_start
                    left_donor = np.empty(left_n, dtype=np.float64)
                    for k in range(left_n):
                        left_donor[k] = pure_noise[i, valid_indices[left_start + k]]
                # проверка, есть ли донор справа
                if has_right:
                    right_end = min(v_count, idx_end_pos + donor_size)
                    right_n = right_end - idx_end_pos
                    right_donor = np.empty(right_n, dtype=np.float64)
                    for k in range(right_n):
                        right_donor[k] = pure_noise[i, valid_indices[idx_end_pos + k]]

                # если есть оба донора:
                if has_left and has_right:
                    # расчет донорского шума для данных слева
                    left_fill = pivot_mirrored_tile_numba(left_donor, gap_len)

                    """
                    правого донора нужно развернуть задом наперед, чтобы заполнение
                    шло от границы данных справа налево в глубь пустоты
                    """
                    rd_rev = np.empty(right_n, dtype=np.float64)
                    for k in range(right_n): rd_rev[k] = right_donor[right_n - 1 - k]
                    # расчет донорского шума для данных справа
                    right_fill_tmp = pivot_mirrored_tile_numba(rd_rev, gap_len)

                    """
                    перекрестное заполнение:
                    смешивание шумов
                    
                    Constant-Power Crossfade
                    вес левого донора: w_left = cos(theta)
                    вес правого донора: w_right = sin(theta)
                    
                    theta на интервале пустоты меняется от 0 до pi/2
                    
                    sin^2(theta)+cos^2(theta)=1 мощность одинакова на всем интервале
                    """
                    theta = np.linspace(0, np.pi / 2, gap_len)
                    for k in range(gap_len):
                        w_left = np.cos(theta[k])
                        w_right = np.sin(theta[k])
                        right_val = right_fill_tmp[gap_len - 1 - k]
                        borrowed_noise[i, gap_start + k] = left_fill[k] * w_left + right_val * w_right

                # если донор только с одной стороны заполнение паттерном без смешивания
                elif has_left:
                    left_fill = pivot_mirrored_tile_numba(left_donor, gap_len)
                    for k in range(gap_len):
                        borrowed_noise[i, gap_start + k] = left_fill[k]

                elif has_right:
                    rd_rev = np.empty(right_n, dtype=np.float64)
                    for k in range(right_n): rd_rev[k] = right_donor[right_n - 1 - k]
                    right_fill_tmp = pivot_mirrored_tile_numba(rd_rev, gap_len)
                    for k in range(gap_len):
                        borrowed_noise[i, gap_start + k] = right_fill_tmp[gap_len - 1 - k]

            if is_valid:
                current_v_idx += 1

    return borrowed_noise

class FastAcquisition1To3GHzBorrowedNoiseInterpolator(FastAcquisition1To3GHzInterpolator):
    """
    интерполяция NaN значений шумом самой поляризации:
    вычисляется огибающая, из нее определяется тренд. Из значений вычитается тренд (остается чистый шум)
    определяется тренд для отсутствующих значений, к нему добавляется шум соседнего участка со значениями, со случайным сдвигом

    для поиска стандартного отклонения используется median absolute deviation (MAD), для устойчивости к импульсным помехам
    """

    def __init__(self, smoothing_sigma: float = 50.0, edge_trim_points: int = 3):
        self.smoothing_sigma = smoothing_sigma
        self.edge_trim_points = edge_trim_points

    def process(self, observation: FastAcquisition1To3GHzObservation) -> FastAcquisition1To3GHzObservation:

        observation.data.pol_channel1 = self._interpolate_channel_matrix(observation.data.pol_channel0)
        observation.data.pol_channel0 = self._interpolate_channel_matrix(observation.data.pol_channel1)

        return observation

    def _interpolate_channel_matrix(self, data_matrix: np.ndarray) -> np.ndarray:
        result_matrix = data_matrix.copy().astype(np.float64)

        # --- этап 1: создание маски ---
        # фильтр отрицательных значений
        result_matrix[result_matrix < 0] = np.nan

        # отсечение краев
        valid_mask = ~np.isnan(result_matrix)
        if self.edge_trim_points > 0:
            window_size = 2 * self.edge_trim_points + 1
            valid_mask = minimum_filter1d(valid_mask.view(np.int8), size=window_size, axis=1).astype(bool)
            result_matrix[~valid_mask] = np.nan

        nan_mask = ~valid_mask
        # отсечение пустых каналов
        nan_channels_mask = np.all(nan_mask, axis=1)

        num_channels, num_samples = result_matrix.shape
        x_indices = np.arange(num_samples)

        # --- этап 2: нахождение огибающей ---
        dense_data = np.zeros_like(result_matrix)

        for i in range(num_channels):
            if nan_channels_mask[i]:
                continue

            v_mask = valid_mask[i]
            x_valid = x_indices[v_mask]
            y_valid = result_matrix[i, v_mask]

            if len(x_valid) < 4:
                dense_data[i] = np.mean(y_valid) if len(y_valid) > 0 else 0
                continue

            # защита от помех
            y_valid_smooth = median_filter(y_valid, size=5)

            # защита краев для сплайна
            x_fit = x_valid.copy()
            y_fit = y_valid_smooth.copy()

            if x_fit[0] > 0:
                x_fit = np.insert(x_fit, 0, 0)
                y_fit = np.insert(y_fit, 0, y_fit[0])
            if x_fit[-1] < num_samples - 1:
                x_fit = np.append(x_fit, num_samples - 1)
                y_fit = np.append(y_fit, y_fit[-1])

            """
            интерполяция сплайном
            PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)
            """
            interpolator = PchipInterpolator(x_fit, y_fit, extrapolate=False)
            dense_data[i] = interpolator(x_indices)

        # --- этап 3: сглаживание сплайна гауссианой ---
        trend_matrix = gaussian_filter1d(dense_data, sigma=self.smoothing_sigma, axis=1)

        """
        альтернативный способ сглаживания:
        работает быстро, но прямоугольники сглаживает слишком сильно
        
        # пересчет sigma в ширину окна w. формула: w = sigma * sqrt(12)
        w = int(self.smoothing_sigma * 3.464) 
        if w < 1: w = 1
        
        # 3 прогона
        trend_matrix = uniform_filter1d(dense_data, size=w, axis=1)
        trend_matrix = uniform_filter1d(trend_matrix, size=w, axis=1)
        trend_matrix = uniform_filter1d(trend_matrix, size=w, axis=1)
        """

        # --- этап 4: извлечение шума (сигнал - огибающая) ---
        safe_result = np.nan_to_num(result_matrix, nan=0.0)
        pure_noise = safe_result - trend_matrix

        # --- этап 5: заполнение интервалом заимствованным шумом с соседних промежутков ---
        borrowed_noise = fill_noise_fast(pure_noise, valid_mask.astype(np.bool_))

        # --- этап 5: окончательный результат
        recovered_signal = trend_matrix + borrowed_noise
        final_matrix = np.where(nan_mask, recovered_signal, result_matrix)
        final_matrix[nan_channels_mask, :] = np.nan

        return final_matrix

    # def _get_crossfade_weights(self, length: int):
    #     if length not in self._crossfade_cache:
    #         theta = np.linspace(0, np.pi / 2, length)
    #         self._crossfade_cache[length] = (np.cos(theta), np.sin(theta))
    #     return self._crossfade_cache[length]
    #
    # def _pivot_mirrored_tile(self, donor: np.ndarray, target_length: int) -> np.ndarray:
    #     n = len(donor)
    #     if n == 0:
    #         return np.zeros(target_length)
    #     if n == 1:
    #         return np.full(target_length, donor[0])

    #     padded_mask = np.pad(nan_mask, pad_width=((0, 0), (1, 1)), mode='constant', constant_values=False)
    #     diffs = np.diff(padded_mask.astype(int), axis=1)
    #
    #     for i in range(num_channels):
    #         if nan_channels_mask[i]:
    #             continue
    #
    #         empty_starts = np.where(diffs[i] == 1)[0]
    #         empty_ends = np.where(diffs[i] == -1)[0]
    #
    #         valid_idx = np.where(~nan_mask[i])[0]
    #         if len(valid_idx) == 0:
    #             continue
    #
    #         for start, end in zip(empty_starts, empty_ends):
    #             gap_len = end - start
    #
    #             idx_start_pos = np.searchsorted(valid_idx, start)
    #             idx_end_pos = np.searchsorted(valid_idx, end)
    #
    #             has_left = idx_start_pos > 0
    #             has_right = idx_end_pos < len(valid_idx)
    #
    #             if has_left:
    #                 left_donor_idx = valid_idx[max(0, idx_start_pos - 50): idx_start_pos]
    #                 left_donor = pure_noise[i, left_donor_idx]
    #             else:
    #                 left_donor = np.array([])
    #
    #             if has_right:
    #                 right_donor_idx = valid_idx[idx_end_pos: min(len(valid_idx), idx_end_pos + 50)]
    #                 right_donor = pure_noise[i, right_donor_idx]
    #             else:
    #                 right_donor = np.array([])
    #
    #             if has_left and has_right:
    #                 left_fill = self._pivot_mirrored_tile(left_donor, gap_len)
    #                 right_fill = self._pivot_mirrored_tile(right_donor[::-1], gap_len)[::-1]
    #
    #                 w_left, w_right = self._get_crossfade_weights(gap_len)
    #                 borrowed_noise[i, start:end] = (left_fill * w_left) + (right_fill * w_right)
    #
    #             elif has_left:
    #                 borrowed_noise[i, start:end] = self._pivot_mirrored_tile(left_donor, gap_len)
    #             elif has_right:
    #                 borrowed_noise[i, start:end] = self._pivot_mirrored_tile(right_donor[::-1], gap_len)[::-1]
    #
    #     # =================================================================
    #     # ШАГ 4: ФИНАЛЬНАЯ СБОРКА
    #     # =================================================================
    #     recovered_signal = trend_matrix + borrowed_noise
    #     final_matrix = np.where(nan_mask, recovered_signal, result_matrix)
    #     final_matrix[nan_channels_mask, :] = np.nan
    #
    #     return final_matrix