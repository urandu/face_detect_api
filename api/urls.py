from django.conf.urls import url

from api.views import Image

urlpatterns = [
    url(r'^new_image/$', Image.as_view(), name='Image'),
]
