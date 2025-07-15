#!/usr/bin/env bash

set -e

echo "Starting worker container..."

celery --app=api.celery_app worker --concurrency=2 --hostname=worker@%h --loglevel=INFO
