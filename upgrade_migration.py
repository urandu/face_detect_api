#!/usr/bin/env python
"""
Django 5.0 Upgrade Migration Script

This script helps with the Django upgrade process by:
1. Creating new migrations for BigAutoField
2. Running the migration
3. Validating the upgrade
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_detect_api.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    print("Django 5.0 Upgrade Migration Script")
    print("===================================")
    
    print("\n1. Creating new migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    print("\n2. Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("\n3. Checking for issues...")
    execute_from_command_line(['manage.py', 'check'])
    
    print("\nUpgrade completed successfully!")
    print("\nNOTE: Make sure to:")
    print("- Test all functionality thoroughly")
    print("- Update any third-party packages")
    print("- Check for deprecated features")
