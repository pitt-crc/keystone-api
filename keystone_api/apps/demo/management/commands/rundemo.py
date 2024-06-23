"""Launch an application server using demo data.

## Arguments

| Argument   | Description                                                      |
|------------|------------------------------------------------------------------|
| --data     | path to JSON demo data                                           |
"""

import tempfile
from argparse import ArgumentParser
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Launch an application server using a temporary database with demo data."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Define command-line arguments

        Args:
            parser: The parser instance to add arguments under
        """

        parser.add_argument('--data', type=Path, help='path to JSON demo data')

    def handle(self, *args, **options):
        """Handle the command execution

        Args:
            *args: Additional positional arguments.
            **options: Additional keyword arguments.
        """

        # Check for demo data at user provided path
        json_file = options['json_file']
        if not json_file.is_file():
            raise CommandError(f'The file "{json_file}" does not exist')

        # Create a temporary SQLite database
        with tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False) as temp_db:
            temp_db_path = Path(temp_db.name)

        try:
            # Configure the settings to use the temporary database
            settings.DATABASES['default'] = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': temp_db_path,
            }

            call_command('migrate')
            call_command(f'loaddata {json_file}')
            call_command('runserver')

        finally:
            if temp_db_path.exists():
                temp_db_path.unlink()
