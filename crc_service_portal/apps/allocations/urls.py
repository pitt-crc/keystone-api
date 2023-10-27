from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'allocations'

api_router = DefaultRouter()
api_router.register(r'clusters', ClusterViewSet)
api_router.register(r'allocations', AllocationViewSet)
api_router.register(r'proposals', ProjectProposalViewSet)
api_router.register(r'publications', PublicationViewSet)

urlpatterns = [
    path('api/', include(api_router.urls)),
    path('allocations', AllocationsView.as_view(), name='allocations'),
    path('proposals', ProposalsView.as_view(), name='proposals'),
    path('publications', PublicationsView.as_view(), name='publications'),
]
