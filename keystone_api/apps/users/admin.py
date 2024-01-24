"""Extends the builtin Django admin interface for the parent application.

Extends and customizes the site-wide administration utility with
interfaces for managing application database constructs.
"""

import django.contrib.auth.admin
from django.conf import settings
from django.contrib import admin, auth

from .models import *

settings.JAZZMIN_SETTINGS['icons'].update({
    'users.User': 'fa fa-user',
    'users.ResearchGroup': 'fa fa-users',
})

settings.JAZZMIN_SETTINGS['order_with_respect_to'].extend([
    'users.User', 'users.ResearchGroup'
])


@admin.register(User)
class UserAdmin(auth.admin.UserAdmin):
    """Admin interface for managing user accounts"""

    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


@admin.register(ResearchGroup)
class ResearchGroupAdmin(admin.ModelAdmin):
    """Admin interface for managing research group delegates"""

    list_display = ['name', 'pi']
    filter_horizontal = ('admins', 'members')
