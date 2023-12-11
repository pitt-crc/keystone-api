"""Tests for the `ResearchGroup` model"""

from django.db import IntegrityError
from django.test import TestCase

from apps.users.models import ResearchGroup, User


class GetAllMembers(TestCase):
    """Test fetching all group members via the `get_all_members` member"""

    def setUp(self):
        """Create temporary user accounts for use in tests"""

        self.pi = User.objects.create_user(username='pi')
        self.admin1 = User.objects.create_user(username='admin1')
        self.admin2 = User.objects.create_user(username='admin2')
        self.unprivileged1 = User.objects.create_user(username='unprivileged1')
        self.unprivileged2 = User.objects.create_user(username='unprivileged2')

    def test_pi_only(self) -> None:
        """Test returned group members for a group with a PI only"""

        group = ResearchGroup.objects.create(pi=self.pi)
        expected_members = (self.pi,)
        self.assertEqual(expected_members, group.get_all_members())

    def test_pi_with_admins(self) -> None:
        """Test returned group members for a group with a PI and admins"""

        group = ResearchGroup.objects.create(pi=self.pi)
        group.admins.add(self.admin1)
        group.admins.add(self.admin2)

        expected_members = (self.pi, self.admin1, self.admin2)
        self.assertEqual(expected_members, group.get_all_members())

    def test_pi_with_unprivileged(self) -> None:
        """Test returned group members for a group with a PI and unprivileged users"""

        group = ResearchGroup.objects.create(pi=self.pi)
        group.unprivileged.add(self.unprivileged1)
        group.unprivileged.add(self.unprivileged2)

        expected_members = (self.pi, self.unprivileged1, self.unprivileged2)
        self.assertEqual(expected_members, group.get_all_members())

    def test_pi_with_admin_and_unprivileged(self) -> None:
        """Test returned group members for a group with a PI, admins, and unprivileged users"""

        group = ResearchGroup.objects.create(pi=self.pi)
        group.admins.add(self.admin1)
        group.admins.add(self.admin2)
        group.unprivileged.add(self.unprivileged1)
        group.unprivileged.add(self.unprivileged2)

        expected_members = (self.pi, self.admin1, self.admin2, self.unprivileged1, self.unprivileged2)
        self.assertEqual(expected_members, group.get_all_members())
