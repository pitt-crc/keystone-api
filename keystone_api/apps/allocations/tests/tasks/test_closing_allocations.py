"""Tests for the allocation closing step of the `update_limits` task."""

from datetime import date

from django.db.models import Sum
from django.test import TestCase
from freezegun import freeze_time

from apps.allocations.models import *
from apps.allocations.tasks import close_expired_allocations


class ClosingAllocations(TestCase):
    """Test various scenarios for updating the usage limit of an account"""

    fixtures = ['single_research_group_multi_requests.yaml']

    def setUp(self):
        """Provide some basic queries used leading up to closing allocations during limit updating"""

        # Base query for approved Allocations under the given account on the given cluster
        self.acct_alloc_query = Allocation.objects.filter(request__group=1,
                                                          cluster=Cluster.objects.get(name="cluster"),
                                                          request__status='AP')
        self.historical_usage = self.acct_alloc_query.filter(request__expire__lte=date.today()).aggregate(Sum("final"))['final__sum'] or 0

    def test_closing_single_allocation(self, **kwargs) -> None:
        """Ensure closing a single allocation result in the correct current usage, and that the allocation's final usage is set"""
        with freeze_time("2024-01-03"):
            # Query for allocations that have expired but do not have a final usage value
            closing_query = self.acct_alloc_query \
                .filter(final=None, request__expire__lte=date.today()) \
                .order_by("request__expire")
            current_usage = close_expired_allocations(closing_query.all(), 30000 - self.historical_usage)

            self.assertEqual(current_usage, 10000)
            self.assertEqual(Allocation.objects.get(pk=2).final, 10000)

    def test_closing_multiple_allocations(self, **kwargs) -> None:
        """Ensure closing multiple allocations results in the correct current usage, and that the final usage values are set"""
        with freeze_time("2024-01-04"):
            self.assertEqual(date.today(), date(year=2024, month=1, day=4))
            # Query for allocations that have expired but do not have a final usage value
            closing_query = self.acct_alloc_query \
                .filter(final=None, request__expire__lte=date.today()) \
                .order_by("request__expire")
            current_usage = close_expired_allocations(closing_query.all(), 30000 - self.historical_usage)

            self.assertEqual(current_usage, 0)
            self.assertEqual(Allocation.objects.get(pk=1).final, 10000)
            self.assertEqual(Allocation.objects.get(pk=2).final, 10000)

