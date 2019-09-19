from django.conf.urls import url

from api.views import Image

urlpatterns = [
    url(r'^image/$', Image.as_view(), name='Image'),
]
