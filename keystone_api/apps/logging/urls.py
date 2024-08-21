"""URL routing for the parent application."""

from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('apps', AppLogViewSet, basename='applog')
router.register('requests', RequestLogViewSet, basename='requestlog')
router.register('tasks', TaskResultViewSet, basename='taskresult')

urlpatterns = router.urls
