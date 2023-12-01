#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import sys

from django.core.management import execute_from_command_line


def main():
    """Parse the commandline and run administrative tasks."""

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
