import sys

from django.apps import AppConfig
from django.db import connection
from django.db.models.signals import post_migrate

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings


def create_updated_at_triggers(sender, **kwargs):
    """
    Создание триггера для обновления поля updated_at.
    Добавляет триггер на все таблицы приложения где есть такое поле.
    Запускается после создания всех таблиц при команде migrate
    """
    models = sender.get_models()

    with connection.cursor() as cursor:
        cursor.execute("""
                       CREATE
                       OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
                       BEGIN
                NEW.updated_at
                       = NOW();
                       RETURN NEW;
                       END;
            $$
                       language 'plpgsql';
                       """)

        for model in models:
            field_names = [field.name for field in model._meta.local_fields]

            # if hasattr(model, 'updated_at'):
            if 'updated_at' in field_names:
                table_name = model._meta.db_table
                trigger_name = f"trg_update_modtime_{table_name}"

                cursor.execute(f"""
                    DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};

                    CREATE TRIGGER {trigger_name}
                    BEFORE UPDATE ON {table_name}
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                """)

class ObservationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'observations'

    def ready(self):
        # подключение функции к сигналу успешной миграции
        post_migrate.connect(create_updated_at_triggers, sender=self)

        # инициализация настроек быстрого сбора 1-3 ГГц
        try:
            FastAcquisition1To3GHzSettings.load()
        except Exception as e:
            sys.stderr.write(f"FATAL: Missing configuration for FastAcquisition1To3GHz settings: {e}\n")
            sys.exit(1)
