"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.db import models
from django.template.defaultfilters import truncatechars

from apps.users.models import ResearchGroup
from .managers import *

__all__ = ['Grant', 'Publication']


class Publication(models.Model):
    """Metadata for an academic publication"""

    group = models.ForeignKey(ResearchGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    abstract = models.TextField()
    date = models.DateField('Publication Date')
    journal = models.CharField(max_length=100)
    doi = models.CharField(max_length=50, unique=True, null=True, blank=True)

    objects = PublicationManager()

    def __str__(self) -> str:
        """Return the publication title truncated to 50 characters"""

        return truncatechars(self.title, 100)


class Grant(models.Model):
    """Metadata for a funding grant"""

    group = models.ForeignKey(ResearchGroup, on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(decimal_places=2, max_digits=19)
    agency = models.CharField(max_length=100)
    title = models.CharField(max_length=250)

    objects = GrantManager()

    def __str__(self) -> str:
        """Return the grant title truncated to 50 characters"""

        return truncatechars(self.title, 100)
