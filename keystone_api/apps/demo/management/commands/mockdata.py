"""Generate mock application data.

## Arguments

| Argument   | Description                                                      |
|------------|------------------------------------------------------------------|
| --indent   | JSON indentation level                                           |
"""

from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from apps.demo.mock import *


class Command(BaseCommand):
    """Randomly generate mock application data."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Define command-line arguments

        Args:
            parser: The parser instance to add arguments under
        """

        json_group = parser.add_argument_group('JSON formatting')
        json_group.add_argument('--indent', type=int, default=2, help='JSON indentation level')

    def handle(self, *args, **options):
        """Handle the command execution

        Args:
            *args: Additional positional arguments.
            **options: Additional keyword arguments.
        """

        data = []
        data.extend(ClusterMocker() for _ in range(4))
        data.extend(AllocationMocker() for _ in range(20))
        data.extend(AllocationRequestMocker() for _ in range(5))
        data.extend(AllocationRequestReviewMocker() for _ in range(5))
        print(json.dumps(data, cls=MockerEncoder, indent=options['indent']))
