"""URL routing for the parent application"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'research_products'

api_router = DefaultRouter()
api_router.register(r'clusters', PublicationViewSet)
api_router.register(r'allocations', GrantViewSet)

urlpatterns = [
    path('api/', include(api_router.urls)),
]
