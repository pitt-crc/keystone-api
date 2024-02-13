"""Schedule tasks executed in parallel by Celery."""

from datetime import date

import requests
from django.conf import settings
from django.db.models import Sum

from apps.allocations.models import *
from apps.users.models import *

SLURM_DB_PATH = f'/slurmdb/{settings.SLURM_API_VERSION}'
SLURM_API_PATH = f'/slurm/{settings.SLURM_API_VERSION}'


def update_status() -> None:
    """Update the account status on all clusters"""

    for cluster in Cluster.objects.filter(enabled=True).all():
        update_status_for_cluster(cluster)


def update_status_for_cluster(cluster: Cluster) -> None:
    """Update the status of all accounts on a given cluster

    Args:
        cluster: A Cluster database record
    """

    api_headers = {'X-SLURM-USER-TOKEN': cluster.api_token, 'X-SLURM-USER-NAME': cluster.api_user}
    api_url = cluster.api_url.rstrip('/') + SLURM_DB_PATH + '/associations'

    # Fetch account information for all users
    response = requests.get(api_url, headers=api_headers)
    response.raise_for_status()

    # Update status for each individual account
    for association in response.json()['associations']:
        update_status_for_account(cluster.name, association)


def update_status_for_account(cluster: Cluster, association: dict) -> None:
    """Update the resource limit in SLURM for the given account

    Args:
        cluster: A Cluster database record
        association: Slurm association dictionary as returned by he Slurm API
    """

    # Get account information from Slurm API response
    account_name = association['account']
    current_tres_limit = association['max']['tres']['group']['active']
    total_usage = association['usage']

    try:
        research_group = ResearchGroup.objects.get(name=account_name)

    except ResearchGroup.DoesNotExist:
        return  # TODO: Lock account if it does not exist

    # Get research group information from application database
    initial_usage = InitialUsage.objects.get(group=research_group).usage

    approved_proposal_query = Allocation.objects.filter(
        proposal__group=research_group,
        proposal__approved=True,
        cluster=cluster)

    active_sus = approved_proposal_query.filter(
        proposal__active__lte=date.today(),
        proposal__expire__gt=date.today()
    ).aggregate(Sum("sus"))['sus_sum']

    historical_usage = approved_proposal_query.filter(
        proposal__expire__lte=date.today()
    ).aggregate(Sum("final"))['final_sum']

    new_limit = calculate_new_limit(active_sus, historical_usage, initial_usage, total_usage, current_tres_limit)
    # TOD: PATCH (or POST) updated account limits


def calculate_new_limit(active_sus: int, historical_usage: int, initial_usage: int, total_usage: int, current_tres_limit: int) -> int:
    """Compute the new tres limit"""

    # TODO: We don't have any mechanism to increase the limit yet
    return current_tres_limit - min(0, active_sus + historical_usage + initial_usage - total_usage)
