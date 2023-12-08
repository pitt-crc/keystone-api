"""Extends the builtin Django admin interface for the parent application.

Extends and customizes the site-wide administration utility with
interfaces for managing application database constructs.
"""

from auditlog.models import LogEntry
from django.contrib import admin

# Remove the audit log from the admin dashboard
admin.site.unregister(LogEntry)
