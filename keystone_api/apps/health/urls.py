"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'health'

router = DefaultRouter()
router.register('', HealthCheckJsonViewSet, basename='health')
router.register('json', HealthCheckJsonViewSet, basename='health-json')
router.register('prometheus', HealthCheckPrometheusViewSet, basename='health-prometheus')

urlpatterns = router.urls
