"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', ResearchGroupViewSet)

urlpatterns = router.urls
