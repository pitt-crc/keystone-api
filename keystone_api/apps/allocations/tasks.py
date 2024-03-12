"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

import logging
from datetime import date
from typing import Collection

from celery import shared_task
from django.db.models import Sum

from apps.allocations.models import Allocation, Cluster
from apps.users.models import ResearchGroup
from keystone_api.plugins.slurm import get_accounts_on_cluster, get_cluster_limit, get_cluster_usage, set_cluster_limit

log = logging.getLogger(__name__)


@shared_task()
def update_limits() -> None:
    """Adjust per Slurm account TRES billing hours usage limits on all enabled clusters"""
    log.info(f"Begin updating TRES billing hour limits for all Slurm Accounts")

    for cluster in Cluster.objects.filter(enabled=True).all():
        log.info(f"Updating TRES billing hour limits for cluster {cluster.name}")
        update_limits_for_cluster(cluster)


@shared_task()
def update_limits_for_cluster(cluster: Cluster) -> None:
    """Update the TRES billing usage limits of each account on a given cluster, excluding the root account"""

    for account_name in get_accounts_on_cluster(cluster.name):
        # Do not adjust limits for root
        if account_name in ['root']:
            continue
        log.info(f"Updating TRES billing hour limits for account {account_name}")
        update_limit_for_account(account_name, cluster)


@shared_task()
def update_limit_for_account(account_name: str, cluster: Cluster) -> None:
    """Update the TRES billing usage limits for an individual Slurm account, closing out any expired allocations"""

    # Check that the Slurm account has an entry in the keystone database
    try:
        account = ResearchGroup.objects.get(name=account_name)
    except ResearchGroup.DoesNotExist:
        #  Set the usage limit to the current usage (lock on this cluster) and continue
        log.warning(f"No existing ResearchGroup for account {account_name}, locking {account_name} on {cluster.name}")
        set_cluster_limit(account_name, cluster.name, get_cluster_usage(account_name, cluster.name))
        return

    # Base query for approved Allocations under the account on this cluster
    acct_alloc_query = Allocation.objects.filter(request__group=account, cluster=cluster, request__approved__isnull=False)

    # Filter on the base query for allocations that have expired but do not have a final usage value
    # (still contributing to current limit as active SUs instead of historical usage)
    closing_query = acct_alloc_query.filter(final=None, request__expire__lte=date.today()) \
                                    .order_by("request__expire")

    # Filter account's allocations to those that are active, and determine their total service unit contribution
    active_sus = acct_alloc_query.filter(request__active__lte=date.today(), request__expire__gt=date.today()) \
                                 .aggregate(Sum("awarded"))['awarded__sum'] or 0

    # Determine usage that can be covered:
    # total usage on the cluster (from slurm) - historical usage (current limit from slurm - active SUs - closing SUs)
    closing_sus = closing_query.aggregate(Sum("awarded"))['awarded__sum'] or 0

    historical_usage_from_limit = get_cluster_limit(account.name, cluster.name) - active_sus - closing_sus
    current_usage = get_cluster_usage(account.name, cluster.name) - historical_usage_from_limit

    close_expired_allocations(closing_query.all(), current_usage)

    # Gather the updated historical usage from expired allocations (including any newly expired allocations)
    updated_historical_usage = acct_alloc_query.filter(request__expire__lte=date.today()).aggregate(Sum("final"))['final__sum'] or 0

    # Set the new limit to the calculated limit
    set_cluster_limit(account_name, cluster.name, limit=updated_historical_usage + active_sus)


def close_expired_allocations(closing_allocations: Collection[Allocation], current_usage: int) -> None:
    """Set the final usage for expired allocations that have not yet been closed out

    Args:
        closing_allocations: list of Allocations to set final usage for
        current_usage: TRES billing hour usage to apply to allocations being closed out
    """

    for allocation in closing_allocations:
        log.debug(f"Closing allocation {allocation.id}")

        # Set the final usage for the expired allocation
        allocation.final = min(current_usage, allocation.awarded)

        # Update the usage needing to be covered, so it is not double counted (can only ever be >= 0)
        current_usage -= allocation.final
