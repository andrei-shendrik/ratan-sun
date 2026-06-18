from django.contrib import admin
from .models import RawObservationFastAcquisition1To3GHzDB, FitsObservationFastAcquisition1To3GHzDB

@admin.register(RawObservationFastAcquisition1To3GHzDB)
class RawObservationFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    list_display = ('filename', 'created_at', 'updated_at')
    list_filter = ('filename', 'created_at')
    search_fields = ('filename',)
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(FitsObservationFastAcquisition1To3GHzDB)
class FitsObservationFastAcquisition1To3GHzAdmin(admin.ModelAdmin):
    list_display = ('filename', 'object_of_observation', 'azimuth', 'datetime_culmination_feed_horn_utc')
    list_filter = ('object_of_observation', 'datetime_culmination_feed_horn_utc')
    search_fields = ('filename', 'raw_observation__filename')
    readonly_fields = ('id', 'created_at', 'updated_at')