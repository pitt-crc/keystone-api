"""Application interface for the backend Celery service.

Defines a specially named `celery_app` variable which acts as the primary
interface between django and Celery. Celery tasks are automatically registered
with the Celery application instance for all applications defined in the
`settings.INSTALLED_APPS` list.
"""

from celery import Celery

celery_app = Celery("scheduler")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
