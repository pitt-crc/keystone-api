from django import forms

from . import models


class ClusterForm(forms.ModelForm):
    """Form for creating or updating a Slurm cluster metadata"""

    class Meta:
        model = models.Cluster
        fields = ('name',)


class AllocationForm(forms.ModelForm):
    """Form for creating or updating a user's SU allocation on a given cluster"""

    class Meta:
        model = models.Allocation
        fields = ('user', 'cluster', 'expire', 'sus')


class ProjectProposalForm(forms.ModelForm):
    """Form for creating or updating a user project proposal"""

    class Meta:
        model = models.ProjectProposal
        fields = ('submitter', 'allocations', 'title', 'funding_agency', 'project_description')


class PublicationForm(forms.ModelForm):
    """Form for creating or updating publication metadata"""

    class Meta:
        model = models.Publication
        fields = (
            'title', 'user', 'author_names', 'publication_date', 'abstract',
            'journal', 'volume', 'page_numbers', 'doi', 'link', 'preprint'
        )
