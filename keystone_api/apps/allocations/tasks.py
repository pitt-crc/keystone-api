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
    """Adjust per Slurm account usage limits on all enabled clusters"""
    log.info(f"{date.today()} - BEGIN update_limits")

    for cluster in Cluster.objects.filter(enabled=True).all():
        log.debug(f"Updating limits for cluster {cluster.name}")
        update_limits_for_cluster(cluster)
        log.debug(f"Updating limits for cluster {cluster.name} DONE")


@shared_task()
def update_limits_for_cluster(cluster: Cluster) -> None:
    """Update the usage limits of each account on a given cluster, excluding the root account"""

    for account_name in get_accounts_on_cluster(cluster.name):
        if account_name in ['root']:
            continue
        log.debug(f"Updating limits for account {account_name}")
        update_limit_for_account(account_name, cluster.name)
        log.debug(f"Updating limits for account {account_name} DONE")


@shared_task()
def update_limit_for_account(account_name: str, cluster: Cluster) -> None:
    """Update the usage limits for an individual Slurm account"""

    # Check that the Slurm account has an entry in the keystone database
    try:
        account = ResearchGroup.objects.get(name=account_name)
    except ObjectDoesNotExist:
        #  Set the usage limit to zero (lock on this cluster) and continue
        log.warning(f"No existing ResearchGroup for account {account_name}, locking {account_name} on {cluster.name}")
        # TODO: This may create historical usage that keystone doesnt know about if raw usage is not reset
        #  for the account upon it actually being added into the application
        set_cluster_limit(account_name, cluster.name, get_cluster_usage(account_name, cluster.name))
        return

    # TODO: plan to perform a reset of rawusage before deployment. This makes it so an initial usage does not need
    #  to be tracked. Resetting rawusage will be part of the install procedure for us and others

    # Gather allocations that have expired but do not have a final usage value
    # (still contributing to current limit as active SUs instead of historical usage)
    closing_allocations_query = (Allocation.objects.filter(request__group=account,
                                                           cluster=cluster,
                                                           request__approved=True,
                                                           final=None,  # TODO: will this work?
                                                           request__expire__lte=date.today())
                                                   .order_by("request__expire"))

    # Gather all allocations belonging to "active" (started today or before and approved) Allocation Requests
    # for the account
    active_allocations_query = (Allocation.objects.filter(request__group=account,
                                                          cluster=cluster,
                                                          request__approved=True,
                                                          request__active__lte=date.today(),
                                                          request__expire__gt=date.today())
                                                  .order_by("request__expire"))

    # Determine the SU contribution by active allocations
    # TODO: Is this zero if there are no active allocations?
    active_sus = active_allocations_query.aggregate(Sum("awarded"))

    # Determine usage that can be covered:
    # total usage on the cluster (from slurm) - historical usage (current limit from slurm - active SUs - closing SUs)
    current_usage = (get_cluster_usage(account.name, cluster.name) -
                     (get_cluster_limit(account.name, cluster.name)
                      - active_sus - closing_allocations_query.aggregate(Sum("awarded"))))

    # Close out any expired allocations
    close_expired_allocations(closing_allocations_query.all(), current_usage)

    # Gather the updated historical usage from expired allocations (including any newly expired allocations)
    historical_usage = (Allocation.objects.filter(request__group=account,
                                                  cluster=cluster,
                                                  request__approved=True,
                                                  request__expire__lte=date.today())
                                          .aggregate(Sum("final")))

    # Determine new limit, including the SUs any new allocations starting today
    new_limit = historical_usage + active_sus

    # Set the new limit to the calculated limit
    set_cluster_limit(account_name, cluster.name, new_limit)


def close_expired_allocations(closing_allocations: Collection[Allocation], current_usage: int) -> None:
    """ Cover as much of the current usage as possible with expired allocations that have not yet been closed out
    # Setting final usage for these allocations  the historical usage """

    for allocation in closing_allocations:
        # TODO: Do these have an ID we can log instead?
        log.debug(f"Closing allocation {allocation.request.group}:{allocation.request.title}")

        # Set the final usage for the expired allocation
        if current_usage < allocation.final:
            allocation.final = current_usage
        else:
            allocation.final = allocation.awarded

        # Update the usage needing to be covered, so it is not double counted (can only ever be >= 0)
        current_usage -= allocation.final


def get_accounts_on_cluster(cluster_name: str) -> Collection[str]:
    """Return a list of account names for a given cluster"""

    # TODO: can we assume Slurm installations will have root as parent for child slurm accounts
    cmd = split(f"sacctmgr show -nP account withassoc where parents=root cluster={cluster_name} format=Account")

    out = subprocess_call(cmd)

    return out.split()


def set_cluster_limit(account_name: str, cluster_name: str, limit: int) -> None:
    """Update the current usage limit (in minutes) to the provided limit on a given cluster for a given account"""

    # TODO: This needs to be run as slurm user

    cmd = split(f"sacctmgr modify account where account={account_name} cluster={cluster_name} set "
                f"GrpTresRunMins=billing={limit}")

    subprocess_call(cmd)


def get_cluster_limit(account_name: str, cluster_name: str) -> int:
    """Get the current usage limit (in minutes) on a given cluster for a given account"""

    cmd = split(f"sacctmgr show -nP association where account={account_name} cluster={cluster_name} "
                f"format=GrpTRESRunMin")

    limit = re.findall(r'billing=(.*)\n', subprocess_call(cmd))[0]

    return int(limit) if limit.isnumeric() else 0


def get_cluster_usage(account_name: str, cluster_name: str) -> int:
    """Get the total billable usage in minutes on a given cluster for a given account"""

    cmd = split(f"sshare -nP -A {account_name} -M {cluster_name} --format=GrpTRESRaw")

    usage = re.findall(r'billing=(.*),fs', subprocess_call(cmd))[0]

    return int(usage) if usage.isnumeric() else 0


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
