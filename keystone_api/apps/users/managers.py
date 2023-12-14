"""Custom database managers for encapsulating repeatable table queries.

Manager classes encapsulate common database operations at the table level (as
opposed to the level of individual records). At least one Manager exists for
every database model. Managers are commonly exposed as an attribute of the
associated model class called `objects`.
"""

from django.contrib.auth.models import User
from django.db import models

__all__ = ['ResearchGroupManager']


class ResearchGroupManager(models.Manager):
    """Object manager for the `ResearchGroup` database model"""

    def groups_for_user(self, user: User) -> models.QuerySet:
        """Get all research groups the user is affiliated with

        Args:
            user: The user to return groups for

        Return:
            A filtered queryset
        """

        return self.get_queryset().filter(models.Q(pi=user.id) | models.Q(admins=user.id) | models.Q(members=user.id))

    def groups_for_admin(self, user: User) -> models.QuerySet:
        """Get all research groups the user has admin privileges for

        Args:
            user: The user to return groups for

        Return:
            A filtered queryset
        """

        return self.get_queryset().filter(models.Q(pi=user.id) | models.Q(admins=user.id))

    def groups_for_pi(self, user: User) -> models.QuerySet:
        """Get all research groups the user is a PI for

        Args:
            user: The user to return groups for

        Return:
            A filtered queryset
        """

        return self.get_queryset().filter(models.Q(pi=user.id))
