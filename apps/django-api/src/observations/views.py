from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FitsObservationFastAcquisition1To3GHzDB
from .serializers import LatestObservationSerializer


@api_view(['GET'])
def get_latest_observation(request):
    # последняя запись, у которой сгенерирован json
    latest_obs = FitsObservationFastAcquisition1To3GHzDB.objects.exclude(json_path__isnull=True).first()

    if not latest_obs:
        return Response({"error": "No observations found"}, status=404)

    target_date = latest_obs.datetime_culmination_feed_horn_utc.date()

    # поиск азимута 0 за этот же день
    azimuth_zero_obs = FitsObservationFastAcquisition1To3GHzDB.objects.filter(
        datetime_obs__date=target_date,
        azimuth=0.0
    ).exclude(json_path__isnull=True).first()

    # взять азимут 0, если нет, то последнее
    final_obs = azimuth_zero_obs if azimuth_zero_obs else latest_obs

    serializer = LatestObservationSerializer(final_obs)
    return Response(serializer.data)