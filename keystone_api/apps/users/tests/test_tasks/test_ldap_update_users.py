from unittest.mock import MagicMock, Mock, patch

from django.test import override_settings, TestCase

from apps.users.models import User
from apps.users.tasks import ldap_update_users


class LdapUpdateUsers(TestCase):
    """Test the `ldap_update_users` function."""

    @override_settings(AUTH_LDAP_SERVER_URI=None)
    def test_exit_silently_when_uri_is_none(self) -> None:
        """Test the function exits gracefully when no LDAP server URI is provided."""

        ldap_update_users()

    @override_settings(
        AUTH_LDAP_SERVER_URI='ldap://ds.example.com:389',
        AUTH_LDAP_USER_SEARCH=MagicMock(base_dn='dc=example,dc=com'),
        AUTH_LDAP_USER_ATTR_MAP={'username': 'uid'}
    )
    @patch('apps.users.tasks.get_ldap_connection')
    def test_users_are_created(self, mock_get_ldap_connection: Mock) -> None:
        """Test that users are updated from LDAP data."""

        # Mock LDAP search results
        mock_conn = MagicMock()
        mock_conn.search_s.return_value = [
            ('cn=admin,dc=example,dc=com', {'uid': [b'user1']}),
            ('cn=admin2,dc=example,dc=com', {'uid': [b'user2']})
        ]
        mock_get_ldap_connection.return_value = mock_conn

        # Execute the update
        ldap_update_users()

        # Test users were created
        self.assertTrue(User.objects.filter(username='user1').exists())
        user1 = User.objects.get(username='user1')
        self.assertTrue(user1.is_ldap_user)

        self.assertTrue(User.objects.filter(username='user2').exists())
        user2 = User.objects.get(username='user2')
        self.assertTrue(user2.is_ldap_user)

    @override_settings(
        AUTH_LDAP_SERVER_URI='ldap://ds.example.com:389',
        AUTH_LDAP_USER_SEARCH=MagicMock(base_dn='dc=example,dc=com'),
        AUTH_LDAP_USER_ATTR_MAP={'username': 'uid'}
    )
    @patch('apps.users.tasks.get_ldap_connection')
    def test_users_are_pruned(self, mock_get_ldap_connection: Mock) -> None:
        """Test the deletion of missing user accounts."""

        # Mock an LDAP search result with no users
        mock_conn = MagicMock()
        mock_conn.search_s.return_value = []
        mock_get_ldap_connection.return_value = mock_conn

        # Test missing users are deleted
        User.objects.create(username='user_to_prune', is_ldap_user=True)
        ldap_update_users(prune=True)
        self.assertFalse(User.objects.filter(username='user_to_prune').exists())

    @override_settings(
        AUTH_LDAP_SERVER_URI='ldap://ds.example.com:389',
        AUTH_LDAP_USER_SEARCH=MagicMock(base_dn='dc=example,dc=com'),
        AUTH_LDAP_USER_ATTR_MAP={'username': 'uid'}
    )
    @patch('apps.users.tasks.get_ldap_connection')
    def test_users_are_deactivated(self, mock_get_ldap_connection: Mock) -> None:
        """Test the deactivation of missing users."""

        # Mock an LDAP search result with no users
        mock_conn = MagicMock()
        mock_conn.search_s.return_value = []
        mock_get_ldap_connection.return_value = mock_conn

        # Test missing users are deactivated
        User.objects.create(username='user_to_deactivate', is_ldap_user=True, is_active=True)
        ldap_update_users()
        self.assertFalse(User.objects.get(username='user_to_deactivate').is_active)
