#!/usr/bin/env bash

set -e

echo "Starting worker container..."
celery worker --app=apps.api.celery_app --concurrency=3 --scheduler django_celery_beat.schedulers:DatabaseScheduler --hostname=worker@%h --loglevel=INFO
