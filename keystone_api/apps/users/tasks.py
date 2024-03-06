"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

import ldap
from celery import shared_task
from django.conf import settings
from django_auth_ldap.backend import LDAPBackend
from tqdm import tqdm

from keystone_api.plugins.slurm import get_slurm_account_names, get_slurm_account_principal_investigator, get_slurm_account_users
from .models import ResearchGroup, User


def get_ldap_connection() -> ldap.ldapobject.LDAPObject:
    """Establish a new LDAP connection"""

    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    if settings.AUTH_LDAP_BIND_DN:
        conn.bind(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

    if settings.AUTH_LDAP_START_TLS:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        conn.start_tls_s()

    return conn


@shared_task()
def ldap_update_users(prune=False) -> None:
    """Update the user database with the latest data from LDAP

    This function performs no action if the `AUTH_LDAP_SERVER_URI` setting
    is not configured in the application settings.

    Args:
        prune: Optionally delete any accounts with usernames not found in LDAP
    """

    if not settings.AUTH_LDAP_SERVER_URI:
        return

    # Search LDAP for all users
    conn = get_ldap_connection()
    search = conn.search_s(settings.AUTH_LDAP_USER_SEARCH.base_dn, ldap.SCOPE_SUBTREE, '(objectClass=account)')

    # Fetch keystone usernames using the LDAP attribute map defined in settings
    ldap_username_attr = settings.AUTH_LDAP_USER_ATTR_MAP.get('username', 'uid')
    ldap_names = {uid.decode() for result in search for uid in result[1][ldap_username_attr]}

    for username in tqdm(ldap_names):
        LDAPBackend().populate_user(username)

    if prune:
        usernames = set(User.objects.values_list('username', flat=True))
        users_to_delete = usernames - ldap_names
        User.objects.filter(username__in=users_to_delete).delete()


@shared_task()
def slurm_update_research_groups(prune=False) -> None:
    """Update the Research Group database with the latest account information from Slurm

    Args:
        prune: Optionally delete any Research Groups that are no longer present in Slurm
    """

    names_from_slurm = get_slurm_account_names()
    names_from_keystone = set(ResearchGroup.objects.values_list('name', flat=True))
    new_research_groups = names_from_slurm - names_from_keystone

    for account_name in tqdm(new_research_groups):
        ResearchGroup(name=account_name,
                      pi=get_slurm_account_principal_investigator(account_name),
                      members=User.objects.filter(username__in=get_slurm_account_users(account_name))
                      ).save()

    if prune:
        groups_to_delete = names_from_keystone - names_from_slurm
        ResearchGroup.objects.filter(name__in=groups_to_delete).delete()
