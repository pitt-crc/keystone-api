"""Helper functions for streamlining common tasks.

Shortcuts are designed to simplify common tasks such as rendering templates,
redirecting URLs, issuing notifications, and handling HTTP responses.
"""

import logging

from apps.allocations.models import AllocationRequest
from apps.notifications.models import Notification
from apps.notifications.shortcuts import send_notification_template
from apps.users.models import User

log = logging.getLogger(__name__)


def send_notification_upcoming_expiration(user: User, request: AllocationRequest) -> None:
    """Send a notification to alert a user their allocation request will expire soon.

    Args:
        user: The user to notify.
        request: The allocation request to notify the user about.
    """

    log.info(f'Sending notification to user "{user.username}" on upcoming expiration for request {request.id}.')

    days_until_expire = request.get_days_until_expire()
    send_notification_template(
        user=user,
        subject=f'You have an allocation expiring on {request.expire}',
        template='upcoming_expiration_email.html',
        context={
            'user': user,
            'request': request,
            'days_to_expire': days_until_expire
        },
        notification_type=Notification.NotificationType.request_expiring,
        notification_metadata={
            'request_id': request.id,
            'days_to_expire': days_until_expire
        }
    )


def send_notification_past_expiration(user: User, request: AllocationRequest) -> None:
    """Send a notification to alert a user their allocation request has expired.

    Args:
        user: The user to notify.
        request: The allocation request to notify the user about.
    """

    log.info(f'Sending notification to user "{user.username}" on expiration of request {request.id}.')
    send_notification_template(
        user=user,
        subject='One of your allocations has expired',
        template='past_expiration_email.html',
        context={
            'user': user,
            'request': request
        },
        notification_type=Notification.NotificationType.request_expired,
        notification_metadata={
            'request_id': request.id
        }
    )
