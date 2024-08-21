"""URL routing for the parent application."""

from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'publications', PublicationViewSet)
router.register(r'grants', GrantViewSet)

urlpatterns = router.urls
