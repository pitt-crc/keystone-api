"""Schedule tasks executed in parallel by Celery."""

from celery import shared_task
import requests
from apps.allocations.models import *
from apps.users.models import *
from datetime import date
from django.db.models import Sum

def update_status() -> None:
    """Update the account status on all clusters"""

    # Update account status on each cluster
    for cluster in Cluster.objects.filter(enabled=True).all():
        update_status_for_cluster(cluster)

def update_status_for_cluster(cluster: Cluster) -> None:
    """Using a URL and Token from a specific cluster's slurmrestd, update the status of each account on that cluster"""

    # Gather all user account information
    header_values = {'X-SLURM-USER-TOKEN': cluster.api_token, 'X-SLURM-USER-NAME': cluster.api_user}
    response = requests.get(f'{SLURM_DB_URL}/associations', headers=header_values)
    response_dict = response.json()

    # Update status for each individual account
    for association in response_dict['associations']:
        update_status_for_account(cluster.name, association)

    # TODO: if full associations json posted back to slurm, POST here

def update_status_for_account(cluster: Cluster, association: dict) -> None:
    """Update the resource limit in SLURM for the given account"""

    # Lock account if it does not exist
    account_name = association['account']
    try:
        account = ResearchGroup.objects.get(name=account_name)
    except ResearchGroup.DoesNotExist:
        # Lock the account
        # Logging

    # Pull the required values from the account entry
    # Pull usage values from db

    current_tres_limit = association['max']['tres']['group']['active']
    total_usage = association['usage']

    # TODO: initial_usage value not yet kept track of in db
    initial_usage = 0

    active_sus = Allocation.objects.filter(proposal__group=account,
                                             cluster=cluster,
                                             proposal__approved=True,
                                             proposal__active__lte=date.today(),
                                             proposal__expire__gt=date.today()).aggregate(Sum("sus"))


    historical_usage = Allocation.objects.filter(proposal__group=account,
                                             cluster=cluster,
                                             proposal__approved=True,
                                             proposal__expire__lte=date.today()).aggregate(Sum("final"))

    # TODO: double check cluster=cluster works, also make sure we handle when it comes back as None

    # Proposals must be approved and active

    calculate_new_limit(active_sus, historical_usage, initial_usage, total_usage, current_tres_limit)

    # Insert new limits into dictionary item
    #association['max']['tres']['group']['active'] =

    # PATCH (ideally, may have to POST) updated dictionary item for the account

def calculate_new_limit(active_sus: int, historical_usage: int, initial_usage: int, total_usage: int, current_tres_limit: int) -> int:
    """Compute the new tres limit"""

    # TODO: We don't have any mechanism to increase the limit yet
    return current_tres_limit - min(0, active_sus + historical_usage + initial_usage - total_usage)