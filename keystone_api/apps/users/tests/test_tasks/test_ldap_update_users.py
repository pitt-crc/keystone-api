from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from apps.users.tasks import ldap_update_users


class LdapUpdateUsers(TestCase):
    """Test the `ldap_update_users` function."""

    @patch('apps.users.tasks.get_ldap_connection')
    @patch('apps.users.tasks.LDAPBackend')
    def test_ldap_update_users(self, mock_ldap_backend, mock_get_ldap_connection) -> None:
        """Test that users are updated from LDAP data."""

        # Mock LDAP search result
        mock_conn = MagicMock()
        mock_conn.search_s.return_value = [
            ('cn=admin,dc=example,dc=com', {'uid': [b'user1']}),
            ('cn=admin2,dc=example,dc=com', {'uid': [b'user2']})
        ]
        mock_get_ldap_connection.return_value = mock_conn

        # Configure settings and execute the update
        settings.AUTH_LDAP_USER_SEARCH = MagicMock(base_dn='dc=example,dc=com')
        settings.AUTH_LDAP_USER_ATTR_MAP = {'username': 'uid'}
        ldap_update_users()

        # Todo ensure user was created
        self.fail()
