"""Background tasks for issuing user notifications."""

import logging

from celery import shared_task
from django.utils import timezone

from apps.allocations.models import AllocationRequest
from apps.notifications.models import Notification, Preference
from apps.notifications.shortcuts import send_notification_template
from apps.users.models import User

log = logging.getLogger(__name__)

__all__ = ['send_notifications', 'send_expiry_notification']


def send_expiry_notification(user: User, request: AllocationRequest) -> None:
    """Send any pending expiration notices to the given user.

    A notification is only generated if warranted by the user's notification preferences.

    Args:
        user: The user to notify.
        request: The allocation request to check for pending notifications.
    """

    log.debug(f'Checking notifications for user {user.username} on request {request.id}.')

    # There are no notifications if the allocation does not expire
    days_until_expire = request.get_days_until_expire()
    if days_until_expire is None:
        log.debug(f'Request {request.id} does not expire')
        return

    elif days_until_expire <= 0:
        log.debug(f'Request {request.id} has already expired')
        return

    # Exit early if we have not hit a notification threshold yet
    next_threshold = Preference.get_user_preference(user).get_next_expiration_threshold(days_until_expire)
    log.debug(f'Request {request.id} expires in {days_until_expire} days. Next threshold at {next_threshold} days.')
    if next_threshold is None:
        return

    # Check if a notification has already been sent for the next threshold or any smaller threshold
    if Notification.objects.filter(
        user=user,
        notification_type=Notification.NotificationType.request_status,
        metadata__request_id=request.id,
        metadata__days_to_expire__lte=next_threshold
    ).exists():
        return

    log.debug(f'Sending new notification for request {request.id} to user {user.username}.')
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
def send_notifications() -> None:
    """Send any pending expiration notices to all users."""

    active_requests = AllocationRequest.objects.filter(
        status=AllocationRequest.StatusChoices.APPROVED,
        expire__gte=timezone.now()
    ).all()

    failed = False
    for request in active_requests:
        for user in request.group.get_all_members():

            try:
                send_expiry_notification(user, request)

            except Exception as error:
                log.exception(f'Error notifying user {user.username} for request {request.id}: {error}')
                failed = True

    if failed:
        raise RuntimeError('Task failed with one or more errors. See logs for details.')
