"""Unit tests for the `AllocationViewSet` class."""

from typing import Any
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.allocations.views import AllocationViewSet


class GetQueryset(TestCase):
    """Test the generation of database queries based on user permissions."""

    def setUp(self) -> None:
        """Create a new viewset instance."""

        self.viewset = AllocationViewSet()

    @patch('apps.allocations.models.Allocation.objects.filter')
    @patch('apps.users.models.ResearchGroup.objects.groups_for_user')
    def test_get_queryset_for_non_staff_user(self, mock_groups_for_user: Any, mock_filtered_allocations: Any) -> None:
        """Test non-staff users can only query allocations for their own research groups."""

        # Mock request and user
        request = MagicMock()
        request.user.is_staff = False
        self.viewset.request = request

        # Generate the DB query
        mock_groups_for_user.return_value = ['group1', 'group2']
        queryset = self.viewset.get_queryset()

        # Assert the queryset returned is filtered by user's research groups
        self.assertEqual(queryset, mock_filtered_allocations.return_value)
        mock_groups_for_user.assert_called_once_with(request.user)
        mock_filtered_allocations.assert_called_once_with(request__group__in=['group1', 'group2'])
