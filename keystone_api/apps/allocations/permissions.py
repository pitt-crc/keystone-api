"""Custom permission objects used to manage access to HTTP endpoints."""

from rest_framework import permissions

__all__ = ['StaffWriteAuthenticatedRead']


class StaffWriteAuthenticatedRead(permissions.BasePermission):
    """
    Staff members are given full rad/write permissions. General authenticated
    users are given read-only permissions.
    """

    def has_permission(self, request, view) -> bool:
        """Return whether the request has permissions to access the requested resource"""

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_staff or request.method == 'TRACE'
