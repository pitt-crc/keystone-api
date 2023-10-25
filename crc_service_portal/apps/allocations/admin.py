from django.contrib import admin

from . import models

admin.site.register(models.Cluster)


@admin.register(models.Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'cluster', 'expire', 'sus')


@admin.register(models.ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = ('submitter', 'title', 'funding_agency')
    filter_horizontal = ('allocations',)


@admin.register(models.Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'publication_date', 'preprint')
