from django import forms

from .models import *


class AllocationForm(forms.ModelForm):
    """Form for creating or updating a user's SU allocation on a given cluster"""

    class Meta:
        model = Allocation
        fields = "__all__"


class PublicationForm(forms.ModelForm):
    """Form for creating or updating publication metadata"""

    class Meta:
        model = Publication
        fields = "__all__"


class ProjectProposalForm(forms.ModelForm):
    """Form for creating or updating a user proposal"""

    class Meta:
        model = Proposal
        fields = "__all__"
