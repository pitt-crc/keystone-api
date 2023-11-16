# CRC Self Service Portal

[![](https://app.codacy.com/project/badge/Grade/9ee06ecdddef4f75a8deeb42fa4a9651)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)


## Settings

| Setting                          | Default Value              | Description                                                                                      |
|----------------------------------|----------------------------|--------------------------------------------------------------------------------------------------|
| `DEBUG`                          | `False`                    | Enables or disables debug mode.                                                                  |
| `SECRET_KEY`                     | Randomly generated         | A secret key for cryptographic signing.                                                          |
| `ALLOWED_HOSTS`                  | `localhost 127.0.0.1`      | A list of valid host/domain names for the site.                                                  |
| `SECURE_SSL_REDIRECT`            | `True`                     | Redirects all HTTP traffic to HTTPS.                                                             |
| `SESSION_COOKIE_SECURE`          | `True`                     | Whether to use a secure cookie for the session.                                                  |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True`                     | Whether to include subdomains in HSTS header.                                                    |
| `SECURE_HSTS_PRELOAD`            | `True`                     | Whether to enable HSTS preload functionality.                                                    |
| `SECURE_HSTS_SECONDS`            | `10`                       | The duration, in seconds, to cache HSTS settings.                                                |
| `CSRF_COOKIE_SECURE`             | `True`                     | Whether to use a secure cookie for CSRF.                                                         |
| `AUTH_LDAP_START_TLS`            | `True`                     | Whether to use TLS when connecting to the LDAP server.                                           |
| `AUTH_LDAP_SERVER_URI`           |                            | The URI of the LDAP server.                                                                      |
| `AUTH_LDAP_BIND_DN`              |                            | The DN to use when binding to the LDAP server.                                                   |
| `AUTH_LDAP_BIND_PASSWORD`        |                            | The password to use when binding to the LDAP server.                                             |
| `AUTH_LDAP_USER_SEARCH`          | `(uid=%(user)s)`           | The search query for finding a user in the LDAP server.                                          |
| `OPT_X_TLS_REQUIRE_CERT`         | `True`                     |                                                                                                  |
| `CELERY_BROKER_URL`              | `redis://127.0.0.1:6379/0` | URL for the Celery message broker.                                                               |
| `CELERY_RESULT_BACKEND`          | `redis://127.0.0.1:6379/0` | URL for the Celery result backend.                                                               |
| `EMAIL_FILE_PATH`                | `<BASE_DIR> / email`       | The directory where email files are stored.                                                      |
| `DB_DRIVER`                      | `sqlite3`                  |                                                                                                  |
| `DB_NAME`                        | `crc_service`              |                                                                                                  |
| `DB_USER`                        |                            |                                                                                                  |
| `DB_PASSWORD`                    |                            |                                                                                                  |
| `DB_HOST`                        | 'localhost`                |                                                                                                  |
| `DB_PORT`                        | '5432`                     |                                                                                                  |
| `STATIC_URL`                     | `static/`                  | URL to use when referring to static files.                                                       |
| `STATIC_ROOT`                    | `<BASE_DIR> / static_root` | The absolute path to the directory where collectstatic will collect static files for deployment. |
