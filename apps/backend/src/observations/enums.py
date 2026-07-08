from django.db import models


class ProcessingJobStatus(models.TextChoices):
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

class ObservationMode(models.TextChoices):
    """
    Режимы наблюдений

    Regular = обычное наблюдение
    Tracking = режим сопровождения активной области (диаграмма удерживается на определенной координате Солнца)
    Scanning = режим сканирования Солнца (кареткой сканируется Солнце)
    """
    REGULAR = 'regular', 'Regular'
    TRACKING = 'tracking', 'Tracking'
    SCANNING = 'scanning', 'Scanning'
    UNSPECIFIED = 'unspecified', 'Unspecified'