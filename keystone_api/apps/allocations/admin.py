"""Extends the builtin Django admin interface for the parent application.

Extends and customizes the site-wide administration utility with
interfaces for managing application database constructs.
"""

from django.conf import settings
from django.contrib import admin

from .models import *

settings.JAZZMIN_SETTINGS['icons'].update({
    'allocations.Cluster': 'fa fa-server',
    'allocations.Allocation': 'fas fa-coins',
    'allocations.Proposal': 'fa fa-file-alt',
})

settings.JAZZMIN_SETTINGS['order_with_respect_to'].extend([
    'allocations.Cluster', 'allocations.Proposal', 'allocations.allocation'
])


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    """Admin interface for the `Cluster` model"""

    @admin.action
    def enable_selected_clusters(self, request, queryset) -> None:
        """Mark selected clusters as enabled"""

        queryset.update(enabled=True)

    @admin.action
    def disable_selected_clusters(self, request, queryset) -> None:
        """Mark selected clusters as disabled"""

        queryset.update(enabled=False)

    list_display = ['enabled', 'name', 'description']
    list_display_links = list_display
    ordering = ['name']
    list_filter = ['enabled']
    search_fields = ['name', 'description']
    actions = [enable_selected_clusters, disable_selected_clusters]


class ProposalReviewInline(admin.StackedInline):
    """Inline admin interface for the `ProposalReview` model"""

    model = ProposalReview
    show_change_link = True
    readonly_fields = ('date_modified',)
    extra = 0


class AllocationInline(admin.TabularInline):
    """Inline admin interface for the `Allocation` model"""

    model = Allocation
    show_change_link = True
    extra = 0


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    """Admin interface for the `Proposal` model"""

    @staticmethod
    @admin.display
    def title(obj: Proposal) -> str:
        """Return a proposal's title as a human/table friendly string"""

        return str(obj)

    @staticmethod
    @admin.display
    def reviews(obj: Proposal) -> int:
        """Return the total number of proposal reviews"""

        return sum(1 for review in obj.proposalreview_set.all())

    @staticmethod
    @admin.display
    def approvals(obj: Proposal) -> int:
        """Return the number of approving proposal reviews"""

        return sum(1 for review in obj.proposalreview_set.all() if review.approve)

    list_display = ['group', title, 'submitted', 'approved', 'active', 'expire', 'reviews', 'approvals']
    list_display_links = list_display
    search_fields = ['title', 'description', 'group__acc_name']
    ordering = ['submitted']
    list_filter = [
        ('submitted', admin.DateFieldListFilter),
        ('approved', admin.DateFieldListFilter),
    ]
    inlines = [AllocationInline, ProposalReviewInline]


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    """Admin interface for the `Allocation` model"""

    @staticmethod
    @admin.display
    def group(obj: Allocation) -> str:
        """Return the username of the PI for the associated proposal"""

        return obj.proposal.group.name

    @staticmethod
    @admin.display
    def proposal_approved(obj: Allocation) -> bool:
        """Return whether the allocation proposal has been marked as approved"""

        return obj.proposal.approved is not None

    @staticmethod
    @admin.display
    def service_units(obj: Allocation) -> str:
        """Return an allocation's service units formatted as a human friendly string"""

        return f'{obj.sus:,}'

    list_display = [group, 'proposal', 'cluster', service_units, proposal_approved]
    list_display_links = list_display
    ordering = ['proposal__group__name', 'cluster']
    search_fields = ['proposal__group__name', 'proposal__title', 'cluster__name']




