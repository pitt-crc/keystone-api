"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'researchgroups', ResearchGroupViewSet, basename='researchgroup')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls
