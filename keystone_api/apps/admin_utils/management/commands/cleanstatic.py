"""A Django management command for deleting static files in development."""

import shutil

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Developer utility to delete the static file directories"""

    help = 'Delete the static root and media root directories'

    def handle(self, *args, **options) -> None:
        """Handle the command execution

        Args:
          *args: Additional positional arguments
          **options: Additional keyword arguments
        """

        shutil.rmtree(settings.STATIC_ROOT)
        shutil.rmtree(settings.MEDIA_ROOT)
