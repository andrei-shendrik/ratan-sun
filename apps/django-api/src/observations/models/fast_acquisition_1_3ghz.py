import uuid

from django.db import models

from observations.enums import ProcessingStatus, DataValues, PolarizationType
from observations.models.base import AbstractObservation, AbstractProcessingJob


# таблица сырых данных
class RawObservationFastAcquisition1To3GHzDB(AbstractObservation):
    objects = models.Manager()

    object_of_observation = models.CharField(null=True, max_length=100, db_index=True)
    azimuth = models.FloatField(null=True, db_index=True)

    datetime_obs_local = models.DateTimeField(null=True, blank=True, db_index=True)
    datetime_obs_utc = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'raw_observation_fast_acquisition_1_3ghz'
        ordering = ['-datetime_obs_local']

        verbose_name = 'Raw observation FastAcquisition 1-3GHz'
        verbose_name_plural = 'Raw observations FastAcquisition 1-3GHz'

    @property
    def telescope(self) -> str:
        return "RATAN-600"

    def __str__(self):
        return self.filename

# таблица обработки сырых данных в fits
class ProcessingJobBin2FitsFastAcquisition1To3GHzDB(AbstractProcessingJob):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    peak_memory_mb = models.FloatField(null=True, blank=True)
    time_taken_sec = models.FloatField(null=True, blank=True)
    min_free_ram_gb = models.FloatField(null=True, blank=True, help_text="Override .env value")
    max_worker_ram_gb = models.FloatField(null=True, blank=True, help_text="Override .env value")

    # каждому файлу сырых данных может единственная запись обработки
    raw_observation = models.OneToOneField(
        RawObservationFastAcquisition1To3GHzDB,
        on_delete=models.CASCADE,
        related_name='processing_job_bin2fits_fast_1_3'  # позволяет обратиться raw.processing_job_bin2fits_fast_1_3.status
    )

    status = models.CharField(
        max_length=20,
        choices=ProcessingStatus,
        default=ProcessingStatus.UNPROCESSED,
        db_index=True
    )
    comment = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'processing_job_bin2fits_fast_acquisition_1_3ghz'
        verbose_name = 'Processing Job Bin2Fits FastAcquisition 1-3GHz'
        verbose_name_plural = 'Processing Jobs Bin2Fits FastAcquisition 1-3GHz'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Job for {self.raw_observation.filename} [{self.status}]"

# таблица обработанных данных
class FitsObservationFastAcquisition1To3GHzDB(AbstractObservation):
    objects = models.Manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # каждому raw соответствует только один fits
    raw_observation = models.OneToOneField(
        RawObservationFastAcquisition1To3GHzDB,
        on_delete=models.CASCADE,
        related_name='fits_observation_fast_1_3'
    )

    object_of_observation = models.CharField(null=True, max_length=100, db_index=True)
    azimuth = models.FloatField(null=True, db_index=True)

    datetime_obs_local = models.DateTimeField(null=True, blank=True, db_index=True)
    datetime_obs_utc = models.DateTimeField(null=True, blank=True, db_index=True)

    datetime_reg_start_utc = models.DateTimeField()
    datetime_reg_start_local = models.DateTimeField()

    datetime_culmination_efrat_utc = models.DateTimeField()
    datetime_culmination_efrat_local = models.DateTimeField()

    datetime_culmination_feed_horn_utc = models.DateTimeField(db_index=True) # db_index=True для поиска последнего наблюдения
    datetime_culmination_feed_horn_local = models.DateTimeField()

    datetime_reg_stop_utc = models.DateTimeField()
    datetime_reg_stop_local = models.DateTimeField()

    altitude = models.FloatField()
    declination = models.FloatField()
    right_ascension = models.FloatField()
    solar_radius = models.FloatField()
    solar_position_angle = models.FloatField()
    solar_b_angle = models.FloatField()

    data_values = models.CharField(max_length=2, choices=DataValues)
    pol_ch0 = models.CharField(max_length=10, choices=PolarizationType)
    pol_ch1 = models.CharField(max_length=10, choices=PolarizationType)

    num_samples = models.IntegerField()
    num_frequencies = models.IntegerField()
    ref_time = models.FloatField(help_text="seconds from the start of registration")
    ref_sample = models.IntegerField()
    start_pulse_edge_sample = models.IntegerField()
    start_pulse_edge_time = models.FloatField()
    stop_pulse_edge_sample = models.IntegerField()
    stop_pulse_edge_time = models.FloatField()

    samples_per_second = models.FloatField()
    arcsec_per_sample = models.FloatField()
    arcsec_per_second = models.FloatField()

    record_duration_seconds = models.FloatField()

    time_reduction_factor = models.FloatField()
    frequency_resolution = models.FloatField()
    time_resolution = models.FloatField()
    arcsec_resolution = models.FloatField()
    switch_polarization_time = models.FloatField()

    feed_horn_offset = models.FloatField()
    feed_horn_offset_time = models.FloatField()

    attenuator_common = models.FloatField()
    attenuator_1_2ghz = models.FloatField()
    attenuator_2_3ghz = models.FloatField()

    half_width_kurtosis_interval = models.FloatField()

    is_bad = models.BooleanField(default=False)
    is_calibrated = models.BooleanField(default=False)
    unit = models.CharField(max_length=50)
    quiet_sun_point_arcsec = models.FloatField()

    data_receiver = models.CharField(max_length=100)
    band = models.CharField(max_length=100)
    freq_min = models.FloatField()
    freq_max = models.FloatField()

    json_path = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'fits_observation_fast_acquisition_1_3ghz'
        ordering = ['-datetime_culmination_feed_horn_utc']

        verbose_name = 'Fits observation FastAcquisition 1-3GHz'
        verbose_name_plural = 'Fits observations FastAcquisition 1-3GHz'

    @property
    def telescope(self) -> str:
        return "RATAN-600"

    def __str__(self):
        return self.filename