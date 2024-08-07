"""Run tests with coverage reporting.

## Arguments

| Argument   | Description                                                          |
|------------|----------------------------------------------------------------------|
| test_label | Specify the test label(s) to run. If omitted, all tests will be run. |
| --omit     | Specify patterns to omit from coverage.                              |
| --xml      | Write an XML coverage report to the given file path.                 |
"""

from argparse import ArgumentParser

import coverage
from django.conf import settings
from django.core.management.base import BaseCommand
from django.test.utils import get_runner


class Command(BaseCommand):
    """Run tests with optional coverage reporting."""

    help = "Run tests with optional coverage reporting."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Define command-line arguments.

        Args:
          parser: The parser instance to add arguments under.
        """

        parser.add_argument(
            'test_label',
            nargs='*',
            help='Specify the test label(s) to run. If omitted, all tests will be run.'
        )

        parser.add_argument(
            '--omit',
            nargs='+',
            help='Specify patterns to omit from coverage.'
        )

        parser.add_argument(
            '--xml',
            help='Write an XML coverage report to the given file path.'
        )

    def handle(self, *args, **options) -> None:
        """Handle the command execution

        Args:
          *args: Additional positional arguments.
          **options: Additional keyword arguments.
        """

        cov = coverage.Coverage()
        cov.start()

        TestRunner = get_runner(settings)
        failures = TestRunner().run_tests(options['test_label'])

        cov.stop()
        cov.save()

        if options['xml']:
            cov.xml_report(outfile=options['xml'], omit=options['omit'])

        cov.report(omit=options['omit'])
        if failures:
            exit(1)
