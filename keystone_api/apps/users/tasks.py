"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

import ldap
from celery import shared_task
from django.conf import Settings
from django_auth_ldap.backend import LDAPBackend


@shared_task()
def sync_users_with_ldap() -> None:
    """Update the user database with the latest data from LDAP

    This function performs no action if the `AUTH_LDAP_SERVER_URI` setting
    is not configured in the application settings.
    """

    if not Settings.AUTH_LDAP_SERVER_URI:
        return

    conn = ldap.initialize(Settings.AUTH_LDAP_SERVER_URI)
    if Settings.AUTH_LDAP_BIND_DN:
        conn.bind(Settings.AUTH_LDAP_BIND_DN, Settings.AUTH_LDAP_BIND_PASSWORD)

    if Settings.AUTH_LDAP_START_TLS:
        conn.start_tls_s()

    search = conn.search_s(Settings.AUTH_LDAP_USER_SEARCH, ldap.SCOPE_SUBTREE, '(objectClass=account)')
    ldap_names = {uid.decode() for result in search for uid in result[1]['uid']}

    for username in ldap_names:
        LDAPBackend().populate_user(username)
