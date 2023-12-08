"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.contrib.auth import models as auth_model
from django.db import models

__all__ = ['ResearchGroup', 'Group', 'User']


class User(auth_model.User):
    """Proxy model for the built-in django `User` model"""

    class Meta:
        proxy = True


class Group(auth_model.Group):
    """Proxy model for the built-in django `Group` model"""

    class Meta:
        proxy = True


class Permission(auth_model.Permission):
    """Proxy model for the built-in django `Permission` model"""

    class Meta:
        proxy = True


class ResearchGroup(models.Model):
    """A user research group tied to a slurm account"""

    acc_name = models.CharField(max_length=255)
    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_group_pi')
    admins = models.ManyToManyField(User, related_name='research_group_admins')

    def __str__(self) -> str:
        """Return the research group's account name"""

        return str(self.acc_name)
