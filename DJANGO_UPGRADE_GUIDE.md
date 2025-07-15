# Django 5.0 Upgrade Guide

This document outlines the changes made to upgrade the Face Detection API from Django 2.2.28 to Django 5.0.7.

## Major Changes Made

### 1. Updated Dependencies (requirements.txt)
- **Django**: 2.2.28 → 5.0.7
- **djangorestframework**: 3.11.2 → 3.15.1
- **celery**: 4.2.0 → 5.3.4
- **Python**: Updated to 3.11 (in Dockerfile)
- Added **gunicorn**: 22.0.0 for WSGI server
- Updated all other dependencies to their latest compatible versions

### 2. URL Configuration Updates
- Replaced deprecated `django.conf.urls.url()` with `django.urls.path()` and `re_path()`
- Updated both main `urls.py` and API `urls.py` files
- Updated documentation references to Django 5.0

### 3. Settings Configuration
- Updated BASE_DIR to use `pathlib.Path` (Django 5.0 standard)
- Added `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`
- Removed deprecated `USE_L10N` setting
- Updated Celery configuration keys (lowercase format)
- Updated storage settings to use new `STORAGES` dictionary format

### 4. Celery Configuration
- Updated `api/celery_app.py` to use modern Celery configuration
- Changed from `app.conf.update()` to `app.config_from_object()`

### 5. Docker Configuration
- Updated base image from `python:3.7` to `python:3.11-slim`
- Improved package installation and cleanup
- Fixed gunicorn WSGI module reference

## Breaking Changes

### URL Patterns
**Before (Django 2.2):**
```python
from django.conf.urls import url
url(r'^api/', include('api.urls')),
```

**After (Django 5.0):**
```python
from django.urls import path, include
path('api/', include('api.urls')),
```

### Settings
**Before:**
```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
```

**After:**
```python
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STORAGES = {
    "default": {"BACKEND": "minio_storage.storage.MinioMediaStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
```

### Celery Configuration
**Before:**
```python
CELERY = {
    'BROKER_URL': os.getenv('CELERY_BROKER'),
    'CELERY_IMPORTS': ('api.tasks', ),
    # ...
}
```

**After:**
```python
CELERY = {
    'broker_url': os.getenv('CELERY_BROKER'),
    'imports': ('api.tasks', ),
    # ...
}
```

## Migration Instructions

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create and Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Check for Issues
```bash
python manage.py check
```

### 4. Test the Application
```bash
python manage.py runserver
```

### 5. Docker Deployment
```bash
docker-compose build
docker-compose up
```

## Compatibility Notes

### Python Version
- **Minimum**: Python 3.8
- **Recommended**: Python 3.11 (as used in Dockerfile)
- **Maximum**: Python 3.12

### Database
- PostgreSQL remains the same (compatible)
- No database schema changes required
- Existing data will be preserved

### Third-party Packages
- All major packages have been updated to compatible versions
- MTCNN, OpenCV, TensorFlow updated to latest versions
- MinIO storage updated to newer API

## Testing Checklist

After upgrade, verify:
- [ ] API endpoints respond correctly (`/api/image/`)
- [ ] Image upload functionality works
- [ ] Face detection processing completes
- [ ] Callback URLs receive results
- [ ] MinIO storage integration works
- [ ] Celery workers process tasks
- [ ] Admin interface is accessible
- [ ] Swagger/OpenAPI documentation loads

## Performance Improvements

Django 5.0 brings several performance improvements:
- Better async support
- Improved query optimization
- Enhanced static file handling
- Better memory usage

## Security Enhancements

- Updated dependencies address security vulnerabilities
- Django 5.0 includes the latest security fixes
- Better CSRF protection
- Enhanced middleware security

## Rollback Plan

If issues arise, you can rollback by:
1. Reverting to the previous requirements.txt
2. Restoring the old settings.py format
3. Rolling back URL configuration changes
4. Using the previous Docker image

Keep backups of:
- Database before migration
- requirements.txt (old version)
- settings.py (old version)
- Docker images (old version)
