import os
import uuid

from django.db import models


class Image(models.Model):
    image_id = models.CharField(max_length=100)
    image_array = models.TextField(null= True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="processing")
    callback_url = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
