"""Schedule tasks executed in parallel by Celery."""

from datetime import date
import re
import subprocess
from typing import List

from celery import shared_task
from django.db.models import Sum

from apps.allocations.models import *
from apps.users.models import *


@shared_task()
def update_limits() -> None:
    """Adjust per Slurm account usage limits on all enabled clusters"""

    for cluster in Cluster.objects.filter(enabled=True).all():
        update_limits_for_cluster(cluster)


@shared_task()
def update_limits_for_cluster(cluster: Cluster) -> None:
    """Update the usage limits of each account on a given cluster"""

    for account_name in get_accounts_on_cluster(cluster.name):
        update_limit_for_account(account_name, cluster.name)


@shared_task()
def update_limit_for_account(account_name: str, cluster_name: str) -> None:
    """Update the usage limits for an individual Slurm account"""

    # TODO: Check that the Slurm account has an entry in the keystone database
    try:
        account = ResearchGroup.objects.get(name=account_name)
    except ResearchGroup.DoesNotExist:
        # TODO: create research group for this slurm account and let the rest of the function run?
        #  or just set usage limit to zero (lock on this cluster) and continue?
        return

    # Set initial usage for the Slurm Account. If this is their first allocation on the cluster,
    # set it to their current usage
    if not account.initial_usage:
        account.initial_usage = get_cluster_usage(account.name, cluster_name)
    initial_usage = account.initial_usage

    # TODO: Close out any allocations have ended?
    close_out_allocations = Allocation.objects.filter(proposal__group=account,
                                                      cluster=cluster_name,
                                                      proposal_approved=True,
                                                      final=None,
                                                      proposal__expire__lte=date.today()).order_by("proposal__expire")

    # Cover as much of the current usage as possible with expired allocations that have not yet been closed out
    for allocation in close_out_allocations:
        # TODO: fill out this calculation
        current_usage = total_cluster_usage - historical_usage - initial_usage

        # Set the final usage for the expired allocation
        if current_usage < allocation.awarded:
            allocation.final = current_usage
        else:
            allocation.final = allocation.awarded

    # Gather all allocations belonging to active proposals for the account
    active_allocations_query = Allocation.objects.filter(proposal__group=account,
                                                         cluster=cluster_name,
                                                         proposal_approved=True,
                                                         proposal__active__lte=date.today(),
                                                         final=None,
                                                         proposal__expire__gt=date.today()).order_by("proposal__expire")

    # Gather the historical usage from expired proposal allocations
    historical_usage = Allocation.objects.filter(proposal__group=account_name,
                                                 cluster=cluster_name,
                                                 proposal__approved=True,
                                                 proposal__active__lte=date.today(),
                                                 proposal__expire__lte=date.today()).aggregate(Sum("final"))

    # Gather total service units available from active proposal allocations
    proposal_sus = active_allocations_query.aggregate(Sum("awarded"))

    # Get the usage total on the cluster for the account from Slurm
    total_usage = get_cluster_usage(account_name, cluster_name)

    # Get the current limit
    current_limit = get_cluster_limit(account_name, cluster_name)

    # Calculate the new limit for the account given the current usage and state of their allocations
    new_limit = calculate_new_limit(current_limit, proposal_sus, historical_usage, initial_usage, total_usage)

    # Set the new limit to the calculated limit
    set_cluster_limit(account_name, cluster_name, new_limit)


def calculate_new_limit(current_limit: int, proposal_sus: int, historical_usage: int, initial_usage: int, total_usage: int) -> int:
    """Calculate the new usage limits given the current state of an account's usage and allocations"""

    return current_limit - min(0, proposal_sus + historical_usage + initial_usage - total_usage)


def get_accounts_on_cluster(cluster_name: str) -> List[str]:
    """Return a list of account names for a given cluster"""

    cmd = "sacctmgr show -nP account withassoc where parents=root cluster={cluster_name} format=Account"
    out = subprocess.check_output(cmd,shell=True)

    return out.decode("utf-8").strip().split()


def set_cluster_limit(account_name: str, cluster_name: str, limit: int) -> None:
    """Update the current usage limit (in minutes) to the provided limit on a given cluster for a given account"""

    # TODO: Does this need to be run as root?
    cmd = (f"sacctmgr modify account where account={account_name} cluster={cluster_name} set "
           f"GrpTresRunMins=billing={limit}")
    subprocess.run(cmd, shell=True)


def get_cluster_limit(account_name: str, cluster_name: str) -> int:
    """Get the current usage limit (in minutes) on a given cluster for a given account"""

    # TODO: reintroduce popen/PIPE format to manage security risk of escalating commands with shell=True
    cmd = f"sacctmgr show -nP association where account={account_name} cluster={cluster_name} format=GrpTRESRunMin"
    out = subprocess.check_output(cmd, shell=True).decode("utf-8")
    limit = re.findall(r'billing=(.*)\n', out)[0]

    return int(limit) if limit.isnumeric() else 0


def get_cluster_usage(account_name: str, cluster_name: str) -> int:
    """Get the total billable usage in minutes on a given cluster for a given account"""

    cmd = f"sshare -nP -A {account_name} -M {cluster_name} --format=GrpTRESRaw"
    out = subprocess.check_output(cmd, shell=True).decode("utf-8")
    usage = re.findall(r'billing=(.*),fs', out)[0]

    return int(usage) if usage.isnumeric() else 0
