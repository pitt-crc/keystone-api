"""Background tasks for issuing user notifications."""

import logging
from datetime import date, timedelta

from celery import shared_task

from apps.allocations.models import AllocationRequest
from apps.notifications.models import Notification, Preference
from apps.notifications.shortcuts import send_notification_template
from apps.users.models import User

log = logging.getLogger(__name__)


def should_notify_upcoming_expiration(user: User, request: AllocationRequest) -> bool:
    """Determine if a notification should be sent concerning an upcoming allocation expiration.

     Returns `True` if a notification is warranted by user preferences and
     an existing email has not already been sent.

    Args:
        user: The user to notify.
        request: The allocation request to notify the user about.

    Returns:
        A boolean reflecting whether to send a notification.
    """

    days_until_expire = request.get_days_until_expire()
    next_threshold = Preference.get_user_preference(user).get_next_expiration_threshold(days_until_expire)
    msg_prefix = f'Skipping notification on upcoming expiration for user "{user.username}" on request {request.id}: '

    # Check user notification preferences
    if next_threshold is None:
        log.debug(msg_prefix + 'No notification threshold has been hit yet.')
        return False

    # Avoid spamming new users
    if user.date_joined >= date.today() - timedelta(days=next_threshold):
        log.debug(msg_prefix + 'User account created after notification threshold.')
        return False

    # Check if a notification has already been sent
    if Notification.objects.filter(
        user=user,
        notification_type=Notification.NotificationType.request_expiring,
        metadata__request_id=request.id,
        metadata__days_to_expire__lte=next_threshold
    ).exists():
        log.debug(msg_prefix + 'Notification already sent for threshold.')
        return False

    return True


def send_notification_upcoming_expiration(user: User, request: AllocationRequest) -> None:
    """Send a notification to alert a user their allocation request will expire soon.

    Args:
        user: The user to notify.
        request: The allocation request to notify the user about.
    """

    log.debug(f'Sending notification to user "{user.username}" on upcoming expiration for request {request.id}.')

    days_until_expire = request.get_days_until_expire()
    send_notification_template(
        user=user,
        subject=f'Allocation Expires on {request.expire}',
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


@shared_task()
def notify_upcoming_expirations() -> None:
    """Send a notification to all users with soon-to-expire allocations."""

    active_requests = AllocationRequest.objects.filter(
        status=AllocationRequest.StatusChoices.APPROVED,
        expire__gt=date.today()
    ).all()

    failed = False
    for request in active_requests:
        for user in request.group.get_all_members().filter(is_active=True):
            try:
                if should_notify_upcoming_expiration(user, request):
                    send_notification_upcoming_expiration(user, request)

            except Exception as error:
                failed = True
                log.exception(
                    f'Error notifying user "{user.username}" on upcoming expiration of request {request.id}: {error}'
                )

    if failed:
        raise RuntimeError('Task failed with one or more errors. See logs for details.')


def should_notify_past_expiration(user: User, request: AllocationRequest) -> bool:
    """Determine if a notification should be sent concerning an upcoming expiration based on user preferences.

    Args:
        user: The user to notify
        request: The allocation request to notify the user about

    Returns:
        A boolean reflecting whether to send a notification.
    """

    # Check if a notification has already been sent
    if Notification.objects.filter(
        user=user,
        notification_type=Notification.NotificationType.request_expired,
        metadata__request_id=request.id,
    ).exists():
        log.debug(f'Skipping expiry notification for request {request.id} to user {user.username}: Notification already sent.')
        return False

    # Check user notification preferences
    return Preference.get_user_preference(user).notify_on_expiration


def send_notification_past_expiration(user: User, request: AllocationRequest) -> None:
    """Send a notification to alert a user their allocation request has expired.

    Args:
        user: The user to notify.
        request: The allocation request to notify the user about.
    """

    log.debug(f'Sending notification to user "{user.username}" on expiration of request {request.id}.')
    send_notification_template(
        user=user,
        subject=f'Your Allocation has Expired',
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


@shared_task()
def notify_past_expirations() -> None:
    """Send a notification to all users with expired allocations"""

    active_requests = AllocationRequest.objects.filter(
        status=AllocationRequest.StatusChoices.APPROVED,
        expire__lte=date.today(),
        expire__gt=date.today() - timedelta(days=3),
    ).all()

    failed = False
    for request in active_requests:
        for user in request.group.get_all_members().filter(is_active=True):

            try:
                if should_notify_past_expiration(request, user):
                    send_notification_past_expiration(user, request)

            except Exception as error:
                failed = True
                log.exception(
                    f'Error notifying user "{user.username}" on the expiration of request {request.id}: {error}'
                )

    if failed:
        raise RuntimeError('Task failed with one or more errors. See logs for details.')
