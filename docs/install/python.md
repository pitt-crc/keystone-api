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

### LDAP (Optional)

An LDAP server is only required if users are expected to authenticate with LDAP credentials.
Setting up LDAP for use with Keystone-API doesn't require any special configuration.
However, Keystone's API settings must be properly configured to ensure correct mapping between LDAP fields and Keystone user account attributes.
See the [Settings](settings.md) page for more details.

### Redis

Most Redis server instances will work out of the box so long as the connection and authentication values are set correctly in the Keystone-API settings.

### PostgreSQL

Using PostgreSQL for the application database is strongly recommended.
After deploying a PostgreSQL server, you will need to create a dedicated database and user account. 
Start by launching a new SQL session with admin permissions: 

```bash
sudo -u postgres psql
```

Next, create the database and a Keystone service account.
Making sure to replace the passwrd value below with a secure password.

```postgresql
create database keystone;
create user keystone_sa with encrypted password '[PASSWORD]';
grant all privileges on database keystone to keystone_sa;
```

### Celery

Celery and Celery Beat are both included when pip installing the `keystne_api` package.
Both applications should be launched using the settings below.

```bash
celery -A keystone_api.apps.scheduler worker
celery -A keystone_api.apps.scheduler beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

If running on a Linux machine, users may appreciate the convenience of managing Celery via the systemd service manager. 
The following unit files are provided as a starting point for system administrators.

### Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 keystone_api.main.wsgi:application
```
