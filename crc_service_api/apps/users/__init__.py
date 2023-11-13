"""
The `signup` application is responsible for the creation and verification
of new user accounts.

Application features include:

- Allows users to create new accounts using a unique username, email address, and password.
- An extended user database model with additional fields and functionality.
- User account management via customized administrative interfaces in the website admin portal.
- Account verification email confirmation requests.

## Installation

Add the application and it's required dependencies to the `installed_apps`
list in the package settings:

```python
INSTALLED_APPS = [
    'django.contrib.sites',
    'apps.signup',
]
```

Register application URLs in the package's primary URL configuration file:

```python
from django.urls import include, path

urlpatterns = [
    path('signup/', include('apps.signup.urls', namespace='signup')),
]
```

Using the same namespace value as chosen in the previous step, override the
default user model by adding the following definition to the package settings file:

```python
AUTH_USER_MODEL = 'signup.AuthUser'
"""
