"""URL routing for the parent application."""

from dj_rest_auth import views as djra_views
from django.urls import path

app_name = 'authentication'

urlpatterns = [
    path(r'login/', djra_views.LoginView.as_view(), name='login'),
    path(r'logout/', djra_views.LogoutView.as_view(), name='logout'),
]
