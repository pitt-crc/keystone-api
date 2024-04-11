"""Custom permission objects used to manage access to HTTP endpoints.

Permission classes control access to API resources by determining user
privileges for different HTTP operations. They are applied at the view level,
enabling authentication and authorization to secure endpoints based on
predefined access rules.
"""

from rest_framework import permissions

__all__ = [
    'GroupMemberAll',
    'GroupMemberReadGroupAdminWrite'
]

from apps.users.models import ResearchGroup


class CustomPermissionsBase(permissions.BasePermission):

    def get_research_group(self, request) -> ResearchGroup | None:
        try:
            group_id = request.data.get('group', None)
            return ResearchGroup.objects.get(pk=group_id)

        except (ResearchGroup.DoesNotExist, Exception):
            return None


class GroupMemberAll(CustomPermissionsBase):
    def has_permission(self, request, view) -> bool:
        """Return whether the request has permissions to access the requested resource"""

        if request.method in permissions.SAFE_METHODS:
            return True

        research_group = self.get_research_group(request)
        return research_group and request.user in research_group.get_all_members()

    def has_object_permission(self, request, view, obj):
        """Return whether the incoming HTTP request has permission to access a database record"""

        return request.user in obj.group.get_all_members()


class GroupMemberReadGroupAdminWrite(CustomPermissionsBase):

    def has_permission(self, request, view) -> bool:
        """Return whether the request has permissions to access the requested resource"""

        if request.method in permissions.SAFE_METHODS:
            return True

        research_group = self.get_research_group(request)
        return research_group and request.user in research_group.get_privileged_members()

    def has_object_permission(self, request, view, obj):
        """Return whether the incoming HTTP request has permission to access a database record"""

        read_only = request.method in permissions.SAFE_METHODS
        is_group_member = request.user in obj.group.get_all_members()
        is_group_admin = request.user in obj.group.get_privileged_members()
        return is_group_admin or (read_only and is_group_member)
