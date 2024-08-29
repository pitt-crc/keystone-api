"""Unit tests for the `AllocationManager` class."""

from datetime import date, timedelta

from django.test import TestCase

from apps.allocations.models import *
from apps.users.models import *


class GetAllocationData(TestCase):
    """Test get methods used to retrieve allocation metadata/status."""

    def setUp(self) -> None:
        """Create test data."""

        self.user = User.objects.create(username="user", password='foobar123!')
        self.group = ResearchGroup.objects.create(name="Research Group 1", pi=self.user)
        self.cluster = Cluster.objects.create(name="Test Cluster")

        self.allocation_request = AllocationRequest.objects.create(
            group=self.group,
            status='AP',
            active=date.today() - timedelta(days=10),
            expire=date.today() + timedelta(days=10)
        )

        self.expired_request = AllocationRequest.objects.create(
            group=self.group,
            status='AP',
            active=date.today() - timedelta(days=20),
            expire=date.today() - timedelta(days=5)
        )

        self.allocation = Allocation.objects.create(
            requested=1000,
            awarded=800,
            final=700,
            cluster=self.cluster,
            request=self.allocation_request
        )

        self.expired_allocation = Allocation.objects.create(
            requested=1000,
            awarded=600,
            final=500,
            cluster=self.cluster,
            request=self.expired_request
        )

    def test_approved_allocations(self) -> None:
        """Test the `approved_allocations` method returns only approved allocations."""

        qs = Allocation.objects.approved_allocations(account=self.group, cluster=self.cluster)
        self.assertIn(self.allocation, qs)
        self.assertIn(self.expired_allocation, qs)
        self.assertEqual(qs.count(), 2)

    def test_active_allocations(self) -> None:
        """Test the `active_allocations` method returns only active allocations."""

        qs = Allocation.objects.active_allocations(account=self.group, cluster=self.cluster)
        self.assertIn(self.allocation, qs)
        self.assertNotIn(self.expired_allocation, qs)
        self.assertEqual(qs.count(), 1)

    def test_expired_allocations(self) -> None:
        """Test the `expired_allocations` method returns only expired allocations."""

        qs = Allocation.objects.expired_allocations(account=self.group, cluster=self.cluster)
        self.assertIn(self.expired_allocation, qs)
        self.assertNotIn(self.allocation, qs)
        self.assertEqual(qs.count(), 1)

    def test_active_service_units(self) -> None:
        """Test the `active_service_units` method returns the total awarded service units for active allocations."""

        total_units = Allocation.objects.active_service_units(account=self.group, cluster=self.cluster)
        self.assertEqual(total_units, 800)

    def test_expired_service_units(self) -> None:
        """Test the `expired_service_units` method returns the total awarded service units for expired allocations."""

        total_units = Allocation.objects.expired_service_units(account=self.group, cluster=self.cluster)
        self.assertEqual(total_units, 600)

    def test_historical_usage(self) -> None:
        """Test the `historical_usage` method returns the total final usage for expired allocations."""

        usage = Allocation.objects.historical_usage(account=self.group, cluster=self.cluster)
        self.assertEqual(usage, 500)
