"""
A Django management command for quickly migrating/deploying a development server.

This management command streamlines development by providing a single command
to handle database migrations, static file collection, and web server deployment.

## Arguments

| Argument   | Description                                                      |
|------------|------------------------------------------------------------------|
| --static   | Collect static files                                             |
| --migrate  | Run database migrations                                          |
| --celery   | Launch a Celery worker with a Redis backend                      |
| --gunicorn | Run a web server using Gunicorn                                  |
| --no-input | Do not prompt for user input of any kind                         |
"""

import subprocess
from argparse import ArgumentParser

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A helper utility that wraps other common Django commands for easier development"""

    help = 'A helper utility that wraps other common Django commands for easier development'

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-line arguments to the parser

        Args:
          parser: The argument parser instance
        """

        parser.add_argument('--static', action='store_true', help='Collect static files.')
        parser.add_argument('--migrate', action='store_true', help='Run database migrations.')
        parser.add_argument('--celery', action='store_true', help='Launch a background Celery worker.')
        parser.add_argument('--gunicorn', action='store_true', help='Run a web server using Gunicorn.')
        parser.add_argument('--no-input', action='store_false', help='Do not prompt for user input of any kind.')

    def handle(self, *args, **options) -> None:
        """Handle the command execution

        Args:
          *args: Additional positional arguments
          **options: Additional keyword arguments
        """

        if options['migrate']:
            self.stdout.write(self.style.SUCCESS('Running database migrations...'))
            call_command('migrate', no_input=options['no_input'])

        if options['static']:
            self.stdout.write(self.style.SUCCESS('Collecting static files...'))
            call_command('collectstatic', no_input=options['no_input'])

        if options['celery']:
            self.stdout.write(self.style.SUCCESS('Starting Celery worker...'))
            self.run_celery()

        if options['gunicorn']:
            self.stdout.write(self.style.SUCCESS('Starting Gunicorn server...'))
            self.run_gunicorn()

    @staticmethod
    def run_celery() -> None:
        """Start a Celery worker"""

        subprocess.Popen(['redis-server'])
        subprocess.Popen(['celery', '-A', 'keystone_api.apps.scheduler', 'beat', '--scheduler', 'django_celery_beat.schedulers:DatabaseScheduler'])
        subprocess.Popen(['celery', '-A', 'keystone_api.apps.scheduler', 'worker'])

    @staticmethod
    def run_gunicorn(host: str = '0.0.0.0', port: int = 8000) -> None:
        """Start a Gunicorn server

        Args:
          host: The host to bind to
          port: The port to bind to
        """

        command = ['gunicorn', '--bind', f'{host}:{port}', 'keystone_api.main.wsgi:application']
        subprocess.run(command, check=True)
