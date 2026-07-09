from datetime import datetime
from pathlib import Path

from django.db import models

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.enums import DataValues, PolarizationType, ObservationMode
from observations.models.base import AbstractProcessingJob, AbstractRatanObservation, AbstractVisualization
from ratanpy.ratan.data_receiver import DataReceiver


# таблица сырых данных
class RawObservationFastAcquisition1To3GHz(AbstractRatanObservation):
    objects = models.Manager()

    class Meta:
        db_table = 'raw_observation_fast_acquisition_1_3ghz'
        ordering = ['-datetime_obs_utc']

        verbose_name = 'Raw observation FastAcquisition 1-3 GHz'
        verbose_name_plural = 'Raw observations FastAcquisition 1-3 GHz'

    @property
    def observatory(self) -> str:
        return "SAO RAS"

    @property
    def telescope(self) -> str:
        return "RATAN-600"

    @property
    def data_receiver(self) -> str:
        return DataReceiver.FAST_ACQUISITION_1_3GHZ.value #"Fast Acquisition 1-3 GHz"

    @property
    def band(self) -> str:
        return "1-3 GHz"

    @property
    def base_path(self) -> Path:
        return Path(FastAcquisition1To3GHzSettings.load().bin_archive)

    def __str__(self):
        return self.filename

# таблица обработки сырых данных в fits
class ProcessingJobBin2FitsFastAcquisition1To3GHz(AbstractProcessingJob):
    objects = models.Manager()

    peak_memory_mb = models.FloatField(null=True, blank=True, db_index=True)
    time_taken_sec = models.FloatField(null=True, blank=True, db_index=True)
    min_free_ram_gb = models.FloatField(null=True, blank=True, help_text="Override .env value")
    max_worker_ram_gb = models.FloatField(null=True, blank=True, help_text="Override .env value")

    # внешний ключ
    raw_observation = models.OneToOneField(
        RawObservationFastAcquisition1To3GHz,
        on_delete=models.CASCADE, # при удалении записи сырых данных будет удалена запись в processing_job
        related_name='job_bin2fits'  # позволяет обратиться raw.job_bin2fits.status
    )

    class Meta:
        db_table = 'processing_job_bin2fits_fast_acquisition_1_3ghz'
        verbose_name = 'Processing Job Bin2Fits FastAcquisition 1-3 GHz'
        verbose_name_plural = 'Processing Jobs Bin2Fits FastAcquisition 1-3 GHz'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Job for {self.raw_observation.filename} [{self.status}]"

# таблица обработанных данных
class FitsObservationFastAcquisition1To3GHz(AbstractRatanObservation):
    objects = models.Manager()

    # внешний ключ
    # каждому raw соответствует только один fits
    raw_observation = models.OneToOneField(
        RawObservationFastAcquisition1To3GHz,
        on_delete=models.CASCADE, # при удалении сырых будет удален fits
        related_name='fits_observation'
    )

    datetime_culmination_efrat_utc = models.DateTimeField(null=True, blank=True, db_index=True)
    datetime_culmination_feed_horn_utc = models.DateTimeField(null=True, blank=True, db_index=True) # db_index=True для поиска последнего наблюдения

    obs_mode = models.CharField(null=True, blank=True, max_length=20, choices=ObservationMode)

    altitude = models.FloatField(null=True, blank=True)
    declination = models.FloatField(null=True, blank=True)
    right_ascension = models.FloatField(null=True, blank=True)
    solar_r = models.FloatField(null=True, blank=True)
    solar_p = models.FloatField(null=True, blank=True)
    solar_b = models.FloatField(null=True, blank=True)
    scan_angle = models.FloatField(null=True, blank=True)

    data_values = models.CharField(null=True, blank=True, max_length=2, choices=DataValues)
    pol_chan0 = models.CharField(null=True, blank=True, max_length=10, choices=PolarizationType)
    pol_chan1 = models.CharField(null=True, blank=True, max_length=10, choices=PolarizationType)

    num_samples = models.IntegerField(null=True, blank=True)
    num_frequencies = models.IntegerField(null=True, blank=True)
    ref_time = models.FloatField(null=True, blank=True, help_text="seconds from the start of registration")
    ref_sample = models.IntegerField(null=True, blank=True)

    samples_per_second = models.FloatField(null=True, blank=True)
    arcsec_per_sample = models.FloatField(null=True, blank=True)
    arcsec_per_second = models.FloatField(null=True, blank=True)

    record_duration_seconds = models.FloatField(null=True, blank=True)

    time_reduction_factor = models.FloatField(null=True, blank=True)
    frequency_resolution = models.FloatField(null=True, blank=True)
    time_resolution = models.FloatField(null=True, blank=True)
    arcsec_resolution = models.FloatField(null=True, blank=True)
    switch_polarization_time = models.FloatField(null=True, blank=True)

    feed_horn_offset = models.FloatField(null=True, blank=True)
    feed_horn_offset_time = models.FloatField(null=True, blank=True)

    attenuator_common = models.FloatField(null=True, blank=True)
    attenuator_1_2ghz = models.FloatField(null=True, blank=True)
    attenuator_2_3ghz = models.FloatField(null=True, blank=True)

    half_width_kurtosis_interval = models.FloatField(null=True, blank=True)

    is_bad = models.BooleanField(null=True, blank=True, default=False)
    is_calibrated = models.BooleanField(null=True, blank=True, default=False)
    unit = models.CharField(null=True, blank=True, max_length=50)
    quiet_sun_point_arcsec = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'fits_observation_fast_acquisition_1_3ghz'
        ordering = ['-datetime_culmination_feed_horn_utc']

        verbose_name = 'Fits observation FastAcquisition 1-3 GHz'
        verbose_name_plural = 'Fits observations FastAcquisition 1-3 GHz'

    @property
    def telescope(self) -> str:
        return "RATAN-600"

    @property
    def data_receiver(self) -> str:
        return DataReceiver.FAST_ACQUISITION_1_3GHZ.value #"Fast Acquisition 1-3 GHz"

    @property
    def band(self) -> str:
        return "1-3 GHz"

    @property
    def base_path(self) -> Path:
        return Path(FastAcquisition1To3GHzSettings.load().fits_archive)

    @property
    def freq_min_mhz (self) -> float:
        return 1000

    @property
    def freq_max_mhz(self) -> float:
        return 3000

    @property
    def datetime_culmination_efrat_local(self) -> datetime | None:
        return self.as_local(self.datetime_culmination_efrat_utc)

    @property
    def datetime_culmination_feed_horn_local(self) -> datetime | None:
        return self.as_local(self.datetime_culmination_feed_horn_utc)

    def __str__(self):
        return self.filename

class VisualizationFitsFastAcquisition1To3GHz(AbstractVisualization):
    objects = models.Manager()

    fits_observation = models.OneToOneField(
        FitsObservationFastAcquisition1To3GHz,
        on_delete=models.CASCADE,
        related_name='visualization_fits'
    )

    spectrogram_num_freqs = models.IntegerField()
    spectrogram_num_samples = models.IntegerField()
    scan_group_num_freqs = models.IntegerField()
    scan_group_num_samples = models.IntegerField()

    class Meta:
        db_table = 'visualization_fits_fast_acquisition_1_3ghz'
        ordering = ['-updated_at']

        verbose_name = 'Visualization Fits FastAcquisition 1-3 GHz'
        verbose_name_plural = 'Visualization Fits FastAcquisition 1-3 GHz'

    @property
    def base_path(self) -> Path:
        return Path(FastAcquisition1To3GHzSettings.load().fits_web_data)