from rest_framework import serializers
from .models import FitsObservationFastAcquisition1To3GHzDB

class LatestObservationSerializer(serializers.ModelSerializer):
    # поле, чтобы отдать url для скачивания json
    json_url = serializers.SerializerMethodField()

    class Meta:
        model = FitsObservationFastAcquisition1To3GHzDB
        fields = ['id', 'datetime_culmination_feed_horn_utc', 'azimuth', 'observation_object', 'json_url']

    def get_json_url(self, obj):
        if not obj.json_path:
            return None
        # вернуть nginx'у
        return f"{obj.json_path}"