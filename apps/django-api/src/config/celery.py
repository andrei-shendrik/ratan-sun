import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('ratan_backend')
# взять настройки из settings.py (все, что начинаются с CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')
# поиск файлов tasks.py во всех приложениях
app.autodiscover_tasks()

# добавление расписания
app.conf.beat_schedule = {
    'check-fits-every-10-seconds': {
        'task': 'observations.tasks.process_fast_acquisition_1_3ghz_fits',
        'schedule': 10.0, # запуск каждые 10 секунд
    },
}