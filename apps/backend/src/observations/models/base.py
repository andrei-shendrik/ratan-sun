import uuid
import zoneinfo
from datetime import datetime
from pathlib import Path

from django.db import models
from django.db.models.functions import Now
from observations.enums import ProcessingJobStatus


# базовые абстракции
class AbstractObservation(models.Model):
    # общие поля
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    relative_path = models.CharField(max_length=500)
    filename = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now(), auto_now=True)

    class Meta:
        abstract = True # не создавать таблицу

    @property
    def observatory(self) -> str:
        raise NotImplementedError("Subclasses must define 'observatory' name")

    @property
    def telescope(self) -> str:
        raise NotImplementedError("Subclasses must define 'telescope' name")

    @property
    def instrument(self) -> str | None:
        return None

    @property
    def base_path(self) -> Path:
        """ базовая директория наблюдений """
        raise NotImplementedError("Subclasses must define 'base_path'")

    @property
    def absolute_path(self) -> Path:
        """ полный путь к файлу без имени файла """
        return self.base_path / self.relative_path

    @property
    def absolute_path_filename(self) -> Path:
        """ полный путь к файлу """
        return self.base_path / self.relative_path / self.filename

    @property
    def local_timezone(self) -> zoneinfo.ZoneInfo:
        raise NotImplementedError("Subclasses must define 'local_timezone'")

    @staticmethod
    def to_timezone(dt: datetime | None, target_tz: zoneinfo.ZoneInfo) -> datetime | None:
        """
        Конвертирует время в указанный часовой пояс
        """
        if dt is None:
            return None
        return dt.astimezone(target_tz)

    def as_local(self, dt: datetime | None) -> datetime | None:
        """
        Конвертирует время в локальное время обсерватории
        """
        return self.to_timezone(dt, self.local_timezone)

class AbstractRatanObservation(AbstractObservation):

    object_of_observation = models.CharField(null=True, blank=True, max_length=100, db_index=True)
    azimuth = models.FloatField(null=True, blank=True, db_index=True)

    obs_start_utc = models.DateTimeField(null=True, blank=True, db_index=True)
    datetime_obs_utc = models.DateTimeField(null=True, blank=True, db_index=True)
    obs_stop_utc = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    @property
    def data_receiver(self) -> str:
        raise NotImplementedError("Subclasses must define 'data_receiver' name")

    @property
    def band(self) -> str:
        raise NotImplementedError("Subclasses must define 'band' name")

    @property
    def local_timezone(self) -> zoneinfo.ZoneInfo:
        return zoneinfo.ZoneInfo("Europe/Moscow")

    @property
    def datetime_obs_local(self) -> datetime | None:
        return self.as_local(self.datetime_obs_utc)

    @property
    def obs_start_local(self) -> datetime | None:
        return self.as_local(self.obs_start_utc)

    @property
    def obs_stop_local(self) -> datetime | None:
        return self.as_local(self.obs_stop_utc)


class AbstractProcessingJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)

    status = models.CharField(
        max_length=20,
        choices=ProcessingJobStatus,
        default=ProcessingJobStatus.UNPROCESSED,
        db_index=True
    )
    comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now(), auto_now=True)

    class Meta:
        abstract = True

class AbstractVisualization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)

    json_relative_path = models.CharField(
        max_length=500,
        help_text="Relative path from *WEB_DATA root"
    )
    json_filename = models.CharField(max_length=255, unique=True)

    thumbnail_relative_path = models.CharField(
        max_length=500,
        help_text="Relative path from *WEB_DATA root"
    )
    thumbnail_filename = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now(), auto_now=True)

    class Meta:
        abstract = True

    @property
    def base_path(self) -> Path:
        """ базовая директория наблюдений """
        raise NotImplementedError("Subclasses must define 'base_path'")

    @property
    def json_absolute_path(self) -> Path:
        """ полный путь к файлу без имени файла """
        return self.base_path / self.json_relative_path

    @property
    def json_absolute_path_filename(self) -> Path:
        """ полный путь к файлу """
        return self.base_path / self.json_relative_path / self.json_filename

    @property
    def thumbnail_absolute_path(self) -> Path:
        """ полный путь к файлу без имени файла """
        return self.base_path / self.thumbnail_relative_path

    @property
    def thumbnail_absolute_path_filename(self) -> Path:
        """ полный путь к файлу """
        return self.base_path / self.thumbnail_relative_path / self.thumbnail_filename