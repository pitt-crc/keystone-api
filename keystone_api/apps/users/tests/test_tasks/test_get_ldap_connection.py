"""Tests for the `get_ldap_connection` function."""

from unittest.mock import Mock, patch

import ldap
from django.conf import settings
from django.test import TestCase

from apps.users.tasks import get_ldap_connection


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
