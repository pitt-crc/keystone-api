"""
A Django management command for deleting user accounts that have been removed
from LDAP.
"""

from django.core.management.base import BaseCommand

from apps.users.tasks import ldap_prune


class Command(BaseCommand):
    """Delete any user accounts not found in LDAP"""

    help = 'Delete any user accounts not found in LDAP'

    def handle(self, *args, **options) -> None:
        """Handle the command execution"""

        ldap_prune()
