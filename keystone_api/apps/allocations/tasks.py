"""Schedule tasks executed in parallel by Celery."""
import subprocess
from datetime import date

from celery import shared_task
from django.db.models import Sum

from apps.allocations.models import *
from apps.users.models import *


def update_status() -> None:
    """Update the account status on all clusters"""

    # Update account status on each cluster
    for cluster in Cluster.objects.filter(enabled=True).all():
        update_status_for_cluster(cluster)


def update_status_for_cluster(cluster: Cluster) -> None:
    """Update the status of each account on a given cluster"""

    # Gather all user account information
    cmd = "sacctmgr show -nP account format=Account"
    out = subprocess.check_output(cmd, shell=True)
    accounts = out.decode("utf-8").strip()
    accounts = accounts.split()

    # Update status for each individual account
    for account_name in accounts:
        update_status_for_account(cluster.name, account_name)


def update_status_for_account(cluster: Cluster, account_name: str) -> None:
    """Check an accounts resource limits in SLURM against their usage, locking on the cluster if necessary"""

    # Lock account if it does not exist
    try:
        account = ResearchGroup.objects.get(name=account_name)
    except ResearchGroup.DoesNotExist:
        # Lock the account on this cluster
        set_lock_state(cluster.name, account_name)
        # TODO: Logging
        return

    # Pull the required values from the account entry
    # Pull usage values from db

    current_tres_limit = association['max']['tres']['group']['active']


    total_usage = association['usage']

    active_sus = Allocation.objects.filter(proposal__group=account,
                                           cluster=cluster,
                                           proposal__approved=True,
                                           proposal__active__lte=date.today(),
                                           proposal__expire__gt=date.today()).aggregate(Sum("awarded"))

    historical_usage = Allocation.objects.filter(proposal__group=account,
                                                 cluster=cluster,
                                                 proposal__approved=True,
                                                 proposal__expire__lte=date.today()).aggregate(Sum("final"))

    # TODO: double check cluster=cluster works, also make sure we handle when it comes back as None

    # Proposals must be approved and active

    calculate_new_limit(active_sus, historical_usage, initial_usage, total_usage, current_tres_limit)

    # Insert new limits into dictionary item
    # association['max']['tres']['group']['active'] =

    # PATCH (ideally, may have to POST) updated dictionary item for the account


def calculate_new_limit(active_sus: int, historical_usage: int, initial_usage: int, total_usage: int,
                        current_tres_limit: int) -> int:
    """Compute the new tres limit"""

    # TODO: We don't have any mechanism to increase the limit yet
    return current_tres_limit - min(0, active_sus + historical_usage + initial_usage - total_usage)


def set_lock_state(lock_state: bool, cluster: str, account: str) -> None:
    """Update the locked/unlocked state for the given account, on a given cluster"""

    lock_state_int = 0 if lock_state else -1
    cmd = (f'sacctmgr -i modify account where account={account} cluster={cluster} '
           f'set GrpTresRunMins=cpu={lock_state_int}')

    cmd = (f'sacctmgr -i modify account where account={account} cluster={cluster} '
           f'set GrpTresRunMins=gres/gpu={lock_state_int}')
