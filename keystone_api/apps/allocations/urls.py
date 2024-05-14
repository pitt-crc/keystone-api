"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('clusters', ClusterViewSet, basename='cluster')
router.register('allocations', AllocationViewSet, basename='allocation')
router.register('requests', AllocationRequestViewSet, basename='allocationrequest')
router.register('reviews', AllocationRequestReviewViewSet, basename='allocationrequestreview')

urlpatterns = router.urls
