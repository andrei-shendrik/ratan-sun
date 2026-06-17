from django.contrib import admin
from .models import RawObservationFastAcquisition1To3GHzDB, FitsObservationFastAcquisition1To3GHzDB

@admin.register(RawObservationFastAcquisition1To3GHzDB)
class RawObservationFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    list_display = ('bin_filename', 'created_at', 'updated_at')
    list_filter = ('bin_filename', 'created_at')
    search_fields = ('bin_filename',)
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(FitsObservationFastAcquisition1To3GHzDB)
class FitsObservationFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    list_display = ('fits_filename', 'observation_object', 'azimuth', 'datetime_culmination_feed_horn_utc')
    list_filter = ('observation_object', 'datetime_culmination_feed_horn_utc')
    search_fields = ('fits_filename', 'raw_observation__bin_filename')
    readonly_fields = ('id', 'created_at', 'updated_at')