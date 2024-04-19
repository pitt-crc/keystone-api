"""Application configuration and initialization logic.

Subclasses of the Django `AppConfig` class are automatically loaded by Django
and used to initialize the parent application. This includes encapsulating
startup tasks and configuring how the application integrates with the framework.
"""

from django.apps import AppConfig
from django.core.checks import register

from .checks import *


class SchedulerConfig(AppConfig):
    """Configure the parent application"""

    name = 'apps.scheduler'

    def ready(self):
        """Executed as soon as the Django application registry is fully populated."""

        register(check_celery_is_importable)
