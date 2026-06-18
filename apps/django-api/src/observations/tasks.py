import os
from pathlib import Path
from celery import shared_task
from django.db import transaction
from django.db.models import F, Q
from .models import (
    ProcessingJobBin2FitsFastAcquisition1To3GHzDB,
    FitsObservationFastAcquisition1To3GHzDB
)


@shared_task
def process_fast_acquisition_1_3ghz_fits():
    """
    Фоновая задача. Поиск новых и обновленных fits файлов, созданных приложением bin2fits-fast-acq-1-3

    Ищет записи в таблице processing_job_bin2fits_fast_acquisition_1_3ghz, у которых:
     статус SUCCESS && (либо нет fits,
     либо время обновления в processing_job позже времени
     создания fits в таблице fits_observation_fast_acquisition_1_3ghz (fits был перезаписан)
    """

    jobs = ProcessingJobBin2FitsFastAcquisition1To3GHzDB.objects.filter(
        Q(raw_observation__fits_observation_fast_1_3__isnull=True) |
        Q(updated_at__gt=F('raw_observation__fits_observation_fast_1_3__created_at')),
        status='success'
    ).select_related('raw_observation')

    for job in jobs:
        raw = job.raw_observation
        try:
            with transaction.atomic():
                # --- ТУТ БУДЕТ ВЫЗОВ RATANPY ---
                fits_dir = os.environ.get('FAST_ACQ_1_3GHZ_FITS_ARCHIVE')
                fits_file_path = Path(fits_dir) / "2026" / "05" / raw.bin_filename.replace('.bin.gz', '.fits')
                fits_filename = raw.bin_filename.replace('.bin.gz', '.fits')
                # --- 3. Создаем/обновляем FITS-запись ---
                FitsObservationFastAcquisition1To3GHzDB.objects.update_or_create(
                    raw_observation=raw,
                    defaults={
                        'fits_path_filename': str(fits_file_path),
                        'fits_filename': fits_filename,
                        'telescope': 'RATAN-600',
                        'object_of_observation': 'sun',
                        'azimuth': 0.0,
                        'datetime_culmination_feed_horn_utc': job.updated_at,
                        'json_path': f"/data/products/web_json/sun/{fits_filename}.json"
                    }
                )
                print(f"Data Worker: Successfully processed FITS for {raw.bin_filename}")

        except Exception as e:
            print(f"Data Worker Error for {raw.bin_filename}: {e}")

    # targets = RawObservationFastAcquisition1To3GHzDB.objects.filter(
    #     Q(fits_data__isnull=True) | Q(updated_at__gt=F('fits_data__updated_at')),
    #     status='success'
    # )
    #
    # for raw in targets:
    #     try:
    #         with transaction.atomic():
    #             # 1. Здесь должен быть вызов ratanpy:
    #             # meta, l_data, r_data, freqs = extract_from_fits(raw.fits_path_filename)
    #
    #             # Заглушка метаданных:
    #             meta = {
    #                 'telescope': 'RATAN-600', 'target_object': 'Sun', 'azimuth': 0.0,
    #                 'datetime_obs': raw.updated_at, 'datetime_start': raw.updated_at, 'datetime_end': raw.updated_at,
    #                 'data_values': 'IV', 'pol_ch0': 'LHCP', 'pol_ch1': 'RHCP',
    #                 'num_samples': 1000, 'num_frequencies': 512, 'ref_time': 0.0, 'ref_sample': 0,
    #                 'start_pulse_edge_sample': 0, 'start_pulse_edge_time': 0.0, 'stop_pulse_edge_sample': 0,
    #                 'stop_pulse_edge_time': 0.0, 'samples_per_second': 100, 'arcsec_per_sample': 1.5,
    #                 'arcsec_per_second': 150, 'record_duration_seconds': 60, 'time_reduction_factor': 1,
    #                 'frequency_resolution': 1, 'time_resolution': 1, 'arcsec_resolution': 1,
    #                 'switch_polarization_time': 0, 'feed_horn_offset': 0, 'feed_horn_offset_time': 0,
    #                 'attenuator_common': 0, 'attenuator_1_2ghz': 0, 'attenuator_2_3ghz': 0,
    #                 'half_width_kurtosis_interval': 0, 'quiet_sun_point_arcsec': 0,
    #                 'data_receiver': 'Receiver', 'band': '1-3GHz', 'freq_min': 1000, 'freq_max': 3000
    #             }
    #
    #             # 2. Формируем путь к JSON
    #             # Читаем корень из .env: FAST_ACQ_1_3GHZ_JSON_DATA=/data/derived/json/web/ratan-600/fast-acquisition-1-3ghz/sun
    #             json_base_dir = os.environ.get('FAST_ACQ_1_3GHZ_JSON_DATA', '/tmp')
    #             # В идеале брать год/месяц из meta['datetime_obs']
    #             json_rel_path = f"2026/05/{raw.bin_filename}.json"
    #             json_full_path = Path(json_base_dir) / json_rel_path
    #
    #             # 3. Обновляем или создаем запись в таблице FITS (update_or_create!)
    #             fits_obs, created = FitsObservationFastAcquisition1To3GHzDB.objects.update_or_create(
    #                 raw_observation=raw,
    #                 defaults={
    #                     'fits_filename': raw.fits_filename or raw.bin_filename,
    #                     'fits_path_filename': raw.fits_path_filename or raw.bin_path_filename,
    #                     **meta,
    #                     'json_path': f"/data/json/{json_rel_path}"  # То, что пойдет во фронтенд
    #                 }
    #             )
    #
    #             # 4. Вызов даунсемплера:
    #             # ObservationDownsampler.process_and_save(l_data, r_data, freqs, meta, json_full_path)
    #
    #             print(f"Successfully processed {raw.bin_filename}")
    #
    #     except Exception as e:
    #         print(f"Error processing {raw.bin_filename}: {e}")