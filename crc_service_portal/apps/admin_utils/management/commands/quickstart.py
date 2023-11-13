"""
A Django management command for quickly migrating/deploying a development server.

This management command streamlines development by providing a single command
to handle database migrations, static file collection, and web server deployment.

## Arguments

| Argument   | Description                                                      |
|------------|------------------------------------------------------------------|
| --static   | Collect static files                                             |
| --migrate  | Run database migrations                                          |
| --no-input | Do not prompt for user input of any kind                         |
| --gunicorn | Launch a web server using Gunicorn                               |
| --uvicorn  | Launch a web server using Uvicorn                                |
| --host     | Specify the host for the development server (default: '0.0.0.0') |
| --port     | Specify the port for the development server (default: 8000)      |
"""

import subprocess
from argparse import ArgumentParser

from django.core.asgi import get_asgi_application
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'A helper utility for common deployment tasks'

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Add command-line arguments to the parser.

        Args:
          parser (ArgumentParser): The argument parser instance.
        """

        parser.add_argument('--static', action='store_true', help='Collect static files.')
        parser.add_argument('--migrate', action='store_true', help='Run database migrations.')
        parser.add_argument('--no-input', action='store_true', help='Do not prompt for user input of any kind.')

        webserver = parser.add_argument_group('Web Server')
        server_type = webserver.add_mutually_exclusive_group()
        server_type.add_argument('--gunicorn', action='store_true', help='Run a web server using Gunicorn.')
        server_type.add_argument('--uvicorn', action='store_true', help='Run a web server using Uvicorn.')
        parser.add_argument('--host', default='0.0.0.0')
        parser.add_argument('--port', type=int, default=8000)

    def handle(self, *args, **options):
        """Handle the command execution.

        Args:
          *args: Additional positional arguments.
          **options: Additional keyword arguments.

        """

        if options['migrate']:
            self.stdout.write(self.style.SUCCESS('Running database migrations...'))
            call_command('migrate', no_input=options['no_input'])

        if options['static']:
            self.stdout.write(self.style.SUCCESS('Collecting static files...'))
            call_command('collectstatic', no_input=options['no_input'])

        if options['gunicorn']:
            self.stdout.write(self.style.SUCCESS('Starting Gunicorn server...'))
            self.run_gunicorn()

        elif options['uvicorn']:
            self.stdout.write(self.style.SUCCESS('Starting Uvicorn server...'))
            self.run_uvicorn()

    def run_gunicorn(self, host: str = '0.0.0.0', port: int = 8000):
        """Start a Gunicorn server.

        Args:
          host: The host to bind to
          port: The port to bind to
        """

        gunicorn_command = ['gunicorn', '--bind', f'{host}:{port}', 'crc_service_portal.main.wsgi:application', ]
        subprocess.run(gunicorn_command, check=True)

    def run_uvicorn(self, host: str = '0.0.0.0', port: int = 8000):
        """Start a Uvicorn server.

        Args:
          host: The host to bind to
          port: The port to bind to
        """

        import uvicorn
        uvicorn.run(get_asgi_application(), host=host, port=port)
