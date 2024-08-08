"""Tests for the `IsGroupAdminOrReadOnly` class."""

from django.test import RequestFactory, TestCase

from apps.users.models import User
from apps.users.permissions import IsGroupAdminOrReadOnly


class HasPermission(TestCase):
    """Test the `has_permission` method"""

    def setUp(self) -> None:
        """Create user accounts with varying permissions"""

        self.factory = RequestFactory()
        self.permission = IsGroupAdminOrReadOnly()
        self.staff_user = User.objects.create(username='staffuser', is_staff=True)
        self.regular_user = User.objects.create(username='regularuser', is_staff=False)

    def test_has_permission_for_trace_request_as_staff(self) -> None:
        """Test that staff users have permission for TRACE requests."""

        request = self.factory.trace('/')
        request.user = self.staff_user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_for_trace_request_as_non_staff(self) -> None:
        """Test that non-staff users do not have permission for TRACE requests."""

        request = self.factory.trace('/')
        request.user = self.regular_user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_has_permission_for_non_trace_request(self) -> None:
        """Test that all users have permission for non-TRACE requests."""

        request = self.factory.get('/')
        request.user = self.regular_user
        self.assertTrue(self.permission.has_permission(request, None))
