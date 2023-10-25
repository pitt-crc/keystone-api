from django.contrib.auth import get_user_model
from django.db import models


class Cluster(models.Model):
    """A slurm cluster"""

    name = models.CharField(max_length=100)


class Allocation(models.Model):
    """User service unit allocation"""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    expire = models.DateField(null=True, blank=True)
    sus = models.IntegerField()


class ProjectProposal(models.Model):
    """Project proposal requesting service unit allocations on one or more clusters"""

    submitter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    allocations = models.ManyToManyField(Allocation)
    title = models.CharField(max_length=250)
    funding_agency = models.CharField(max_length=100, null=True, blank=True)
    project_description = models.TextField(max_length=1600, null=True, blank=True)


class Publication(models.Model):
    """User submitted information for academic publication"""

    title = models.CharField(max_length=200)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    author_names = models.TextField()
    publication_date = models.DateField()
    abstract = models.TextField()
    journal = models.CharField(max_length=100, null=True, blank=True)
    volume = models.CharField(max_length=20, null=True, blank=True)
    page_numbers = models.CharField(max_length=20, null=True, blank=True)
    doi = models.CharField(max_length=50, unique=True, null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True)
    preprint = models.BooleanField(default=False)
