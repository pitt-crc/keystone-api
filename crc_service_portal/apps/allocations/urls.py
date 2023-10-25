from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'allocations'

api_router = DefaultRouter()
api_router.register(r'allocations', views.AllocationViewSet)
api_router.register(r'project-proposals', views.ProjectProposalViewSet)
api_router.register(r'publications', views.PublicationViewSet)

urlpatterns = [
    path('api/', include(api_router.urls)),
    path('allocations', views.AllocationView.as_view(), name='allocations'),
]
