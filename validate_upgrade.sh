#!/bin/bash

# Django 5.0 Upgrade Validation Script
# This script validates that the upgrade was successful

echo "🔍 Django 5.0 Upgrade Validation"
echo "================================="

# Check Python version
echo -e "\n📋 Checking Python version..."
python --version

# Check Django version
echo -e "\n📋 Checking Django version..."
python -c "import django; print(f'Django {django.get_version()}')"

# Check for Django 5.0 specific settings
echo -e "\n📋 Checking Django 5.0 settings..."
if grep -q "DEFAULT_AUTO_FIELD" face_detect_api/settings.py; then
    echo "✅ DEFAULT_AUTO_FIELD is configured"
else
    echo "❌ DEFAULT_AUTO_FIELD is missing"
fi

if grep -q "pathlib.Path" face_detect_api/settings.py; then
    echo "✅ BASE_DIR uses pathlib.Path"
else
    echo "❌ BASE_DIR not using pathlib.Path"
fi

# Check URL patterns
echo -e "\n📋 Checking URL patterns..."
if grep -q "from django.urls import path" face_detect_api/urls.py; then
    echo "✅ Main URLs using django.urls.path"
else
    echo "❌ Main URLs still using deprecated url()"
fi

if grep -q "from django.urls import path" api/urls.py; then
    echo "✅ API URLs using django.urls.path"
else
    echo "❌ API URLs still using deprecated url()"
fi

# Check Celery configuration
echo -e "\n📋 Checking Celery configuration..."
if grep -q "broker_url" face_detect_api/settings.py; then
    echo "✅ Celery using new configuration format"
else
    echo "❌ Celery still using old configuration format"
fi

# Check storage configuration
echo -e "\n📋 Checking storage configuration..."
if grep -q "STORAGES" face_detect_api/settings.py; then
    echo "✅ Using new STORAGES configuration"
else
    echo "❌ Still using deprecated DEFAULT_FILE_STORAGE"
fi

# Validate Django installation
echo -e "\n📋 Running Django system checks..."
if python manage.py check --deploy 2>/dev/null; then
    echo "✅ Django system checks passed"
else
    echo "❌ Django system checks failed"
fi

# Check for migrations
echo -e "\n📋 Checking migrations..."
if python manage.py showmigrations --plan | grep -q "UNAPPLIED"; then
    echo "⚠️  Unapplied migrations found. Run: python manage.py migrate"
else
    echo "✅ All migrations applied"
fi

# Test imports
echo -e "\n📋 Testing critical imports..."
python -c "
try:
    from django.urls import path, include, re_path
    print('✅ URL imports working')
except ImportError as e:
    print(f'❌ URL imports failed: {e}')

try:
    from rest_framework.views import APIView
    print('✅ DRF imports working')
except ImportError as e:
    print(f'❌ DRF imports failed: {e}')

try:
    from celery import Celery
    print('✅ Celery imports working')
except ImportError as e:
    print(f'❌ Celery imports failed: {e}')

try:
    from minio import Minio
    print('✅ MinIO imports working')
except ImportError as e:
    print(f'❌ MinIO imports failed: {e}')
"

echo -e "\n🎉 Validation complete!"
echo "If you see any ❌ issues above, please review the DJANGO_UPGRADE_GUIDE.md"
