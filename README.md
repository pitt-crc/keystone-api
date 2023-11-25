# Keystone API

[![](https://app.codacy.com/project/badge/Grade/9ee06ecdddef4f75a8deeb42fa4a9651)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

The backend REST API for the Keystone allocation management dashboard.

## Installation

To install the Keystone API, choose from one of the following options.

### Using Docker

Using Docker is the recommended method for building and deploying application instances.
The most recent image can be pulled from the GitHub container registry:

```bash
docker pull ghcr.io/pitt-crc/keystone-api
docker run -p 8000:8000 ghcr.io/pitt-crc/keystone-api
```

Alternatively, the latest development version can be built directly from source:

```bash
git clone https://github.com/pitt-crc/keystone-api
docker build -t keystone-api:develop keystone-api
docker run -p 8000:8000 keystone-api:develop
```

The container will automatically launch a fully functioning application served via the Gunicorn web server.
The application is *not* suitable for full production out of the box.
See the [Settings](#settings) section for a complete overview of availible settings.

### Installing from source

Installing from source is only recommended for project development or as a fallback for situations where Docker is not available.
Before proceeding with installation, the following system dependencies must be met:
- A running Celery instance
- A running Redis database
- A running PostgreSQL database (if not using SQLite)
- LDAP development binaries (if using LDAP authentication)

In keeping with best practice, it is recommended to install packages in a dedicated virtual environment:

```bash
conda create -n keystone-api python=3.11
conda activate keystone-api
```

The package and its dependencies are pip installable.
Note the recommended use of editable mode (`-e`) to simplify development.

```bash
pip install -e keystone-api
```

If the installation was successful, the packaged CLI tool will be available in your working environment.
Use the `--help` option to view the available commands.

```bash
kystone-api --help
```

## Settings

Application settings are configurable as environmental variables.
Available settings are listed below by category and use case.

### Security and Networking

Improperly configuring these settings can introduce dangerous vulnerabilities and may damage your production deployment. Administrators should adhere to the following general guidelines:

- Ensure your deployment is isolated behind a web proxy with proper HTTPS handling
- Always define the `ALLOWED_HOSTS` list using a restrictive collection of domain patterns
- Avoid issuing session/CSRF tokens over unsecured connections by enabling `SESSION_TOKENS_ONLY`
- HTTP Strict Transport Security (HSTS) should be used to enforce the use of HTTPS
- Use a fixed `SECRET_KEY` value to ensure consistent request signing across application instances/restarts

| Setting Name                     | Default Value         | Description                                               |
|----------------------------------|-----------------------|-----------------------------------------------------------|
| `SECRET_KEY`                     | Randomly generated    | Secret key used to enforce cryptographic signing.         |
| `ALLOWED_HOSTS`                  | `localhost,127.0.0.1` | Comma-separated list of accepted host/domain names.       |
| `SECURE_SSL_REDIRECT`            | `False`               | Automatically redirect all HTTP traffic to HTTPS.         |
| `SESSION_TOKENS_ONLY`            | `False`               | Only issue session/CSRF tokens over secure connections.   |
| `SECURE_HSTS_SECONDS`            | `0` (Disabled)        | The duration, in seconds, to cache HSTS settings.         |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `False`               | Include HSTS headers for subdomains.                      |
| `SECURE_HSTS_PRELOAD`            | `False`               | Whether to enable HSTS preload functionality.             |

### LDAP Authentication

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

Official support is included for both SQLite (`sqlite`) and PostgreSQL (`postgresql`) database protocols.
However, the former is intended for development and demonstrative use-cases only.
The PostgreSQL backend should always be used in production settings.

| Setting Name   | Default Value                         | Description                                                     |
|----------------|---------------------------------------|-----------------------------------------------------------------|
| `DATABASE_URL` | `sqlite:///<INSTALL_DIR>/keystone.db` | The database URL `protocol:///username:password@host:port/name` |

### Celery Workers

Connection settings for Celery backend utilities.

| Setting Name                     | Default Value              | Description                                          |
|----------------------------------|----------------------------|------------------------------------------------------|
| `CELERY_BROKER_URL`              | `redis://127.0.0.1:6379/0` | URL for the Celery message broker.                   |
| `CELERY_RESULT_BACKEND`          | `redis://127.0.0.1:6379/0` | URL for the Celery result backend.                   |

### Static File Hosting

The application is capable of hosting its own static file content.
However, users may optionally configure their deployment to use a dedicated CDN.

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

## Developer Notes

The following section details useful information for application contributors.

### Debug Mode

Running the application in debug mode enables/disables various features to aid in the development process.
In addition to enabling the standard debugging behavior provided by Django:
- A `/docs` page is enabled with full API documentation for the parent application
- User permissions are disabled for all API endpoints
- A web GUI is enabled for easier interaction with API endpoints
- Tracebacks are provided in the browser when an exception occurs (a Django standard)

### Tests and System Checks

Application tests are run using the `test` command:

```bash
keystone-api test
```

Specific subsets of tests are run by specifying an app label.
For example, tests for the `admin_utils` application are executed as:

```bash
keystone-api test apps.admin_utils
```

The default django system checks can also be executed as standard:

```bash
keystone-api check                   # Check for system configuraion errors
keystone-api makemigrations --check  # Check for missing database migrations
keystone-api health_check            # Check the status of running backnd services
```
