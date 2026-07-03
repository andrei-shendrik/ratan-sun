import os
from pathlib import Path

from celery import Celery
import logging.config
from celery.signals import setup_logging
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('ratan_backend')
# взять настройки из settings.py (все, что начинаются с CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

@setup_logging.connect
def config_loggers(*args, **kwargs):
    """
    запрет celery переопределять настройки логирования django
    принудительная загрузка словаря LOGGING из settings.py
    """
    logging.config.dictConfig(settings.LOGGING)

# поиск файлов tasks.py во всех приложениях
app.autodiscover_tasks()

# перенос расписания в корень проекта django (не триггерит watchdog)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
app.conf.beat_schedule_filename = str(BASE_DIR / 'celerybeat-schedule')

# расписание celery beat
app.conf.beat_schedule = {
    'sync-fast-acq-1-3ghz-raw': {
        'task': 'observations.tasks.fast_acquisition_1_3ghz.beat_fast_acq_1_3ghz_raw_to_db',
        'schedule': 60.0, # каждые 60 секунд
    },
    # 'dispatch-fast-acq-1-3ghz-jobs': {
    #     'task': 'observations.tasks.fast_acquisition_1_3ghz.beat_fast_acq_1_3ghz_dispatch_jobs',
    #     'schedule': 60.0, # каждые 60 секунд
    # },
}