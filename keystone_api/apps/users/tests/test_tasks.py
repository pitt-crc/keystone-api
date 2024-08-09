"""Tests for the `tasks` module."""

from unittest.mock import MagicMock, Mock, patch

import ldap
from django.conf import settings
from django.test import override_settings, TestCase

from apps.users.models import User
from apps.users.tasks import get_ldap_connection, ldap_update_users


class TLSConfiguration(TestCase):
    """Test the configuration of TLS based on application settings."""

    @patch('ldap.initialize')
    @patch('ldap.set_option')
    @patch('ldap.ldapobject.LDAPObject')
    def test_get_ldap_connection(self, mock_ldap: Mock, mock_set_option: Mock, mock_initialize: Mock) -> None:
        """Test an LDAP connection is correctly configured with TLS enabled."""

        # Set up mock objects
        mock_conn = mock_ldap.return_value
        mock_initialize.return_value = mock_conn
        mock_set_option.return_value = None

        # Configure settings for testing
        settings.AUTH_LDAP_SERVER_URI = 'ldap://testserver'
        settings.AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=com'
        settings.AUTH_LDAP_BIND_PASSWORD = 'password123'
        settings.AUTH_LDAP_START_TLS = True

        # Call the function to test
        conn = get_ldap_connection()
        self.assertEqual(conn, mock_conn)

        # Check the calls
        mock_initialize.assert_called_once_with('ldap://testserver')
        mock_conn.bind.assert_called_once_with('cn=admin,dc=example,dc=com', 'password123')
        mock_set_option.assert_called_once_with(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        mock_conn.start_tls_s.assert_called_once()

    @patch('ldap.initialize')
    @patch('ldap.ldapobject.LDAPObject')
    def test_get_ldap_connection_without_tls(self, mock_ldap: Mock, mock_initialize: Mock) -> None:
        """Test an LDAP connection is correctly configured with TLS disabled."""

        # Set up mock objects
        mock_conn = mock_ldap.return_value
        mock_initialize.return_value = mock_conn

        # Configure settings for testing
        settings.AUTH_LDAP_SERVER_URI = 'ldap://testserver'
        settings.AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=com'
        settings.AUTH_LDAP_BIND_PASSWORD = 'password'
        settings.AUTH_LDAP_START_TLS = False

        # Call the function to test
        conn = get_ldap_connection()
        self.assertEqual(conn, mock_conn)

        # Check the calls
        mock_initialize.assert_called_once_with('ldap://testserver')
        mock_conn.bind.assert_called_once_with('cn=admin,dc=example,dc=com', 'password')
        mock_conn.start_tls_s.assert_not_called()


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
