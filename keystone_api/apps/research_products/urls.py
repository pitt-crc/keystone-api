"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'research_products'

router = DefaultRouter()
router.register(r'publications', PublicationViewSet, basename='publication')
router.register(r'grants', GrantViewSet, basename='grant')

urlpatterns = router.urls
