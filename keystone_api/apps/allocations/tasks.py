"""Schedule tasks executed in parallel by Celery."""

from datetime import date
import re
import subprocess

from celery import shared_task
from django.db.models import Sum

from apps.allocations.models import *


def update_limits_new_allocation(allocation: Allocation, sender, **kwargs) -> None:
    """Update the usage limits to include a new allocation's contributions if it starts today (signaled by new allocation
    creation)"""
    # TODO: use django signaling for this?

    if allocation.proposal.active == date.today():
        update_limit_for_account(allocation)


@shared_task()
def update_limits_allocation() -> None:
    """Reduce or increase usage limits for all allocations that are expiring or starting today (runs daily)"""

    # Gather all allocations that expired today
    expired_allocations = Allocation.objects.filter(proposal__approved=True,
                                                    proposal__active__lt=date.today(),
                                                    proposal__expire=date.today()).sort_by("proposal__active")

    # Update the usage limits due to any expired allocations
    for allocation in expired_allocations:
        update_limit_for_account(allocation)

    # Gather all allocations that start today
    starting_allocations = Allocation.objects.filter(propsal__approved=True,
                                                     proposal__active=date.today(),
                                                     proposal__expired__gt=date.today()).all()

    # Update the usage limits due to any starting allocations
    for allocation in starting_allocations:
        update_limit_for_account(allocation)


def update_limit_for_account(allocation: Allocation) -> None:
    """Check an accounts resource limits in SLURM against their usage, locking on the cluster if necessary"""

    # TODO: Logging?

    group = allocation.get_research_group()
    account_name = group.name
    cluster_name = allocation.cluster.name

    # New allocation starting, add it to existing limits
    if allocation.proposal.active == date.today():

        # Skip if the allocation is already represented in the current limit:
        if allocation.is_contributing:
            return

        # Set initial usage for the Slurm Account if this is their first allocation on the cluster
        if not group.initial_usage:
            group.initial_usage = get_cluster_usage(group.name, cluster_name)

        # Calculate the new limit and set it
        current_usage_limit = get_cluster_limit(account_name, cluster_name)
        new_allocation_contribution = allocation.awarded
        new_limit = current_usage_limit + new_allocation_contribution
        set_cluster_limit(account_name, cluster_name, new_limit)

        allocation.is_contributing = True

    # Old allocation ending, remove it from existing limits
    elif allocation.proposal.expire == date.today():

        # Gather Usage values to compute current usage
        historical_usage = Allocation.objects.filter(proposal__group=account_name,
                                                     cluster=cluster_name,
                                                     proposal__approved=True,
                                                     proposal__active__lte=date.today(),
                                                     proposal__expire__lte=date.today()).aggregate(Sum("final"))

        total_cluster_usage = get_cluster_usage(account_name, cluster_name)
        current_usage = total_cluster_usage - historical_usage - group.initial_usage

        # Set the final usage for the expired allocation
        if current_usage < allocation.awarded:
            allocation.final = current_usage
        else:
            allocation.final = allocation.awarded

        # Calculate the new limit and set it
        current_usage_limit = get_cluster_limit(account_name, cluster_name)
        expired_allocation_contribution = allocation.awarded - allocation.final
        new_limit = current_usage_limit - expired_allocation_contribution
        set_cluster_limit(account_name, cluster_name, new_limit)

        allocation.is_contributing = False


def set_cluster_limit(account_name: str, cluster_name: str, limit: int) -> None:
    """Update the current usage limit (in minutes) to the provided limit on a given cluster for a given account"""

    # TODO: Does this need to be run as root?
    cmd = (f"sacctmgr modify account where account={account_name} cluster={cluster_name} set "
           f"GrpTresRunMins=billing={limit}")
    subprocess.run(cmd, shell=True)


def get_cluster_limit(account_name: str, cluster_name: str) -> int:
    """Get the current usage limit (in minutes) on a given cluster for a given account"""

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
