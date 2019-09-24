from django.conf.urls import url

from api.views import Image

urlpatterns = [
    url(r'^image/(?P<image_id>\w+)/$', Image.as_view(), name='Image'),
]
