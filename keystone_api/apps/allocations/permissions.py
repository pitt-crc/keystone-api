"""Custom permission objects used to manage access to HTTP endpoints.

Permission classes control access to API resources by determining user
privileges for different HTTP operations. They are applied at the view level,
enabling authentication and authorization to secure endpoints based on
predefined access rules.
"""

from rest_framework import permissions

from .models import RGAffiliatedModel

__all__ = ['StaffWriteAuthenticatedRead', 'StaffWriteGroupRead']


class StaffWriteAuthenticatedRead(permissions.BasePermission):
    """
    Read access is granted to all authenticated users.
    Staff users retain all read/write permissions.
    """

    def has_permission(self, request, view) -> bool:
        """Return whether the request has permissions to access the requested resource"""

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_staff


class StaffWriteGroupRead(permissions.BasePermission):
    """
    Read access is granted to all users belonging to the same research group
    as the requested object. Staff users retain all read/write permissions.
    """

    def has_permission(self, request, view) -> bool:
        """Return whether the request has permissions to access the requested resource"""

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_staff

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        if request.user.is_staff:
            return True

        user_is_in_group = request.user in obj.get_research_group().get_all_members()
        return request.method in permissions.SAFE_METHODS and user_is_in_group
