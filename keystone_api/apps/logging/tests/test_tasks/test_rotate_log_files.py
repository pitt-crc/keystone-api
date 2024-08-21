"""Unit tests for the `rotate_log_files` task."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from django.test import override_settings, TestCase
from django.utils.timezone import now

from apps.logging.models import AppLog, RequestLog
from apps.logging.tasks import rotate_log_files


class LogFileDeletion(TestCase):
    """Test the deletion of log records."""

    def create_dummy_records(self, timestamp: datetime) -> None:
        """Create a single record in each logging database table.

        Args:
            timestamp: The creation time of the records.
        """

        AppLog.objects.create(
            name='mock.log.test',
            level=10,
            pathname='/test',
            lineno=100,
            message='This is a log',
            time=timestamp
        )

        RequestLog.objects.create(
            endpoint='/api',
            response_code=200,
            body_request='',
            body_response='',
            time=timestamp
        )

    @override_settings(LOG_RECORD_ROTATION=4)
    @patch('django.utils.timezone.now')
    def test_log_files_rotated(self, mock_now: Mock) -> None:
        """Test expired log files are deleted."""

        # Mock the current time
        initial_time = now()
        mock_now.return_value = initial_time

        # Create an older set of records
        self.create_dummy_records(timestamp=initial_time)

        # Simulate the passage of time
        later_time = initial_time + timedelta(seconds=5)
        mock_now.return_value = later_time

        # Create a newer set of records
        self.create_dummy_records(timestamp=later_time)

        # Ensure records exist
        self.assertEqual(2, AppLog.objects.count())
        self.assertEqual(2, RequestLog.objects.count())

        # Run rotation
        rotate_log_files()

        # Assert only the newer records remain
        self.assertEqual(1, AppLog.objects.count())
        self.assertEqual(1, RequestLog.objects.count())

    @override_settings(LOG_RECORD_ROTATION=0)
    def test_rotation_disabled(self) -> None:
        """Test log files are not deleted when rotation is disabled."""

        self.create_dummy_records(now())

        rotate_log_files()
        self.assertEqual(1, AppLog.objects.count())
        self.assertEqual(1, RequestLog.objects.count())
