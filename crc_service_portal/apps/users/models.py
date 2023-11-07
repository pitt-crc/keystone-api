"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.contrib.auth import models as auth_model
from django.db import models


class User(auth_model.User):
    """Proxy model for the builtin django `User` model"""

    class Meta:
        proxy = True


class ResearchGroup(models.Model):
    """User membership in research groups"""

    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='researchgroup_pi')
    delegates = models.ManyToManyField(User, related_name='researchgroup_delegates')
