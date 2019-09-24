import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_detect_api.settings')
app = Celery()
app.conf.update(settings.CELERY)