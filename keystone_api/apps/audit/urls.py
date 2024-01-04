"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'audit'

router = DefaultRouter()
router.register('log', LogEntryViewSet)

urlpatterns = router.urls
