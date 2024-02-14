"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

import abc

from django.db import models
from django.template.defaultfilters import truncatechars

from apps.users.models import ResearchGroup, User
from .managers import *

__all__ = ['Allocation', 'Cluster', 'Proposal', 'ProposalReview', 'RGAffiliatedModel']


class RGAffiliatedModel:
    """Interface class for database models affiliated with a research group"""

    @abc.abstractmethod
    def get_research_group(self) -> ResearchGroup:
        """Return the research group tied to the current record"""


class Cluster(models.Model):
    """A slurm cluster and it's associated management settings"""

    name = models.CharField(max_length=50)
    description = models.TextField(max_length=150, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    api_url = models.CharField(max_length=1000)
    api_user = models.CharField(max_length=150)
    api_token = models.CharField(max_length=200)

    def __str__(self) -> str:
        """Return the cluster name as a string"""

        return str(self.name)


class Proposal(RGAffiliatedModel, models.Model):
    """Project proposal requesting service unit allocations on one or more clusters"""

    title = models.CharField(max_length=250)
    description = models.TextField(max_length=1600)
    submitted = models.DateField('Submission Date', auto_now=True)
    approved = models.DateField('Approval Date', null=True, blank=True)
    active = models.DateField('Active Date', null=True, blank=True)
    expire = models.DateField('Expiration Date', null=True, blank=True)

    group: ResearchGroup = models.ForeignKey(ResearchGroup, on_delete=models.CASCADE)

    objects = ProposalManager()

    def get_research_group(self) -> ResearchGroup:
        """Return the research group tied to the current record"""

        return self.group

    def __str__(self) -> str:
        """Return the proposal title as a string"""

        return truncatechars(self.title, 100)


class Allocation(RGAffiliatedModel, models.Model):
    """User service unit allocation"""

    requested = models.PositiveIntegerField('Requested Service Units')
    awarded = models.PositiveIntegerField('Awarded Service Units', null=True, blank=True)
    final = models.PositiveIntegerField('Final Usage', null=True, blank=True)
    is_contributing = models.BooleanField('Included in Current Usage Limit', default=False)

    cluster: Cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    proposal: Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)

    objects = AllocationManager()

    def get_research_group(self) -> ResearchGroup:
        """Return the research group tied to the current record"""

        return self.proposal.group

    def __str__(self) -> str:
        """Return a human-readable summary of the allocation"""

        return f'{self.cluster} allocation for {self.proposal.group}'


class ProposalReview(RGAffiliatedModel, models.Model):
    """Review feedback for a project proposal"""

    approve = models.BooleanField()
    public_comments = models.CharField(max_length=500, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True)

    proposal: Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    reviewer: User = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = ProposalReviewManager()

    def get_research_group(self) -> ResearchGroup:
        """Return the research group tied to the current record"""

        return self.proposal.group

    def __str__(self) -> str:
        """Return a human-readable identifier for the proposal"""

        return f'{self.reviewer} review for \"{self.proposal.title}\"'
