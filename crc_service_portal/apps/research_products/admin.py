"""Extends the builtin Django admin interface for the parent application.

Extends and customizes the site-wide administration utility with
interfaces for managing application database constructs.
"""

from django.contrib import admin

from .models import *


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    """Admin interface for the `Publication` class"""

    @staticmethod
    @admin.display
    def title(obj: Publication) -> str:
        """Return a publication's title as a human/table friendly string"""

        return str(obj)

    list_display = ['user', title, 'date']
    search_fields = ['title', 'user__username']
    list_filter = [
        ('date', admin.DateFieldListFilter),
    ]


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    """Admin interface for the `Grant` class"""

    list_display = ['user', 'fiscal_year', 'amount', 'agency', 'start_date', 'end_date']
    ordering = ['user', '-fiscal_year']
    search_fields = ['title', 'agency', 'fiscal_year', 'user__username']
    list_filter = [
        ('start_date', admin.DateFieldListFilter),
        ('end_date', admin.DateFieldListFilter),
    ]
