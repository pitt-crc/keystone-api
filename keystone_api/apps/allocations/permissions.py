from rest_framework import permissions

from .models import *

__all__ = [
    'IsAdminReadObj',
    'IsAdminWriteObj',
    'IsAuthenticatedReadObj',
    'IsAuthenticatedWriteObj',
    'IsGroupAdminReadObj',
    'IsGroupAdminWriteObj',
    'IsGroupMemberReadObj',
    'IsGroupMemberWriteObj'
]


class CustomBasePermission(permissions.BasePermission):
    """Base permission class for custom permissions.

    Provides simple utility methods for checking request metadata
    """

    def request_is_read(self, request) -> bool:
        """Return whether the incoming HTTP request is a read operation"""

        return request.method in permissions.SAFE_METHODS

    def request_is_write(self, request) -> bool:
        """Return whether the incoming HTTP request is a write operation"""

        return not self.request_is_read(request)

    def user_is_authenticated(self, request) -> bool:
        """Return whether the incoming request is coming from an authenticated account"""

        return request.user.is_authenticated

    def user_is_admin(self, request) -> bool:
        """Return whether the incoming request is coming from an admin account"""

        return request.user.is_staff or request.user.is_superuser


class IsAuthenticatedReadObj(CustomBasePermission):
    """Object level permissions restricting read access to authenticated users

    All write operations are allowed by this permission class.
    """

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        return self.request_is_write(request) or self.user_is_authenticated(request)


class IsAuthenticatedWriteObj(CustomBasePermission):
    """Object level permissions restricting write access to authenticated users

    All read operations are allowed by this permission class.
    """

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        return self.request_is_read(request) or self.user_is_authenticated(request)


class IsGroupMemberReadObj(CustomBasePermission):
    """Object level permissions restricting read access to research group members

    All write operations are allowed by this permission class.
    """

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        if self.request_is_write(request) or self.user_is_admin(request):
            return True

        user = request.user
        obj_group = obj.get_research_group()
        return user.is_authenticated and user in obj_group.get_all_members()


class IsGroupMemberWriteObj(CustomBasePermission):
    """Object level permissions restricting write access to research group members

    All read operations are allowed by this permission class.
    """

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        if self.request_is_read(request) or self.user_is_admin(request):
            return True

        user = request.user
        obj_group = obj.get_research_group()
        return user.is_authenticated and user in obj_group.get_all_members()


class IsGroupAdminReadObj(CustomBasePermission):
    """Object level permissions restricting read access to research grou admins

    All write operations are allowed by this permission class.
    """

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        if self.request_is_write(request) or self.user_is_admin(request):
            return True

        user = request.user
        obj_group = obj.get_research_group()
        return user.is_authenticated and user in obj_group.get_privileged_members()


class IsGroupAdminWriteObj(CustomBasePermission):
    """Object level permissions restricting write access to research group admins

    All read operations are allowed by this permission class.
    """

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        if self.request_is_read(request) or self.user_is_admin(request):
            return True

        user = request.user
        obj_group = obj.get_research_group()
        return user.is_authenticated and user in obj_group.get_privileged_members()


class IsAdminReadObj(CustomBasePermission):
    """Object level permissions restricting read access to admin users

    All write operations are allowed by this permission class.
    """

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        return self.request_is_write(request) or self.user_is_admin(request)


class IsAdminWriteObj(CustomBasePermission):
    """Object level permissions restricting write access to admin users

    All read operations are allowed by this permission class.
    """

    def has_object_permission(self, request, view, obj: RGAffiliatedModel) -> bool:
        """Return whether the incoming HTTP request has permission to access a database record"""

        return self.request_is_read(request) or self.user_is_admin(request)
