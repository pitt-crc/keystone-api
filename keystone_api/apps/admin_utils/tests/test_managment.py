"""Tests for custom management commands."""

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class Quickstart(TestCase):
    """Tests for the `quickstart` CLI utility"""

    def test_celery_command(self) -> None:
        """Test the `--celery` flag executes a celery command"""

        with patch('subprocess.Popen') as mock_popen:
            call_command('quickstart', '--celery', '--no-input')
            mock_popen.assert_called_with(
                ['celery', '-A', 'keystone_api.apps.scheduler', 'worker', '-D'])

    def test_gunicorn_command(self) -> None:
        """Test the `--gunicorn` flag executes a gunicorn server command"""

        with patch('subprocess.run') as mock_run:
            call_command('quickstart', '--gunicorn', '--no-input')
            mock_run.assert_called_with(
                ['gunicorn', '--bind', '0.0.0.0:8000', 'keystone_api.main.wsgi:application'], check=True)
