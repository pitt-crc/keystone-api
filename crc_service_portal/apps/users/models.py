"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.contrib.auth import models as auth_model
from django.db import models

__all__ = ['User', 'Group', 'Delegate']


class User(auth_model.User):
    """Proxy model for the built-in django `User` model"""

    class Meta:
        proxy = True


class Group(auth_model.Group):
    """Proxy model for the built-in django `Group` model"""

    class Meta:
        proxy = True


class Delegate(models.Model):
    """Delegated user permissions where PI's allow other users to work in their stead"""

    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delegate_pi')
    delegates = models.ManyToManyField(User, related_name='delegate_delegates')

    def __str__(self) -> str:
        self.pi: User
        return f'Delegates for {self.pi.username}'
