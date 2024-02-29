"""
A Django management command for synchronizing user account data with LDAP.

New accounts are created as necessary and existing accounts are updated to
reflect their corresponding LDAP entries. No Keystone accounts

"""

from django.core.management.base import BaseCommand

from apps.users.tasks import ldap_update


class Command(BaseCommand):
    """Create/update user accounts to reflect changes made in LDAP"""

    help = 'Create/update user accounts to reflect changes made in LDAP'

    def handle(self, *args, **options) -> None:
        """Handle the command execution"""

        ldap_update()
