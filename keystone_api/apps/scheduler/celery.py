"""Application interface for the backend Celery service.

Defines a specially named `celery_app` variable which acts as the primary
interface between django and Celery. Celery tasks are automatically registered
with the Celery application instance for all applications defined in the
`settings.INSTALLED_APPS` list.
"""

from celery import Celery
from celery.schedules import crontab

celery_app = Celery("scheduler")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "Update LDAP users": {
        "task": "apps.users.tasks.ldap_update_users",
        "schedule": crontab(minute='0'),
    },
    "Rotate Log Entries": {
        "task": "apps.logging.tasks.rotate_log_files",
        "schedule": crontab(hour='0', minute='0'),
    }
}
