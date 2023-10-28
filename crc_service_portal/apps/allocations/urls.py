"""URL routing for the parent application"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'allocations'

api_router = DefaultRouter()
api_router.register(r'clusters', ClusterViewSet)
api_router.register(r'allocations', AllocationViewSet)
api_router.register(r'proposals', ProposalViewSet)

urlpatterns = [
    path('api/', include(api_router.urls)),
    path('allocations', AllocationsView.as_view(), name='allocations'),
]
