"""Command-line utility for executing administrative tasks."""

import sys
from warnings import warn

from django.core.management import execute_from_command_line


def main() -> None:
    """Parse the commandline and run administrative tasks."""

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    warn("You are calling `manage.py' directly. Use the bundled `keystone-api` command instead.", RuntimeWarning)
    main()
