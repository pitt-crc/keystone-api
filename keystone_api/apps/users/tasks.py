"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

import ldap
from celery import shared_task
from django.conf import Settings
from django_auth_ldap.backend import LDAPBackend

from .models import User


def get_connection() -> ldap.ldapobject.LDAPObject:
    """Establish a new LDAP connection"""

    conn = ldap.initialize(Settings.AUTH_LDAP_SERVER_URI)
    if Settings.AUTH_LDAP_BIND_DN:
        conn.bind(Settings.AUTH_LDAP_BIND_DN, Settings.AUTH_LDAP_BIND_PASSWORD)

    if Settings.AUTH_LDAP_START_TLS:
        conn.start_tls_s()

    return conn


@shared_task()
def ldap_update(prune=False) -> None:
    """Update the user database with the latest data from LDAP

    This function performs no action if the `AUTH_LDAP_SERVER_URI` setting
    is not configured in the application settings.

    Args:
        prune: Optionally delete any accounts with usernames not found in LDAP
    """

    if not Settings.AUTH_LDAP_SERVER_URI:
        return

    # Search LDAP for all users
    conn = get_connection()
    search = conn.search_s(Settings.AUTH_LDAP_USER_SEARCH, ldap.SCOPE_SUBTREE, '(objectClass=account)')

    # Fetch keystone usernames using the LDAP attribute map defined in settings
    ldap_username_attr = Settings.AUTH_LDAP_USER_ATTR_MAP.get('username', 'uid')
    ldap_names = {uid.decode() for result in search for uid in result[1][ldap_username_attr]}

    for username in ldap_names:
        LDAPBackend().populate_user(username)

    if prune:
        usernames = set(User.objects.values_list('name', flat=True))
        users_to_delete = usernames - ldap_names
        User.objects.filter(username__in=users_to_delete).delete()
