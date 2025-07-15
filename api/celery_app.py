import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_detect_api.settings')
app = Celery('face_detect_api')
app.config_from_object('django.conf:settings', namespace='CELERY')