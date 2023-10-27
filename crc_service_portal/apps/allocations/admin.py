from django.contrib import admin

from .models import *


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    """Admin interface for the `Cluster` model"""

    @staticmethod
    @admin.action
    def enable_selected_clusters(modeladmin, request, queryset) -> None:
        """Mark selected clusters as enabled"""

        queryset.update(enabled=True)

    @staticmethod
    @admin.action
    def disable_selected_clusters(modeladmin, request, queryset) -> None:
        """Mark selected clusters as disabled"""

        queryset.update(enabled=False)

    list_display = ['enabled', 'name', 'description']
    ordering = ['name']
    list_filter = ['enabled']
    search_fields = ['name']
    actions = [enable_selected_clusters, disable_selected_clusters]


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    """Admin interface for the `Allocation` model"""

    @staticmethod
    @admin.display
    def service_units(obj: Allocation) -> str:
        """Return an allocation's service units formatted as a human friendly string"""

        return f'{obj.sus:,}'

    list_display = ['user', 'cluster', 'expire', 'start', service_units]
    ordering = ['user', 'cluster', '-expire']
    search_fields = ['user', 'cluster']
    list_filter = [
        ('start', admin.DateFieldListFilter),
        ('expire', admin.DateFieldListFilter),
    ]


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    """Admin interface for the `Publication` class"""

    @staticmethod
    @admin.display
    def title(obj: Publication) -> str:
        """Return an allocation's service units formatted as a human friendly string"""

        return obj.get_truncated_title(100)

    list_display = ['user', title, 'date']
    search_fields = ['user', 'title']
    list_filter = [
        ('date', admin.DateFieldListFilter),
    ]


@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'submitted', 'approved']
    search_fields = ['user', 'title']
    ordering = ['submitted']
