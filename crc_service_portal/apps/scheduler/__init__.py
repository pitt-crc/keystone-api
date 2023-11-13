from .celery import celery_app

# The `celery_app` variable must be discoverable by the Celery workers
__all__ = ['celery_app']
