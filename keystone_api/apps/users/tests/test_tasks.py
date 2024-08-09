"""Tests for the `tasks` module."""

from unittest.mock import MagicMock, Mock, patch

import ldap
from django.test import override_settings, TestCase

from apps.users.models import User
from apps.users.tasks import get_ldap_connection, ldap_update_users


class GetLdapConnection(TestCase):
    """Test connecting to LDAP via the `test_get_ldap_connection` function."""

    @override_settings(
        AUTH_LDAP_SERVER_URI='ldap://testserver',
        AUTH_LDAP_BIND_DN='cn=admin,dc=example,dc=com',
        AUTH_LDAP_BIND_PASSWORD='password123',
        AUTH_LDAP_START_TLS=True
    )
    @patch('ldap.initialize')
    @patch('ldap.set_option')
    @patch('ldap.ldapobject.LDAPObject')
    def test_tls_configuration(self, mock_ldap: Mock, mock_set_option: Mock, mock_initialize: Mock) -> None:
        """Test an LDAP connection is correctly configured with TLS enabled."""

        # Set up mock objects
        mock_conn = mock_ldap.return_value
        mock_initialize.return_value = mock_conn
        mock_set_option.return_value = None

        # Call the function to test
        conn = get_ldap_connection()
        self.assertEqual(conn, mock_conn)

        # Check the connection calls
        mock_initialize.assert_called_once_with('ldap://testserver')
        mock_conn.bind.assert_called_once_with('cn=admin,dc=example,dc=com', 'password123')
        mock_set_option.assert_called_once_with(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)


class LdapUpdateUsers(TestCase):
    """Test updating user data via the `ldap_update_users` function."""

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
    @patch('apps.users.tasks.LDAPBackend')
    def test_users_are_created(self, ldap_backend: Mock, mock_get_ldap_connection: Mock) -> None:
        """Test users are updated from LDAP data."""

        # Mock LDAP search results
        mock_conn = mock_get_ldap_connection.return_value
        mock_conn.search_s.return_value = [
            ('uid=user1,ou=users,dc=example,dc=com', {'uid': [b'user1']}),
            ('uid=user2,ou=users,dc=example,dc=com', {'uid': [b'user2']}),
        ]

        # Mock backend to return user objects
        mock_backend = ldap_backend.return_value
        mock_backend.populate_user.side_effect = lambda username: User(username=username)

        # Test users are created
        ldap_update_users(prune=False)
        user1 = User.objects.get(username='user1')
        user2 = User.objects.get(username='user2')

        # Verify that the users have the is_ldap_user flag set
        self.assertTrue(user1.is_ldap_user)
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

        # Create users
        User.objects.create(username='user_to_prune', is_ldap_user=True)
        User.objects.create(username='non_ldap_user', is_ldap_user=False)

        # Test missing LDAP users are deleted
        ldap_update_users(prune=True)
        self.assertFalse(User.objects.filter(username='user_to_prune').exists())
        self.assertTrue(User.objects.filter(username='non_ldap_user').exists())

    @override_settings(
        AUTH_LDAP_SERVER_URI='ldap://ds.example.com:389',
        AUTH_LDAP_USER_SEARCH=MagicMock(base_dn='dc=example,dc=com'),
        AUTH_LDAP_USER_ATTR_MAP={'username': 'uid'}
    )
    @patch('apps.users.tasks.get_ldap_connection')
    def test_users_are_deactivated(self, mock_get_ldap_connection: Mock) -> None:
        """Test the deactivation of missing LDAP users, ensuring non-LDAP users are not affected."""

        # Mock an LDAP search result with no users
        mock_conn = MagicMock()
        mock_conn.search_s.return_value = []
        mock_get_ldap_connection.return_value = mock_conn

        # Create users
        User.objects.create(username='user_to_deactivate', is_ldap_user=True, is_active=True)
        User.objects.create(username='non_ldap_user', is_ldap_user=False, is_active=True)

        # Test missing LDAP users are deactivated
        ldap_update_users()
        self.assertFalse(User.objects.get(username='user_to_deactivate').is_active)
        self.assertTrue(User.objects.get(username='non_ldap_user').is_active)
