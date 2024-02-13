"""Schedule tasks executed in parallel by Celery."""
import subprocess
from typing import List
from datetime import date

from celery import shared_task
from django.db.models import Sum

from apps.allocations.models import *
from apps.users.models import *


#TODO: Upon creation of a new allocation, update the GrpTresRunMinutes Limit

@shared_task()
def update_status() -> None:
    """Update the account status on all clusters"""

    # Update account status on each cluster
    for cluster in Cluster.objects.filter(enabled=True).all():
        update_status_for_cluster(cluster)


@shared_task()
def update_status_for_cluster(cluster: Cluster) -> None:
    """Update the status of each account on a given cluster"""

    # Update status for each individual account
    for account_name in get_account_names():
        update_status_for_account(cluster, account_name)


def update_status_for_account(cluster: Cluster, account_name: str) -> None:
    """Check an accounts resource limits in SLURM against their usage, locking on the cluster if necessary"""

    # TODO: Logging?
    # TODO: Need to make sure investment partitions are not locked for relevant slurm accounts
    # Lock account if it does not exist
    try:
        account = ResearchGroup.objects.get(name=account_name)
    except ResearchGroup.DoesNotExist:
        # Lock the account on this cluster
        lock_account_on_cluster(cluster.name, account_name)
        return

    # TODO: Should there be a check here for Allocations that expire today? Need to set final usage on those...
    #  attribute as much of the current day's usage to the expiring allocation if so?

    # Determine the earliest start date across proposals containing active allocations on the cluster
    end = date.today()
    active_allocations_query = Allocation.objects.filter(proposal__group=account,
                                                         cluster=cluster,
                                                         proposal__approved=True,
                                                         proposal__active__lte=date.today(),
                                                         proposal__expire__gt=date.today()).order_by("proposal__expire")

    # TODO: compare rawusage against limit

    # TODO: double check cluster=cluster works, also make sure we handle when it comes back as None
    start = active_allocations_query

    total_cluster_usage = get_cluster_usage(account_name, cluster.name, start, end)
    # Determine the total SUs available on the cluster across the active allocations
    total_cluster_sus = active_allocations_query.aggregate(Sum("awarded"))



    if total_cluster_usage >= total_cluster_sus:

        # All allocations are exhausted by current usage, set final usage and lock
        for alloc in active_allocations:
            alloc.final = alloc.awarded

        set_lock_state(True, cluster.name, account_name)


def lock_account_on_cluster(cluster: str, account: str) -> None:
    """Lock the given account, on a given cluster"""
    cmd = (f'sshare -nP -A {account} -M {cluster} --format=RawUsage')

    # Lock/Unlock CPU resources on the cluster
    cmd = (f'sacctmgr -i modify account where account={account} cluster={cluster} '
           f'set GrpTresRunMins=cpu={lock_state_int}')
    subprocess.run(cmd)

    # Lock/Unlock GPU resources on the cluster
    cmd = (f'sacctmgr -i modify account where account={account} cluster={cluster} '
           f'set GrpTresRunMins=gres/gpu={lock_state_int}')
    subprocess.run(cmd)


def get_account_names() -> List[str]:
    """Get a list of account names for a given cluster"""

    # Gather all user account information
    # For sacctmgr, "n" corresponds to no header rows, P is parsable
    # TODO: Should this pull info at the per cluster level?
    cmd = "sacctmgr show -nP account format=Account"
    out = subprocess.check_output(cmd, shell=True)
    accounts = out.decode("utf-8").strip()

    return accounts.split()


def get_cluster_usage(account_name: str, cluster_name: str, start: date, end: date) -> int:
    """Get the total usage on a given cluster for a given account between a given start and end date"""

    # Run sreport to get the account's usage on the cluster
    # TODO: by using f"format=Proper,Used") we can get usage per user for crc-usage type display
    cmd = (f"sreport cluster AccountUtilizationByUser -Pn -T Billing -t Hours cluster={cluster_name} "
           f"Account={account_name} start={start.strftime('%Y-%m-%d')} end={end.strftime('%Y-%m-%d')} "
           f"format=Used")
    out = subprocess.check_output(cmd, shell=True)

    # The first value is a sum across users in the account for the cluster
    usage = int(out.decode("utf-8").split()[0])

    return usage
