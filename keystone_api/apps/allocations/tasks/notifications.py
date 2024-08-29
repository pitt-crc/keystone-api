"""Background tasks for issuing user notifications."""

import logging
from datetime import date, timedelta

from celery import shared_task
from django.utils import timezone

from apps.allocations.models import AllocationRequest
from apps.notifications.models import Notification, Preference
from apps.notifications.shortcuts import send_notification_template
from apps.users.models import User

log = logging.getLogger(__name__)

__all__ = ['send_expiry_notifications', 'send_expiry_notification_for_request']


def send_expiry_notification_for_request(user: User, request: AllocationRequest) -> None:
    """Send any pending expiration notices to the given user.

    A notification is only generated if warranted by the user's notification preferences.

    Args:
        user: The user to notify.
        request: The allocation request to check for pending notifications.
    """

    # There are no notifications if the allocation does not expire
    log.debug(f'Checking notifications for user {user.username} on request #{request.id}.')
    if not request.expire:
        log.debug('Request does not expire')
        return

    # The next notification occurs at the smallest threshold that is greater than or equal the days until expiration
    days_until_expire = (request.expire - date.today()).days
    notification_thresholds = Preference.get_user_preference(user).expiry_thresholds
    next_threshold = min(
        filter(lambda x: x >= days_until_expire, notification_thresholds),
        default=None
    )

    # Exit early if we have not hit a threshold yet
    log.debug(f'Request #{request.id} expires in {days_until_expire} days. Next threshold at {next_threshold} days.')
    if next_threshold is None:
        return

    # Check if a notification has already been sent
    notification_sent = Notification.objects.filter(
        user=user,
        notification_type=Notification.NotificationType.request_status,
        metadata__request_id=request.id,
        metadata__days_to_expire__lte=next_threshold
    ).exists()

    if notification_sent:
        log.debug(f'Existing notification found.')
        return

    log.debug(f'Sending new notification for request #{request.id} to user {user.username}.')
    send_notification_template(
        user=user,
        subject=f'Allocation Expires on {request.expire}',
        template='expiration_email.html',
        context={
            'user': user,
            'request': request,
            'days_to_expire': days_until_expire
        },
        notification_type=Notification.NotificationType.request_status,
        notification_metadata={
            'request_id': request.id,
            'days_to_expire': days_until_expire
        }
    )


@shared_task()
def send_expiry_notifications() -> None:
    """Send any pending expiration notices to all users."""

    expiring_requests = AllocationRequest.objects.filter(
        status=AllocationRequest.StatusChoices.APPROVED,
        expire__gte=timezone.now() - timedelta(days=7)
    ).all()

    failed = False
    for request in expiring_requests:
        for user in request.group.get_all_members():

            try:
                send_expiry_notification_for_request(user, request)

            except Exception as error:
                log.exception(f'Error notifying user {user.username} for request #{request.id}: {error}')
                failed = True

    if failed:
        raise RuntimeError('Task failed with one or more errors. See logs for details.')
