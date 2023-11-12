"""URL routing for the parent application"""

from django.urls import path

from .views import *

app_name = 'docs'

urlpatterns = [
    path('openapi', SchemaView, name='openapi-schema'),
    path('', RedocView, name='redoc'),
]
