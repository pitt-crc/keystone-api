from rest_framework import permissions

from apps.allocations.models import RGAffiliatedModel

__all__ = ['StaffWriteAuthenticatedRead', 'StaffWriteGroupRead']


class StaffWriteAuthenticatedRead(permissions.BasePermission):
    """Allows write access for staff members and read-only access for all other authenticated users"""

    def has_permission(self, request, view):
        """Return whether the request has permissions to access the requested resource"""

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_staff or request.method == 'TRACE'


class StaffWriteGroupRead(permissions.BasePermission):

    def has_permission(self, request, view):
        """Return whether the request has permissions to access the requested resource"""

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_staff or request.method == 'TRACE'

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        if request.user.is_staff or request.method == 'TRACE':
            return True

        user_is_in_group = request.user in obj.get_research_group().get_all_members()
        return request.method in permissions.SAFE_METHODS and user_is_in_group
