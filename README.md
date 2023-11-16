# CRC Self Service Portal

[![](https://app.codacy.com/project/badge/Grade/9ee06ecdddef4f75a8deeb42fa4a9651)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)


## Settings

| Setting                          | Default Value                                                         | Description                                                                                      |
|----------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| `DEBUG`                          | `0`                                                                   | Enables or disables debugging mode.                                                              |
| `SECRET_KEY`                     | Randomly generated                                                    | A secret key for cryptographic signing.                                                          |
| `ALLOWED_HOSTS`                  | `localhost 127.0.0.1`                                                 | A list of valid host/domain names for the site.                                                  |
| `SECURE_SSL_REDIRECT`            | `True` if not in debug mode                                           | Redirects all HTTP traffic to HTTPS.                                                             |
| `SESSION_COOKIE_SECURE`          | `True` if not in debug mode                                           | Whether to use a secure cookie for the session.                                                  |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` if not in debug mode                                           | Whether to include subdomains in HSTS header.                                                    |
| `SECURE_HSTS_PRELOAD`            | `True` if not in debug mode                                           | Whether to enable HSTS preload functionality.                                                    |
| `CSRF_COOKIE_SECURE`             | `True` if not in debug mode                                           | Whether to use a secure cookie for CSRF.                                                         |
| `SECURE_HSTS_SECONDS`            | `0` if in debug mode, `10` otherwise                                  | The duration, in seconds, to cache HSTS settings.                                                |
| `AUTH_LDAP_MIRROR_GROUPS`        | `True`                                                                | Whether to mirror LDAP groups locally.                                                           |
| `AUTH_LDAP_ALWAYS_UPDATE_USER`   | `True`                                                                | Whether to update the user model on each login.                                                  |
| `AUTH_LDAP_START_TLS`            | `True` if not explicitly set to `'0'`                                 | Whether to use TLS when connecting to the LDAP server.                                           |
| `AUTH_LDAP_SERVER_URI`           | `""`                                                                  | The URI of the LDAP server.                                                                      |
| `AUTH_LDAP_BIND_DN`              | `""`                                                                  | The DN to use when binding to the LDAP server.                                                   |
| `AUTH_LDAP_BIND_PASSWORD`        | `""`                                                                  | The password to use when binding to the LDAP server.                                             |
| `AUTH_LDAP_USER_SEARCH`          | `LDAPSearch("", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")`                | The search query for finding a user in the LDAP server.                                          |
| `ROOT_URLCONF`                   | `'main.urls'`                                                         | The Python import path to the root URLconf.                                                      |
| `LOGIN_REDIRECT_URL`             | `'/'`                                                                 | The URL where users will be redirected after login.                                              |
| `SITE_ID`                        | `1`                                                                   | The ID of the current site in the Django Sites framework.                                        |
| `INSTALLED_APPS`                 | List of installed apps                                                | The list of installed Django applications.                                                       |
| `MIDDLEWARE`                     | List of middleware                                                    | The list of middleware classes to use.                                                           |
| `TEMPLATES`                      | List of template settings                                             | Configures how Django templates are rendered.                                                    |
| `JAZZMIN_SETTINGS`               | Dictionary with Jazzmin settings                                      | Settings for the Jazzmin Django admin interface.                                                 |
| `REST_FRAMEWORK`                 | Dictionary with REST framework settings                               | Configures settings for the Django REST framework.                                               |
| `CELERY_BROKER_URL`              | `'redis://127.0.0.1:6379/0'`                                          | URL for the Celery message broker.                                                               |
| `CELERY_RESULT_BACKEND`          | `'redis://127.0.0.1:6379/0'`                                          | URL for the Celery result backend.                                                               |
| `CELERY_CACHE_BACKEND`           | `'django-cache'`                                                      | Cache backend for Celery.                                                                        |
| `EMAIL_BACKEND`                  | `'django.core.mail.backends.filebased.EmailBackend'` if in debug mode | The email backend for sending emails.                                                            |
| `EMAIL_FILE_PATH`                | `'BASE_DIR / 'email''` if in debug mode                               | The directory where email files are stored.                                                      |
| `DEFAULT_AUTO_FIELD`             | `'django.db.models.BigAutoField'`                                     | The default auto field to use for models.                                                        |
| `DATABASES`                      | Dictionary with database settings                                     | Configures the default database connection.                                                      |
| `AUTHENTICATION_BACKENDS`        | List of authentication backends                                       | The list of authentication backends to use.                                                      |
| `AUTH_PASSWORD_VALIDATORS`       | List of password validators                                           | Validators used to check the strength of user passwords.                                         |
| `STATIC_URL`                     | `'static/'`                                                           | URL to use when referring to static files.                                                       |
| `STATIC_ROOT`                    | `'BASE_DIR / 'static_root''`                                          | The absolute path to the directory where collectstatic will collect static files for deployment. |
| `STATICFILES_DIRS`               | `['BASE_DIR / 'static'']`                                             | Additional locations of static files.                                                            |

