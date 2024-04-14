# Deploying with Python

The Keystone REST API can be installed as a standard Python package using the pip package manager.
Deploying a production instance via pip is only recommended as a fallback for situations where Docker is not available.
Direct package installations typically require extra configuration and a working familiarity with system administration.

## Installing the API

The `keystone_api` package and it's dependencies are pip installable.
In keeping with best practice, it is recommended to install the package into a dedicated (virtual) environment.

```bash
pip install keystone-api
```

If the installation was successful, the packaged CLI tool will be available in your working environment.
Use the `--help` option to view the available commands.

```bash
keystone-api --help
```

The `keystone-api` utility does not support tab autocompletion by default.
To enable autocomplete for the Bash shell, use the `enable_autocomplete` command.

```bash
keystone-api enable_autocomplete
```

You can test the installed package by deploying a development instance of the application.
The following example creates a SQLite database, generates an admin user account, and launches the API server in debug mode.

!!! danger

    Debug mode is inherently insecure and should **never** be enabled in production.
    It's use is reserved for development and demonstrative purposes only.

!!! important

    The webserver launched by the `runserver` command is not suitable for production.
    A production quality WSGI/ASGI web server should be used instead.

```bash
keystone-api migrate
keystone-api createsuperuser
DEBUG=true keystone-api runserver
```

## Deploying the Application

Keystone requires several backend services to support operation in a production environment.
Specific instructions are provided below on configuring each dependency to work with the Keystone API.

### LDAP

### Redis

### PostgreSQL


```bash
sudo -u postgres psql
```

```postgresql
create database keystone;
create user keystone_sa with encrypted password '[PASSWORD]';
grant all privileges on database keystone to keystone_sa;
```

### Celery

```bash
celery -A keystone_api.apps.scheduler worker
celery -A keystone_api.apps.scheduler beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Gunicorn

```bash
keystone-api migrate --no-input
keystone-api collectstatic --no-input
gunicorn --bind 0.0.0.0:8000 keystone_api.main.wsgi:application
```
