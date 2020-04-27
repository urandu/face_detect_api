#!/usr/bin/env bash

set -e

echo "Starting worker container..."

celery worker --app=api.celery_app --concurrency=2 --hostname=worker@%h --loglevel=INFO
