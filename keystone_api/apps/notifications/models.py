"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from __future__ import annotations

from django.db import models
from django.conf import settings

from . import settings as appsettings


class Notification(models.Model):
    """User notification"""

    class NotificationType(models.TextChoices):
        resource_usage = 'RU', 'Resource Usage'
        request_status = 'SU', 'Status Update'
        general_message = 'GM', 'General Message'

    time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    message = models.TextField()
    metadata = models.JSONField(null=True)
    notification_type = models.CharField(max_length=2, choices=NotificationType.choices, default=NotificationType.general_message)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Preference(models.Model):
    """User notification preferences"""

    alloc_thresholds = models.JSONField(default=lambda: appsettings.NOTIFY_ALLOC_THRESHOLDS)
    notify_status_update = models.BooleanField(default=lambda: appsettings.NOTIFY_STATUS_UPDATE)
    expiry_thresholds = models.BooleanField(default=lambda: appsettings.NOTIFY_EXPIRY_THRESHOLDS)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @classmethod
    def get_user_preference(cls, user: settings.AUTH_USER_MODEL) -> Preference:
        """Retrieve user preferences or create them if they don't exist"""

        preference, created = cls.objects.get_or_create(user=user)
        return preference

    @classmethod
    def set_user_preference(cls, *args, **kwargs) -> None:
        """Set user preferences, creating or updating as necessary"""

        cls.objects.create(*args, **kwargs)