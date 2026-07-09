from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilterBuilder

from .models import RawObservationFastAcquisition1To3GHz, FitsObservationFastAcquisition1To3GHz, \
    ProcessingJobBin2FitsFastAcquisition1To3GHz


@admin.register(RawObservationFastAcquisition1To3GHz)
class RawObservationFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime_obs_utc'

    list_display = ('filename', 'datetime_obs_utc', 'created_at', 'updated_at')
    list_filter = (
        # 'datetime_obs_utc',
        ('datetime_obs_utc', DateTimeRangeFilterBuilder(title="Observation date")),
        'created_at',
        'updated_at'
    )
    search_fields = ('filename',)
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(ProcessingJobBin2FitsFastAcquisition1To3GHz)
class ProcessingJobBin2FitsFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    # навигация по дате наблюдения
    date_hierarchy = 'raw_observation__datetime_obs_utc'

    list_display = (
        'get_raw_filename',
        'get_obs_datetime',
        'status',
        'comment',
        'get_fits_filename',
        'get_peak_memory_mb',
        'get_time_taken_sec',
        'min_free_ram_gb',
        'max_worker_ram_gb',
        'created_at'
    )

    list_filter = (
        # 'raw_observation__datetime_obs_utc'  # фильтр по дате наблюдения
        ("raw_observation__datetime_obs_utc", DateTimeRangeFilterBuilder(title="Observation date")),
        'status',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'status',
        'raw_observation__filename',  # поиск по сырому файлу
        'raw_observation__fits_observation__filename'  # поиск по fits файлу
    )
    readonly_fields = ('id', 'created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # SQL JOIN к таблице raw и транзитный JOIN к таблице fits
        return qs.select_related('raw_observation', 'raw_observation__fits_observation')

    # поля для отображения
    @admin.display(description='Raw Filename', ordering='raw_observation__filename')
    def get_raw_filename(self, obj):
        return obj.raw_observation.filename

    @admin.display(description='Obs Datetime (UTC)', ordering='raw_observation__datetime_obs_utc')
    def get_obs_datetime(self, obj):
        return obj.raw_observation.datetime_obs_utc

    @admin.display(description='Fits Filename')
    def get_fits_filename(self, obj):
        """
        проверка существования обратной связи OneToOneField (fits) перед обращением
        """
        if hasattr(obj.raw_observation, 'fits_observation'):
            return obj.raw_observation.fits_observation.filename
        return "—" # если файла нет


    @admin.display(description='Peak Memory (MB)', ordering='peak_memory_mb')
    def get_peak_memory_mb(self, obj):
        if obj.peak_memory_mb is not None:
            return f"{obj.peak_memory_mb:.2f}" # округление до 2 знаков
        return "—"

    @admin.display(description='Time Taken (sec)', ordering='time_taken_sec')
    def get_time_taken_sec(self, obj):
        if obj.time_taken_sec is not None:
            return f"{obj.time_taken_sec:.2f}"
        return "—"

@admin.register(FitsObservationFastAcquisition1To3GHz)
class FitsObservationFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime_obs_utc'

    list_display = (
        'filename',
        'datetime_obs_utc',
        'azimuth',
        'obs_mode',
        'data_values',
        'datetime_culmination_feed_horn_utc',
        'get_record_duration_seconds',
        'num_samples',
        'num_frequencies'
    )
    list_filter = (
        ('datetime_obs_utc', DateTimeRangeFilterBuilder(title="Observation date")),
        'object_of_observation',
        'created_at',
        'updated_at'
    )
    search_fields = ('filename', 'raw_observation__filename')
    readonly_fields = ('id', 'created_at', 'updated_at')

    @admin.display(description='Record Duration', ordering='record_duration_seconds')
    def get_record_duration_seconds(self, obj):
        if obj.record_duration_seconds is not None:
            minutes, seconds = divmod(obj.record_duration_seconds, 60)
            return f"{int(minutes)}m {seconds:.1f}s"
        return "—"