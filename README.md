# CRC Self Service Portal

[![](https://app.codacy.com/project/badge/Grade/9ee06ecdddef4f75a8deeb42fa4a9651)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

## Settings

### Security and Networking

Improperly configuring these settings can introduce dangerous vulnerabilities and may damage your production deployment.
Most default values are chosen to be sufficient out of the box (except `ALLOWED_HOSTS` and `ALLOWED_HOSTS`, which must
be chosen manually).
User's looking to customize their deployment should adhere to the following general guidelines:

- Ensure your deployment is isolated being a web proxy with proper HTTPS handling
- Allways define the `ALLOWED_HOSTS` list using a restrictive collection of domain patterns
- Avoid issuing session/CSRF tokens over unsecured connections by enabling `SESSION_TOKENS_ONLY`
- HTTP Strict Transport Security (HSTS) should be used to enforce the use of HTTPS

| Setting Name                     | Default Value         | Description                                               |
|----------------------------------|-----------------------|-----------------------------------------------------------|
| `SECRET_KEY`                     | Randomly generated    | Secret key used to enforce cryptographic signing.         |
| `ALLOWED_HOSTS`                  | `localhost,127.0.0.1` | Comma seperated list of accepted host/domain names.       |
| `SECURE_SSL_REDIRECT`            | `False`               | Automatically redirect all HTTP traffic to HTTPS.         |
| `SESSION_TOKENS_ONLY`            | `False`               | Only issue session/CSRF tokens over secure connections.   |
| `SECURE_HSTS_SECONDS`            | `0` (Disabled)        | The duration, in seconds, to cache HSTS settings.         |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `False`               | Include HSTS headers for subdomains.                      |
| `SECURE_HSTS_PRELOAD`            | `False`               | Whether to enable HSTS preload functionality.             |

### LDAP Authenticating

LDAP authentication support is optional and disabled by default.
To enable LDAP, set the `AUTH_LDAP_SERVER_URI` value to the desired LDAP endpoint.

| Setting Name                     | Default Value         | Description                                               |
|----------------------------------|-----------------------|-----------------------------------------------------------|
| `AUTH_LDAP_START_TLS`            | `True`                | Whether to use TLS when connecting to the LDAP server.    |
| `AUTH_LDAP_SERVER_URI`           |                       | The URI of the LDAP server.                               |
| `AUTH_LDAP_BIND_DN`              |                       | Optionally bind LDAP queries to the given DN.             |
| `AUTH_LDAP_BIND_PASSWORD`        |                       | The password to use when binding to the LDAP server.      |
| `AUTH_LDAP_USER_SEARCH`          | `(uid=%(user)s)`      | The search query for finding a user in the LDAP server.   |
| `OPT_X_TLS_REQUIRE_CERT`         | `True`                | Require TLS when connecting to LDAP.                      |

### Database Connection

Official support is included for both SQLite and PostgresSQL database backends.
However, the former is intended for development and demonstrative use-cases only.
The `postgresql` backend should always be used in production settings.

| Setting Name   | Default Value                         | Description                                                     |
|----------------|---------------------------------------|-----------------------------------------------------------------|
| `DATABASE_URL` | `sqlite:///<INSTALL_DIR>/keystone.db` | The database url `protocol:///username:password@host:port/name` |

### Celery Workers

Connection settings for Celery backend utilities.

| Setting Name                     | Default Value              | Description                                          |
|----------------------------------|----------------------------|------------------------------------------------------|
| `CELERY_BROKER_URL`              | `redis://127.0.0.1:6379/0` | URL for the Celery message broker.                   |
| `CELERY_RESULT_BACKEND`          | `redis://127.0.0.1:6379/0` | URL for the Celery result backend.                   |

### Static File Hosting

The application is capable of hosting its own static file content.
However, user's may optionally configure settings to use a dedicated CDN.

| Setting Name   | Default Value               | Description                                                           |
|----------------|-----------------------------|-----------------------------------------------------------------------|
| `STATIC_URL`   | `static/`                   | URL to use when referring to static files.                            |
| `STATIC_ROOT`  | `<INSTALL_DIR>/static_root` | The absolute path where static files are collected for deployment.    |

### Developer Settings

The following settings are intended exclusively for use in development settings.
The `DEBUG` option is inherently insecure and should **never** be enabled in production settings.

| Setting Name      | Default Value          | Description                                                                    |
|-------------------|------------------------|--------------------------------------------------------------------------------|
| `DEBUG`           | `False`                | Enable or disable debug mode.                                                  |
| `EMAIL_FILE_PATH` | `<INSTALL_DIR>/email/` | In debug mode, emails are written to disk instead of being issued to a server. |
