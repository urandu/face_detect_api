import os
import uuid

from django.db import models

import settings


class Face(models.Model):
    image_id = models.CharField(max_length=100)
    face_id = models.CharField(max_length=100)
    confidence = models.CharField(max_length=200)
    box = models.TextField(null= True)
    keypoints = models.TextField(null= True)
    face_array = models.TextField(null= True)
    embedding = models.TextField(null= True)
    encoding = models.TextField(null= True)
    date_created = models.DateTimeField(auto_now_add=True)
