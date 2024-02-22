"""Schedule tasks executed in parallel by Celery."""

from datetime import date
import logging
import re
from shlex import split
from subprocess import PIPE, Popen
from typing import List

from celery import shared_task
from django.db.models import Sum

from apps.allocations.models import *
from apps.users.models import *

log = logging.getLogger(__name__)


@shared_task()
def update_limits() -> None:
    """Adjust per Slurm account usage limits on all enabled clusters"""

    for cluster in Cluster.objects.filter(enabled=True).all():
        update_limits_for_cluster(cluster)


@shared_task()
def update_limits_for_cluster(cluster: Cluster) -> None:
    """Update the usage limits of each account on a given cluster"""

    # TODO: root should not be in this list of accounts, if account_name=root continue
    for account_name in get_accounts_on_cluster(cluster.name):
        update_limit_for_account(account_name, cluster.name)


@shared_task()
def update_limit_for_account(account_name: str, cluster: Cluster) -> None:
    """Update the usage limits for an individual Slurm account"""

    # Check that the Slurm account has an entry in the keystone database
    try:
        account = ResearchGroup.objects.get(name=account_name)
    except ResearchGroup.DoesNotExist:
        #  TODO: just set usage limit to zero (lock on this cluster) and continue
        log.info()
        return

    # TODO: plan to perform a reset of rawusage before deployment.
    #  Resetting rawusage will be part of the install procedure for us and others

    # Gather the historical usage from expired proposal allocations
    historical_usage = (Allocation.objects.filter(proposal__group=account,
                                                  cluster=cluster,
                                                  proposal__approved=True,
                                                  proposal__active__lte=date.today(),
                                                  proposal__expire__lte=date.today())
                        .exclude(final=None).aggregate(Sum("final")))

    # Get the usage total on the cluster for the account from Slurm
    total_usage = get_cluster_usage(account_name, cluster.name)

    # Close out any expired allocations that have not already been closed out first
    # Gather allocations that have expired but do not have a final usage value
    allocations_to_close = Allocation.objects.filter(proposal__group=account,
                                                     cluster=cluster,
                                                     proposal_approved=True,
                                                     final=None,  # TODO: will this work?
                                                     proposal__expire__lte=date.today()).order_by("proposal__expire")

    # Cover as much of the current usage as possible with expired allocations that have not yet been closed out
    # TODO: move up before querying, have closed values contribute to historical before storing them
    for allocation in allocations_to_close:
        current_usage = total_usage - historical_usage

        # Set the final usage for the expired allocation
        if current_usage < allocation.awarded:
            allocation.final = current_usage
        else:
            allocation.final = allocation.awarded

        # Update the historical usage to reflect the closed out allocation
        historical_usage += allocation.final

    # Gather all allocations belonging to active proposals for the account
    active_allocations_query = Allocation.objects.filter(proposal__group=account,
                                                         cluster=cluster,
                                                         proposal_approved=True,
                                                         proposal__active__lte=date.today(),
                                                         proposal__expire__gt=date.today()).order_by("proposal__expire")

    # Calculate the new limit for the account given the current usage and state of their allocations
    new_limit = calculate_new_limit(current_limit=get_cluster_limit(account_name, cluster.name),
                                    proposal_sus=active_allocations_query.aggregate(Sum("awarded")),
                                    historical_usage=historical_usage,
                                    total_usage=total_usage)

    # Set the new limit to the calculated limit
    set_cluster_limit(account_name, cluster.name, new_limit)


def calculate_new_limit(current_limit: int, proposal_sus: int, historical_usage: int, total_usage: int) -> int:
    """Calculate the new usage limits given the current state of an account's usage and allocations"""

    # TODO: Need to consider addition of new allocations and the corresponding limit change
    #  What should the new limit be independent of current_limit
    return current_limit - min(0, proposal_sus + historical_usage - total_usage)


def get_accounts_on_cluster(cluster_name: str) -> List[str]:
    """Return a list of account names for a given cluster"""

    # TODO: can we assume Slurm installations will have root as parent for child slurm accounts
    cmd = f"sacctmgr show -nP account withassoc where parents=root cluster={cluster_name} format=Account"
    out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()

    if err:
        pass
        # TODO: log and raise a runtime error

    return out.decode("utf-8").strip().split()


def set_cluster_limit(account_name: str, cluster_name: str, limit: int) -> None:
    """Update the current usage limit (in minutes) to the provided limit on a given cluster for a given account"""

    # TODO: This needs to be run as slurm user

    cmd = (f"sacctmgr modify account where account={account_name} cluster={cluster_name} set "
           f"GrpTresRunMins=billing={limit}")
    out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()

    if err:
        pass
        # TODO: log and raise an error


def get_cluster_limit(account_name: str, cluster_name: str) -> int:
    """Get the current usage limit (in minutes) on a given cluster for a given account"""

    # TODO: reintroduce popen/PIPE format to manage security risk of escalating commands with shell=True
    cmd = f"sacctmgr show -nP association where account={account_name} cluster={cluster_name} format=GrpTRESRunMin"
    out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()

    if err:
        pass
        # TODO: log and raise an error

    limit = re.findall(r'billing=(.*)\n', out.decode("utf-8"))[0]

    return int(limit) if limit.isnumeric() else 0


def get_cluster_usage(account_name: str, cluster_name: str) -> int:
    """Get the total billable usage in minutes on a given cluster for a given account"""

    cmd = f"sshare -nP -A {account_name} -M {cluster_name} --format=GrpTRESRaw"
    out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()

    if err:
        pass
        # TODO: log and raise an error

    usage = re.findall(r'billing=(.*),fs', out.decode("utf-8"))[0]

    return int(usage) if usage.isnumeric() else 0
