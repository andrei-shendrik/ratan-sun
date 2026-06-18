import uuid
from django.db import models
from django.db.models.functions import Now
from observations.enums import ProcessingStatus

# базовые абстракции
class AbstractObservation(models.Model):
    # общие поля
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path_filename = models.CharField(max_length=500, unique=True)
    filename = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now(), auto_now=True)

    class Meta:
        abstract = True

    @property
    def telescope(self) -> str:
        raise NotImplementedError("Subclasses must define telescope name")

class AbstractProcessingJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    status = models.CharField(max_length=20, choices=ProcessingStatus, default=ProcessingStatus.UNPROCESSED, db_index=True)
    comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now(), auto_now=True)

    class Meta:
        abstract = True