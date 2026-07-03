from django.urls import path
from . import views

urlpatterns = [
    path('latest/', views.get_latest_observation, name='latest-observation'),
]