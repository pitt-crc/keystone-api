"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'allocations'

router = DefaultRouter()
router.register(r'clusters', ClusterViewSet, basename='Cluster')
router.register(r'allocations', AllocationViewSet, basename='Allocation')
router.register(r'proposals', ProposalViewSet, basename='Proposal')
router.register(r'proposal-reviews', ProposalReviewViewSet, basename='ProposalReview')

urlpatterns = router.urls
