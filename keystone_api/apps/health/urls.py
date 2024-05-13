"""URL routing for the parent application"""

from django.urls import path

from .views import *

urlpatterns = [
    path('', HealthCheckView.as_view()),
    path('json/', HealthCheckJsonView.as_view()),
    path('prom/', HealthCheckPrometheusView.as_view()),
]
