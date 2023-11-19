#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys

from django.core.management import execute_from_command_line


def main():
    """Parse the commandline and run administrative tasks."""

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keystone_api.main.settings')
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
