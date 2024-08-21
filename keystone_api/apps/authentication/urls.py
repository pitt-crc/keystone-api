"""URL routing for the parent application."""

from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('new/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('blacklist/', TokenBlacklistView.as_view()),
]
