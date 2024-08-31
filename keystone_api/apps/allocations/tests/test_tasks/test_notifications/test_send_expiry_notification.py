"""Unit tests for the `send_expiry_notification` function."""

from datetime import date, timedelta
from unittest.mock import MagicMock, Mock, patch

from django.test import TestCase

from apps.allocations.models import AllocationRequest
from apps.allocations.tasks import send_expiry_notification
from apps.users.models import User


class NotificationSending(TestCase):
    """Test the sending/skipping of notifications."""

    def setUp(self):
        """Set up test data."""

        self.user = MagicMock(spec=User)
        self.user.username = 'testuser'
        self.user.date_joined = date.today() - timedelta(days=10)
        self.user.is_active = True

        self.request = MagicMock(spec=AllocationRequest)

    @patch('apps.notifications.shortcuts.send_notification_template')
    def test_no_notification_if_request_does_not_expire(self, mock_send_template: Mock) -> None:
        """Test no notification is sent if the request does not expire."""

        self.request.get_days_until_expire.return_value = None
        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            send_expiry_notification(self.user, self.request)
            self.assertRegex(log.output[-1], '.*Skipping expiry notification .* does not expire.*')

        mock_send_template.assert_not_called()

    @patch('apps.notifications.shortcuts.send_notification_template')
    def test_no_notification_if_request_already_expired(self, mock_send_template: Mock) -> None:
        """Test no notification is sent if the request has already expired."""

        self.request.get_days_until_expire.return_value = 0
        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            send_expiry_notification(self.user, self.request)
            self.assertRegex(log.output[-1], '.*Skipping expiry notification .* has already expired.*')

        mock_send_template.assert_not_called()

    @patch('apps.notifications.shortcuts.send_notification_template')
    @patch('apps.notifications.models.Preference.get_user_preference')
    def test_no_notification_if_no_threshold_reached(
        self, mock_get_user_preference: Mock, mock_send_template: Mock
    ) -> None:
        """Test no notification is sent if no threshold is reached."""

        mock_preference = MagicMock()
        mock_preference.get_next_expiration_threshold.return_value = None
        mock_get_user_preference.return_value = mock_preference

        self.request.get_days_until_expire.return_value = 15
        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            send_expiry_notification(self.user, self.request)
            self.assertRegex(
                log.output[-1],
                '.*Skipping expiry notification .* No notification threshold has been hit yet.*'
            )

        mock_send_template.assert_not_called()

    @patch('apps.notifications.shortcuts.send_notification_template')
    @patch('apps.notifications.models.Preference.get_user_preference')
    def test_no_notification_if_user_recently_joined(
        self, mock_get_user_preference: Mock, mock_send_template: Mock
    ) -> None:
        """Test no notification is sent if the user recently joined."""

        mock_preference = MagicMock()
        mock_preference.get_next_expiration_threshold.return_value = 10
        mock_get_user_preference.return_value = mock_preference

        self.user.date_joined = date.today() - timedelta(days=5)
        self.request.get_days_until_expire.return_value = 15

        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            send_expiry_notification(self.user, self.request)
            self.assertRegex(
                log.output[-1],
                '.*Skipping expiry notification .* User account created after notification threshold.*'
            )

        mock_send_template.assert_not_called()

    @patch('apps.notifications.shortcuts.send_notification_template')
    @patch('apps.notifications.models.Notification.objects.filter')
    @patch('apps.notifications.models.Preference.get_user_preference')
    def test_no_duplicate_notification(
        self, mock_get_user_preference: Mock,
        mock_notification_filter: Mock,
        mock_send_template: Mock
    ) -> None:
        """Test no duplicate notification is sent."""

        mock_preference = MagicMock()
        mock_preference.get_next_expiration_threshold.return_value = 10
        mock_get_user_preference.return_value = mock_preference

        mock_notification_filter.return_value.exists.return_value = True

        self.user.date_joined = date.today() - timedelta(days=20)
        self.request.get_days_until_expire.return_value = 15

        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            send_expiry_notification(self.user, self.request)
            self.assertRegex(
                log.output[-1],
                '.*Skipping expiry notification .* Notification already sent for threshold.*'
            )

        mock_send_template.assert_not_called()
