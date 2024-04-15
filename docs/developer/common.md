# Common Developer Tasks

The following sections outline common tasks for application developers and contributors.

## Python Environment Setup

Start by cloning the project repository from GitHub.

```bash
git clone https://github.com/pitt-crc/keystone-api
```

Keystone-API uses [Poetry](https://python-poetry.org/docs/) to manage application dependencies.
Certain dependencies, such as those required for building documentation, are optional.
To install the project dependencies, execute the following from the root of the cloned repository:

```bash
poetry install --with docs #(1)!
```

1. The `--with` option is used to specify optional dependency groups.

If the installation was successful, the packaged CLI tool will be available in your working environment.
Use the `enable_autocomplete` command to enable autocomplete for the Bash shell.

```bash
keystone-api enable_autocomplete
```

## Running In Debug Mode

The Django framework provides a debug mode which enables detailed error tracebacks directly in the browser.
It also enables static file hosting (including page styling) and loosens various security restrictions.
To enable debug mode, specify the `DEBUG=true` setting.

!!! danger

    The `DEBUG` option is inherently insecure and should **never** be enabled in production settings.

```bash
DEBUG=True keystone-api runserver
```

## Admin CLI Utilities

The `keystone-api` utility includes a series of custom admin utilities for automating various development tasks.
A brief summary is provided below.
Use the `keystone-api <command> --help` option for specific usage information.

| Command                   | Description                                                                              |
|---------------------------|------------------------------------------------------------------------------------------|
| `clean`                   | Clean up files generated when launching a new application instance.                      |
| `quickstart`              | A helper utility for quickly migrating/deploying an application instance.                |

## Tests and System Checks

Application tests are run using the `test` command:

```bash
keystone-api test
```

Specific subsets of tests are run by specifying an application module.
For example, tests for the `users` module are executed as:

```bash
keystone-api test apps.users
```

The default Django system checks can also be executed as standard:

```bash
keystone-api check #(1)! 
keystone-api makemigrations --check #(2)! 
keystone-api health_check #(3)! 
```

1. Check for system configuration errors
2. Check for missing database migrations
3. Check the status of backend services

## Previewing Documentation

Project documentation is written using [MkDocs](https://www.mkdocs.org/).
The `serve` command will automatically compile the documentation into HTML launch a preview using local webserver.

```bash
mkdocs serve
```

To compile the HTML documentation without launching a webserver, use the `build` command.

```bash
mkdocs build
```

## OpenAPI Generation

The `spectacular` command will dynamically generate a complete OpenAPI schema.
Rendering the specification into a human friendly format is left to the user and the documentation tool of their choice.  

```bash
keystone-api spectacular --file api.yml
```
