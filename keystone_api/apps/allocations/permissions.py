from rest_framework import permissions

from .models import *


class CustomBasePermission(permissions.BasePermission):
    """Base permission class for custom permissions.

    Provides simple utility methods for checking request metadata
    """

    def request_is_read(self) -> bool:
        """Return whether the incoming HTTP request is a read operation"""

        return self.request.method in permissions.SAFE_METHODS

    def request_is_write(self) -> bool:
        """Return whether the incoming HTTP request is a write operation"""

        return not self.request_is_read()

    def user_is_authenticated(self) -> bool:
        return self.request.user.is_authenticated

    def user_is_admin(self) -> bool:
        """Return whether the request is coming from an admin account"""

        return self.request.user.is_staff or self.request.user.is_superuser


class IsAuthenticatedReadObj(CustomBasePermission):
    """Object level permissions restricting read access to authenticated users"""

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        return self.request_is_write() or self.user_is_authenticated()


class IsAuthenticatedWriteObj(CustomBasePermission):
    """Object level permissions restricting write access to authenticated users"""

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        return self.request_is_read() or self.user_is_authenticated()


class IsGroupAdminReadObj(CustomBasePermission):
    """Object level permissions restricting read access to RESEARCH GROUP admins"""

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        if self.request_is_write() or self.user_is_admin():
            return True

        user = self.request.user
        obj_group = obj.get_research_group()
        return user.is_authenticated and user in obj_group.get_privileged_members()


class IsGroupAdminWriteObj(CustomBasePermission):
    """Object level permissions restricting write access to research group admins"""

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        if self.request_is_read() or self.user_is_admin():
            return True

        user = self.request.user
        obj_group = obj.get_research_group()
        return user.is_authenticated and user in obj_group.get_privileged_members()


class IsAdminReadObj(CustomBasePermission):
    """Object level permissions restricting read access to admin users"""

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        return self.request_is_write() or self.user_is_admin()


class IsAdminWriteObj(CustomBasePermission):
    """Object level permissions restricting write access to admin users"""

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        return self.request_is_read() or self.user_is_admin()
