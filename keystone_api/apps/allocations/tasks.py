"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

from datetime import date, timedelta

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.allocations.models import Allocation, AllocationRequest, Cluster
from apps.notifications.models import Notification, Preference
from apps.notifications.shortcuts import send_notification_template
from apps.users.models import ResearchGroup, User
from keystone_api.plugins.slurm import *

log = logging.getLogger(__name__)


@shared_task()
def update_limits() -> None:
    """Adjust TRES billing limits for all Slurm accounts on all enabled clusters"""

    for cluster in Cluster.objects.filter(enabled=True).all():
        update_limits_for_cluster(cluster)


@shared_task()
def update_limits_for_cluster(cluster: Cluster) -> None:
    """Adjust TRES billing limits for all Slurm accounts on a given Slurm cluster

    The Slurm accounts for `root` and any that are missing from Keystone are automatically ignored.

    Args:
        cluster: The name of the Slurm cluster
    """

    for account_name in get_slurm_account_names(cluster.name):
        if account_name in ['root']:
            continue

        try:
            account = ResearchGroup.objects.get(name=account_name)

        except ResearchGroup.DoesNotExist:
            log.warning(f"No existing ResearchGroup for account {account_name} on {cluster.name}, skipping for now")
            continue

        update_limit_for_account(account, cluster)


@shared_task()
def update_limit_for_account(account: ResearchGroup, cluster: Cluster) -> None:
    """Update the TRES billing usage limits for an individual Slurm account, closing out any expired allocations

    Args:
        account: ResearchGroup object for the account
        cluster: Cluster object corresponding to the Slurm cluster
    """

    # Base query for approved Allocations under the given account on the given cluster
    approved_query = Allocation.objects.filter(request__group=account, cluster=cluster, request__status='AP')

    # Query for allocations that have expired but do not have a final usage value, determine their SU contribution
    closing_query = approved_query.filter(final=None, request__expire__lte=date.today()).order_by("request__expire")
    closing_sus = closing_query.aggregate(Sum("awarded"))['awarded__sum'] or 0

    # Query for allocations that are active, and determine their total service unit contribution
    active_query = approved_query.filter(request__active__lte=date.today(), request__expire__gt=date.today())
    active_sus = active_query.aggregate(Sum("awarded"))['awarded__sum'] or 0

    # Determine the historical contribution to the current limit
    current_limit = get_cluster_limit(account.name, cluster.name)

    historical_usage = current_limit - active_sus - closing_sus
    if historical_usage < 0:
        log.warning(f"Negative Historical usage found for {account.name} on {cluster.name}:\n"
                    f"historical: {historical_usage} = current limit: {current_limit} - active: {active_sus} - closing: {closing_sus}\n"
                    f"Assuming zero...")
        historical_usage = 0

    # Close expired allocations and determine the current usage
    total_usage = get_cluster_usage(account.name, cluster.name)
    current_usage = total_usage - historical_usage
    if current_usage < 0:
        log.warning(f"Negative Current usage found for {account.name} on {cluster.name}:\n"
                    f"current: {current_usage} = total: {total_usage} - historical: {historical_usage}\n"
                    f"Setting to historical usage: {historical_usage}...")
        current_usage = historical_usage

    closing_summary = (f"Summary of closing allocations:\n"
                       f"    Current Usage before closing: {current_usage}\n")
    for allocation in closing_query.all():
        allocation.final = min(current_usage, allocation.awarded)
        closing_summary += f"    Allocation {allocation.id}: {current_usage} - {allocation.final} -> {current_usage - allocation.final}\n"
        current_usage -= allocation.final
        allocation.save()
    closing_summary += f"    Current Usage after closing: {current_usage}"

    # This shouldn't happen but if it does somehow, create a warning so an admin will notice
    if current_usage > active_sus:
        log.warning(f"The current usage is somehow higher than the limit for {account.name}!")

    # Set the new account usage limit using the updated historical usage after closing any expired allocations
    updated_historical_usage = approved_query.filter(request__expire__lte=date.today()).aggregate(Sum("final"))['final__sum'] or 0

    updated_limit = updated_historical_usage + active_sus
    set_cluster_limit(account.name, cluster.name, updated_limit)

    # Log summary of changes during limits update for this Slurm account on this cluster
    log.debug(f"Summary of limits update for {account.name} on {cluster.name}:\n"
              f"    Approved allocations found: {len(approved_query)}\n"
              f"    Service units from {len(active_query)} active allocations: {active_sus}\n"
              f"    Service units from {len(closing_query)} closing allocations: {closing_sus}\n"
              f"    {closing_summary}"
              f"    historical usage change: {historical_usage} -> {updated_historical_usage}\n"
              f"    limit change: {current_limit} -> {updated_limit}")


def send_expiry_notification_for_request(user: User, request: AllocationRequest) -> None:
    """Send any pending expiration notices to the given user

    A notification is only generated if warranted by the user's notification preferences.

    Args:
        user: The user to notify
        request: The allocation request to check for pending notifications
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
    log.debug(f'Request #{request.id} expires in {days_until_expire} days with next threshold at {next_threshold} days.')
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

    else:
        log.debug(f'Sending new notification for request #{request.id} to user {user.username}.')
        send_notification_template(
            user=user,
            subject=f'Allocation Expires on {request.expire}',
            template='expiration_email.html',
            notification_type=Notification.NotificationType.request_status,
            notification_metadata={
                'request_id': request.id,
                'request_title': request.title,
                'request_expire': request.expire.isoformat(),
                'days_to_expire': days_until_expire
            }
        )


@shared_task()
def send_expiry_notifications() -> None:
    """Send any pending expiration notices to all users"""

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
