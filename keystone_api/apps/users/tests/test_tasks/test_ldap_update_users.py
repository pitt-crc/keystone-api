from unittest.mock import MagicMock, Mock, patch

from django.conf import settings
from django.test import TestCase

from apps.users.models import User
from apps.users.tasks import ldap_update_users


class LdapUpdateUsers(TestCase):
    """Test the `ldap_update_users` function."""

    def test_exit_silently_when_uri_is_none(self) -> None:
        """Test the function exits gracefully when no LDAP server URI is provided."""

        settings.AUTH_LDAP_SERVER_URI = None
        ldap_update_users()

    @patch('apps.users.tasks.get_ldap_connection')
    def test_users_are_created(self, mock_get_ldap_connection: Mock) -> None:
        """Test that users are updated from LDAP data."""

        # Mock the LDAP search result
        mock_conn = MagicMock()
        mock_conn.search_s.return_value = [
            ('cn=admin,dc=example,dc=com', {'uid': [b'user1']}),
            ('cn=admin2,dc=example,dc=com', {'uid': [b'user2']})
        ]
        mock_get_ldap_connection.return_value = mock_conn

        # Configure settings and execute the update
        settings.AUTH_LDAP_SERVER_URI = 'ldap://ds.example.com:389'
        settings.AUTH_LDAP_USER_SEARCH = MagicMock(base_dn='dc=example,dc=com')
        settings.AUTH_LDAP_USER_ATTR_MAP = {'username': 'uid'}
        ldap_update_users()

        # Test users were created
        self.assertTrue(User.objects.filter(username='user1').exists())
        user1 = User.objects.get(username='user1')
        self.assertTrue(user1.is_ldap_user)

        self.assertTrue(User.objects.filter(username='user2').exists())
        user2 = User.objects.get(username='user2')
        self.assertTrue(user2.is_ldap_user)

    def test_users_are_pruned(self) -> None:
        """Test the deletion of missing user accounts"""

        self.fail()

    def test_users_are_deactivated(self) -> None:
        """Test the deactivation of missing users"""

        self.fail()
