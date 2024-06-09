from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models

from . import settings as appsettings


class Notification(models.Model):
    """User notification"""

    class NotificationType(models.TextChoices):
        resource_usage = 'RU', 'Resource Usage'
        request_status = 'SU', 'Status Update'

    time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    message = models.TextField()
    metadata = models.JSONField(null=True)
    notification_type = models.CharField(max_length=2, choices=NotificationType.choices)

    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Preference(models.Model):
    """User notification preferences"""

    alloc_thresholds = models.JSONField(default=appsettings.NOTIFY_ALLOC_THRESHOLDS)
    notify_status_update = models.BooleanField(default=appsettings.NOTIFY_STATUS_UPDATE)
    expiry_thresholds = models.BooleanField(default=appsettings.NOTIFY_EXPIRY_THRESHOLDS)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @classmethod
    def get_user_preference(cls, user: User) -> Preference:
        """Retrieve user preferences or create them if they don't exist"""

        preference, created = cls.objects.get_or_create(user=user)
        return preference

    @classmethod
    def set_user_preference(cls, *args, **kwargs) -> None:
        """Set user preferences, creating or updating as necessary"""

        cls.objects.create(*args, **kwargs)
