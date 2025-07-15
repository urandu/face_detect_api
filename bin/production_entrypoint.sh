#!/bin/bash
set -e

echo "Starting Face Detection API in production mode..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z database 5432; do
  echo "Waiting for database to be ready..."
  sleep 2
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  echo "Waiting for Redis to be ready..."
  sleep 2
done
echo "Redis is ready!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create MinIO bucket if it doesn't exist
echo "Ensuring MinIO bucket exists..."
python -c "
import os
import sys
from minio import Minio
from minio.error import S3Error

try:
    client = Minio(
        os.environ.get('MINIO_ENDPOINT', 'minio:9000'),
        access_key=os.environ.get('MINIO_ACCESS_KEY'),
        secret_key=os.environ.get('MINIO_SECRET_KEY'),
        secure=False
    )
    bucket_name = 'django-media'
    
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f'Created bucket: {bucket_name}')
    else:
        print(f'Bucket {bucket_name} already exists')
        
except Exception as e:
    print(f'Warning: Could not ensure MinIO bucket exists: {e}')
    print('Continuing anyway...')
"

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 120 \
    --keep-alive 2 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    face_detect_api.wsgi:application
