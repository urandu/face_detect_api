from django.urls import path

from api.views import Image, HealthCheck

urlpatterns = [
    path('image/', Image.as_view(), name='Image'),
    path('health/', HealthCheck.as_view(), name='HealthCheck'),
]
