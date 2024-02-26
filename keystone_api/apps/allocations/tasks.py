"""Schedule tasks executed in parallel by Celery."""

from datetime import date
import logging
import re
from shlex import split
from subprocess import PIPE, Popen
from typing import Collection, List

from celery import shared_task
from django.db.models import Sum, ObjectDoesNotExist

from apps.allocations.models import Allocation, Cluster
from apps.users.models import ResearchGroup

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
    """Update the TRES billing hour usage limits of each account on a given cluster, excluding the root account"""

    for account_name in get_accounts_on_cluster(cluster.name):
        # Do not adjust limits for root
        if account_name in ['root']:
            continue
        log.info(f"Updating TRES billing hour limits for account {account_name}")
        update_limit_for_account(account_name, cluster.name)


@shared_task()
def update_limit_for_account(account_name: str, cluster: Cluster) -> None:
    """Update the TRES Billing Hour usage limits for an individual Slurm account, closing out any expired allocations"""

    # Check that the Slurm account has an entry in the keystone database
    try:
        account = ResearchGroup.objects.get(name=account_name)
    except ObjectDoesNotExist:
        #  Set the usage limit to the current usage (lock on this cluster) and continue
        log.warning(f"No existing ResearchGroup for account {account_name}, locking {account_name} on {cluster.name}")
        set_cluster_limit(account_name, cluster.name, get_cluster_usage(account_name, cluster.name))
        return

    # Base query for approved Allocations under the account on this cluster
    acct_alloc_query = Allocation.objects.filter(request__group=account, cluster=cluster, request__approved=True)

    # Filter on the base query for allocations that have expired but do not have a final usage value
    # (still contributing to current limit as active SUs instead of historical usage)
    closing_query = acct_alloc_query.filter(final=None, request__expire__lte=date.today()) \
                                    .order_by("request__expire")

    # Filter account's allocations to those that are active, and determine their total service unit contribution
    active_sus = acct_alloc_query.filter(request__active__lte=date.today(),request__expire__gt=date.today()) \
                                 .aggregate(Sum("awarded"))

    # Determine usage that can be covered:
    # total usage on the cluster (from slurm) - historical usage (current limit from slurm - active SUs - closing SUs)
    current_usage = get_cluster_usage(account.name, cluster.name) - (get_cluster_limit(account.name, cluster.name) - active_sus - closing_query.aggregate(Sum("awarded")))

    close_expired_allocations(closing_query.all(), current_usage)

    # Gather the updated historical usage from expired allocations (including any newly expired allocations)
    historical_usage = acct_alloc_query.filter(request__expire__lte=date.today()).aggregate(Sum("final"))

    # Set the new limit to the calculated limit
    set_cluster_limit(account_name, cluster.name, limit=historical_usage + active_sus)


def close_expired_allocations(closing_allocations: Collection[Allocation], current_usage: int) -> None:
    """Set the final usage for expired allocations that have not yet been closed out"""

    for allocation in closing_allocations:
        log.debug(f"Closing allocation {allocation.request.group}:{allocation.request.title}")

        # Set the final usage for the expired allocation
        allocation.final = min(current_usage, allocation.awarded)

        # Update the usage needing to be covered, so it is not double counted (can only ever be >= 0)
        current_usage -= allocation.final


def get_accounts_on_cluster(cluster_name: str) -> Collection[str]:
    """Gather a list of account names for a given cluster from sacctmgr

    Args:
        cluster_name: The name of the cluster to get usage on

    Returns:
        A list of Slurm account names
    """

    cmd = split(f"sacctmgr show -nP account withassoc where parents=root cluster={cluster_name} format=Account")

    out = subprocess_call(cmd)

    return out.split()


def set_cluster_limit(account_name: str, cluster_name: str, limit: int, in_minutes: bool = False) -> None:
    """Update the current TRES Billing hour usage limit to the provided limit on a given cluster for a given account
    with sacctmgr. The default time unit is Hours.

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        limit: Number of billing TRES hours to set the usage limit to
        in_minutes: Boolean value for whether (True) or not (False) the set limit is in minutes (Default: False)
    """

    if in_minutes:
        limit *= 60

    cmd = split(f"sacctmgr modify account where account={account_name} cluster={cluster_name} set GrpTresRunMins=billing={limit}")

    subprocess_call(cmd)


def get_cluster_limit(account_name: str, cluster_name: str, in_minutes: bool = False) -> int:
    """Get the current TRES Billing Hour usage limit on a given cluster for a given account with sacctmgr.
    The default time unit is Hours.

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        in_minutes: Boolean value for whether (True) or not (False) the returned limit is in minutes (Default: False)

    Returns:
        An integer representing the total (historical + current) billing TRES limit
    """

    cmd = split(f"sacctmgr show -nP association where account={account_name} cluster={cluster_name} "
                f"format=GrpTRESRunMin")

    limit = re.findall(r'billing=(.*)\n', subprocess_call(cmd))[0]

    if not limit.isnumeric():
        return 0

    limit = int(limit)
    if in_minutes:
        limit *= 60

    return limit


def get_cluster_usage(account_name: str, cluster_name: str, in_hours: bool = True) -> int:
    """Get the total billable usage in minutes on a given cluster for a given account

    Args:
        account_name: The name of the account to get usage for
        cluster_name: The name of the cluster to get usage on
        in_hours: Boolean value for whether (True) or not (False) the returned Usage is in hours (Default: True)

    Returns:
        An integer representing the total (historical + current) billing TRES hours usage from sshare
    """

    cmd = split(f"sshare -nP -A {account_name} -M {cluster_name} --format=GrpTRESRaw")

    usage = re.findall(r'billing=(.*),fs', subprocess_call(cmd))[0]

    if not usage.isnumeric():
        return 0

    usage = int(usage)
    if in_hours:
        usage //= 60

    return usage


def subprocess_call(args: List[str]) -> str:
    """Wrapper method for executing shell commands via ``Popen.communicate``

    Args:
        args: A sequence of program arguments

    Returns:
        The piped output to STDOUT and STDERR as strings
    """

    process = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        message = f"Error executing shell command: {' '.join(args)} \n {err.decode('utf-8').strip()}"
        log.error(message)
        raise RuntimeError(message)

    return out.decode("utf-8").strip()
