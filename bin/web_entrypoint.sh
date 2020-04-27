#!/usr/bin/env bash

set -e

echo "Making migrations ..."
python manage.py makemigrations

echo "Collect static files ..."
#python manage.py collectstatic

echo "Applying migrations ..."
python manage.py migrate

echo "Starting web container..."
python manage.py runserver 0.0.0.0:8000
