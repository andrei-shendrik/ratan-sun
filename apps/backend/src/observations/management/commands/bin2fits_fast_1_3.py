import sys
from datetime import datetime
from django.core.management.base import BaseCommand

from observations.enums import ProcessingJobStatus
from observations.models import RawObservationFastAcquisition1To3GHz, ProcessingJobBin2FitsFastAcquisition1To3GHz


class Command(BaseCommand):
    help = 'Ручной CLI сервера: Выбор файлов в БД и постановка их в очередь конвертации Celery'

    def add_arguments(self, parser):
        # 1. Точечные файлы
        parser.add_argument("--file", type=str, help="Convert chosen .bin file")
        # 2. Правила перезаписи
        parser.add_argument("--overwrite", action="store_true", help="Overwrite existing SUCCESS jobs")
        parser.add_argument("--failed", action="store_true", help="Include FAILED jobs")
        parser.add_argument("--only-failed", action="store_true", help="Process ONLY FAILED jobs")
        # 3. Фильтры по датам
        parser.add_argument("--start-date", type=str, help="YYYYMMDD")
        parser.add_argument("--end-date", type=str, help="YYYYMMDD")
        parser.add_argument("--day", type=str, help="YYYYMMDD")
        parser.add_argument("--month", type=str, help="YYYYMM")
        parser.add_argument("--year", type=int, help="YYYY")
        # 4. Переопределение ресурсов (для "тяжелых" дней)
        parser.add_argument("--min-free-ram-gb", type=float, help="Override settings")
        parser.add_argument("--max-worker-ram-gb", type=float, help="Override settings")

    def handle(self, *args, **options):
        # Если запущено без флагов - показываем Help и чисто выходим
        if not any(options[k] for k in
                   ['file', 'year', 'month', 'day', 'start_date', 'end_date', 'failed', 'only_failed', 'overwrite']):
            self.print_help('manage.py', 'bin2fits_fast_1_3')
            sys.exit(0)

        # Базовый QuerySet для поиска сырых файлов
        query = RawObservationFastAcquisition1To3GHz.objects.all()

        # --- ТРАНСЛЯЦИЯ ФЛАГОВ В SQL ФИЛЬТРЫ ---
        if options['file']:
            query = query.filter(bin_filename=options['file'])

        if options['year']:
            query = query.filter(datetime_obs_utc__year=options['year'])

        if options['month']:
            year, month = int(options['month'][:4]), int(options['month'][4:])
            query = query.filter(datetime_obs_utc__year=year, datetime_obs_utc__month=month)

        if options['day']:
            year, month, day = int(options['day'][:4]), int(options['day'][4:6]), int(options['day'][6:])
            query = query.filter(datetime_obs_utc__year=year, datetime_obs_utc__month=month, datetime_obs_utc__day=day)

        if options['start_date']:
            dt_start = datetime.strptime(options['start_date'], "%Y%m%d")
            query = query.filter(datetime_obs_utc__gte=dt_start)

        if options['end_date']:
            dt_end = datetime.strptime(options['end_date'], "%Y%m%d")
            query = query.filter(datetime_obs_utc__lte=dt_end)

        # Выбираем ID сырых файлов
        raw_ids = query.values_list('id', flat=True)

        # Находим соответствующие задачи в ProcessingJob
        jobs = ProcessingJobBin2FitsFastAcquisition1To3GHz.objects.filter(raw_observation_id__in=raw_ids)

        # --- ЛОГИКА ФИЛЬТРАЦИИ СТАТУСОВ ---
        if options['only_failed']:
            jobs = jobs.filter(status=ProcessingJobStatus.FAILED.value)
        else:
            if not options['failed']:
                jobs = jobs.exclude(status=ProcessingJobStatus.FAILED.value)
            if not options['overwrite']:
                jobs = jobs.exclude(status=ProcessingJobStatus.SUCCESS.value)

            # Защита: Никогда не трогаем те задачи, которые УЖЕ работают или ждут очереди
            jobs = jobs.exclude(status__in=[ProcessingJobStatus.PROCESSING.value, ProcessingJobStatus.UNPROCESSED.value])

        # --- ОБНОВЛЕНИЕ БАЗЫ ДАННЫХ (Перевод в UNPROCESSED) ---
        update_fields = {
            'status': ProcessingJobStatus.UNPROCESSED.value,
            'comment': None  # Сбрасываем старую ошибку
        }

        # Применяем переопределения RAM, если они переданы
        if options['min_free_ram_gb'] is not None:
            update_fields['override_min_ram_gb'] = options['min_free_ram_gb']
        if options['max_worker_ram_gb'] is not None:
            update_fields['override_max_ram_gb'] = options['max_worker_ram_gb']

        # Массовое обновление (Один SQL-запрос, мгновенная скорость)
        count = jobs.update(**update_fields)

        # Вывод результата
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'[{count}] jobs queued for Celery (Status -> UNPROCESSED).'))
        else:
            self.stdout.write(self.style.WARNING('No matching files found or all are already queued/success.'))