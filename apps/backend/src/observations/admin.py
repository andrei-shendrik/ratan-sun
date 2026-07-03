from django.contrib import admin
from .models import RawObservationFastAcquisition1To3GHz, FitsObservationFastAcquisition1To3GHz

@admin.register(RawObservationFastAcquisition1To3GHz)
class RawObservationFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    list_display = ('filename', 'created_at', 'updated_at')
    list_filter = ('filename', 'created_at')
    search_fields = ('filename',)
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(FitsObservationFastAcquisition1To3GHz)
class FitsObservationFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    list_display = ('filename', 'object_of_observation', 'azimuth', 'datetime_culmination_feed_horn_utc')
    list_filter = ('object_of_observation', 'datetime_culmination_feed_horn_utc')
    search_fields = ('filename', 'raw_observation__filename')
    readonly_fields = ('id', 'created_at', 'updated_at')