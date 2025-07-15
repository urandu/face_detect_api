#!/bin/bash
set -e

echo "Starting Celery worker in production mode..."

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

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ..."
while ! nc -z broker 5672; do
  echo "Waiting for RabbitMQ to be ready..."
  sleep 2
done
echo "RabbitMQ is ready!"

# Start Celery worker
echo "Starting Celery worker..."
exec celery -A api.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=1000 \
    --time-limit=300 \
    --soft-time-limit=240
