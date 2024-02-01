import os

from .apps.scheduler.celery import celery_app

# Default to using the packaged application settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keystone_api.main.settings')

# The celery application needs to be imported when Django starts
__all__ = ('celery_app', 'apps')
