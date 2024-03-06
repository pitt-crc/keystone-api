"""
A Django management command for synchronizing research group data with Slurm.

New groups are created as necessary and existing groups are updated to
reflect their corresponding Slurm associations.

"""
from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from apps.users.tasks import slurm_update_research_groups


class Command(BaseCommand):
    """Create/update research groups to reflect changes made in Slurm"""

    help = 'Create/update research groups to reflect changes made in Slurm'

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-line arguments to the parser

        Args:
          parser: The argument parser instance
        """

        parser.add_argument('--prune', action='store_true', help='delete any research groups with names not found in Slurm')

    def handle(self, *args, **options) -> None:
        """Handle the command execution"""

        try:
            slurm_update_research_groups(prune=options['prune'])

        except KeyboardInterrupt:
            pass
