"""URL routing for the parent application"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'research_products'

api_router = DefaultRouter()
api_router.register(r'publications', PublicationViewSet)
api_router.register(r'grants', GrantViewSet)

urlpatterns = [
    path('', include(api_router.urls)),
]
