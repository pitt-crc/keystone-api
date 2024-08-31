"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.contrib.auth import models as auth_models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone

from .managers import *

__all__ = ['ResearchGroup', 'User']


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    """Proxy model for the built-in django `User` model."""

    # These values should always be defined when extending AbstractBaseUser
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    # User metadata
    username = models.CharField(max_length=150, unique=True, validators=[UnicodeUsernameValidator()])
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=150, null=True)
    last_name = models.CharField(max_length=150, null=True)
    email = models.EmailField(null=True)
    department = models.CharField(max_length=1000, null=True, blank=True)
    role = models.CharField(max_length=1000, null=True, blank=True)

    # Administrative values for user management/permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField('staff status', default=False)
    is_ldap_user = models.BooleanField('LDAP User', default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True)

    objects = UserManager()


class ResearchGroup(models.Model):
    """A user research group tied to a slurm account."""

    name = models.CharField(max_length=255, unique=True)
    pi = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='research_group_pi')
    admins = models.ManyToManyField(User, related_name='research_group_admins', blank=True)
    members = models.ManyToManyField(User, related_name='research_group_unprivileged', blank=True)
    is_active = models.BooleanField(default=True)

    objects = ResearchGroupManager()

    def get_all_members(self) -> models.QuerySet:
        """Return a queryset of all research group members."""

        return User.objects.filter(
            models.Q(pk=self.pi.pk) |
            models.Q(pk__in=self.admins.values_list('pk', flat=True)) |
            models.Q(pk__in=self.members.values_list('pk', flat=True))
        )

    def get_privileged_members(self) -> models.QuerySet:
        """Return a queryset of all research group members with admin privileges."""

        return User.objects.filter(
            models.Q(pk=self.pi.pk) |
            models.Q(pk__in=self.admins.values_list('pk', flat=True))
        )

    def __str__(self) -> str:  # pragma: nocover  # pragma: nocover
        """Return the research group's account name."""

        return str(self.name)
