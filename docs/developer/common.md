# Common Tasks

The following section details useful information for application developers and contributors.

## Debug Mode

The Django framework provides a debug mode which enables detailed error traceback directly in the browser.
It also enables static file hosting (incluing page styling) and loosens various security restrictions.
To enable debug mode, specify the `DEBUG=true` setting.

!!! danger

    The `DEBUG` option is inherently insecure and should **never** be enabled in production settings.

## Admin Utilities

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

Specific subsets of tests are run by specifying an app label.
For example, tests for the `users` application are executed as:

```bash
keystone-api test apps.users
```

The default django system checks can also be executed as standard:

```bash
keystone-api check                   # Check for system configuration errors
keystone-api makemigrations --check  # Check for missing database migrations
keystone-api health_check            # Check the status of running backend services
```

## API Schema Generation

The `spectacular` command will dynamically generate a complete OpenAPI schema.
Rendering the specification into a human friendly format is left to the user and the documentation tool of their choice.  

```bash
keystone-api spectacular >> api.yml
```
