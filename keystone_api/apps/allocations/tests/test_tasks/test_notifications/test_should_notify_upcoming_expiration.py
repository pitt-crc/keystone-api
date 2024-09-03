"""Unit tests for the `send_expiry_notification` function."""

from datetime import date, timedelta
from unittest.mock import Mock, patch

from django.test import TestCase

from apps.allocations.models import AllocationRequest
from apps.allocations.tasks import should_notify_upcoming_expiration
from apps.notifications.models import Preference
from apps.users.models import ResearchGroup, User


class ShouldSend(TestCase):
    """Test the determination of whether an expiry threshold notification should be sent."""

    def setUp(self):
        """Set up test data."""

        self.user = User.objects.create_user(username='testuser', password='foobar123!')
        self.group = ResearchGroup.objects.create(pi=self.user)
        self.request = AllocationRequest.objects.create(group=self.group)

    def test_false_if_request_does_not_expire(self) -> None:
        """Test the return value is `False` if the request does not expire."""

        self.user.date_joined = date(2020, 1, 1)
        self.request.expire = None

        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            self.assertFalse(should_notify_upcoming_expiration(self.user, self.request))
            self.assertRegex(log.output[-1], '.*Request does not expire.')

    def test_false_if_request_already_expired(self) -> None:
        """Test the return value is `False` if the request has already expired."""

        self.user.date_joined = date(2020, 1, 1)
        self.request.expire = date.today()

        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            self.assertFalse(should_notify_upcoming_expiration(self.user, self.request))
            self.assertRegex(log.output[-1], '.*Request has already expired.')

    def test_false_if_no_threshold_reached(self) -> None:
        """Test the return value is `False` if no threshold is reached."""

        # Set notification threshold smaller than days to expiration
        self.user.date_joined = date(2020, 1, 1)
        self.request.expire = date.today() + timedelta(days=15)
        Preference.objects.create(user=self.user, request_expiry_thresholds=[5])

        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            self.assertFalse(should_notify_upcoming_expiration(self.user, self.request))
            self.assertRegex(log.output[-1], '.*No notification threshold has been hit yet.')

    def test_false_if_user_recently_joined(self) -> None:
        """Test the return value is `False` if the user recently joined."""

        # Set notification threshold equal to days to expiration
        self.user.date_joined = date.today()
        self.request.expire = date.today() + timedelta(days=15)
        Preference.objects.create(user=self.user, request_expiry_thresholds=[15])

        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            self.assertFalse(should_notify_upcoming_expiration(self.user, self.request))
            self.assertRegex(log.output[-1], '.*User account created after notification threshold.')

    @patch('apps.notifications.models.Notification.objects.filter')
    def test_no_duplicate_notification(self, mock_notification_filter: Mock) -> None:
        """Test no duplicate notification is sent."""

        # Set notification threshold smaller than days to expiration
        self.user.date_joined = date(2020, 1, 1)
        self.request.expire = date.today() + timedelta(days=5)
        Preference.objects.create(user=self.user, request_expiry_thresholds=[5])
        mock_notification_filter.return_value.exists.return_value = True

        with self.assertLogs('apps.allocations.tasks', level='DEBUG') as log:
            self.assertFalse(should_notify_upcoming_expiration(self.user, self.request))
            self.assertRegex(log.output[-1], '.*Notification already sent for threshold.')
