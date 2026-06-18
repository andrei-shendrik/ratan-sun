from django.db import models


class ProcessingStatus(models.TextChoices):
    # переменная в коде = 'значение в бд', 'отображение в админке django'
    # в бд snake_case
    UNPROCESSED = 'unprocessed', 'Unprocessed'
    PROCESSING = 'processing', 'Processing'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'

class DataValues(models.TextChoices):
    LR = 'lr', 'LHCP, RHCP'
    IV = 'iv', 'Stokes I, Stokes V'

class PolarizationType(models.TextChoices):
    LHCP = 'lhcp', 'Left Hand Circular Polarization'
    RHCP = 'rhcp', 'Right Hand Circular Polarization'
    STOKES_I = 'stokes_i', 'Stokes I'
    STOKES_V = 'stokes_v', 'Stokes V'