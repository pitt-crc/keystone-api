# Deploying with Python

The Keystone REST API can be installed as a standard Python package using the pip package manager.
Deploying a production instance via pip is only recommended as a fallback for situations where Docker is not available. 
Direct package installations typically require extra configuration and a working familiarity with system administration.

## System Requirements

The following dependencies are required:

- A Redis database

The additional dependencies listed below are optional, but required to support various application functionality: 

- A PostgreSQL database (if using PostgreSQL instead of SQLite)
- LDAP development binaries (if using LDAP authentication)

!!! note

    Support for SQLite is intended primarily for use in development and demonstrations.
    Enabling PostgreSQL is **strongly** recommended when operating in a production environment.

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

A development instance of the application 
The following example will set up the project database, create an admin user account, and launch the
API server in debug mode. As a general rule, debug mode should **never** be enabled in production.

```bash
keystone-api migrate
keystone-api createsuperuser
DEBUG=true keystone-api runserver
```

The default container instance is *not* suitable for full production out of the box.
See the [Settings](#settings) section for a complete overview of configurable options and recommended settings.


### Enabling Autocomplete

The `keystone-api` utility does not support tab autocompletion by default.
To enable autocomplete for the Bash shell, use the `enable_autocomplete` command.

```bash
keystone-api enable_autocomplete
```

## Deploying the Application
