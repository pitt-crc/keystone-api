"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import truncatechars

from apps.users.models import ResearchGroup
from .managers import *

__all__ = ['Allocation', 'Cluster', 'Proposal', 'ProposalReview']


class Cluster(models.Model):
    """A slurm cluster and it's associated management settings"""

    name = models.CharField(max_length=50)
    description = models.TextField(max_length=150, null=True, blank=True)
    enabled = models.BooleanField(default=True)

    def __str__(self) -> str:
        """Return the cluster name as a string"""

        return str(self.name)


class Proposal(models.Model):
    """Project proposal requesting service unit allocations on one or more clusters"""

    group = models.ForeignKey(ResearchGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField(max_length=1600)
    submitted = models.DateField('Submission Date', auto_now=True)
    approved = models.DateField('Approval Date', null=True, blank=True)
    active = models.DateField('Active Date', null=True, blank=True)
    expire = models.DateField('Expiration Date', null=True, blank=True)

    objects = ProposalManager()

    def __str__(self) -> str:
        """Return the proposal title as a string"""

        return truncatechars(self.title, 100)


class Allocation(models.Model):
    """User service unit allocation"""

    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    sus = models.PositiveIntegerField('Service Units')
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)

    objects = AllocationManager()

    def __str__(self) -> str:
        """Return a human-readable summary of the allocation"""

        return f'{self.cluster} allocation for {self.proposal.group}'


class ProposalReview(models.Model):
    """Review feedback for a project proposal"""

    reviewer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    approve = models.BooleanField()
    private_comments = models.CharField(max_length=500, null=True, blank=True)
    public_comments = models.CharField(max_length=500, null=True, blank=True)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)

    objects = ProposalReviewManager()

    def __str__(self) -> str:
        """Return a human-readable identifier for the proposal"""

        return f'{self.reviewer} review for \"{self.proposal.title}\"'
