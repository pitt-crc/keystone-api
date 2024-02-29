import ldap
from celery import shared_task
from django.conf import Settings
from django_auth_ldap.backend import LDAPBackend


@shared_task()
def sync_users_with_ldap() -> None:
    if not Settings.AUTH_LDAP_SERVER_URI:
        return

    conn = ldap.initialize(Settings.AUTH_LDAP_SERVER_URI)
    lsearch = conn.search_s(Settings.AUTH_LDAP_USER_SEARCH, ldap.SCOPE_SUBTREE, '(objectClass=account)')
    ldap_usernames = set(result[1]['uid'][0] for result in lsearch)

    for user in ldap_usernames:
        LDAPBackend().populate_user(user)
