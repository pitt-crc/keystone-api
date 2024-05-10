# Using the API

This page provides a general guide for getting the most out of the Keystone REST API.
See the [OpenAPI specification](api.md) for the full API schema.

## Authentication

Keystone uses JSON Web Tokens (JWT) to manage user authentication and permissions.
New JWT tokens are generate using the `authentication/new/` endpoint.

=== "python"

    ```python
    import requests

    credentials = {"username": "admin", "password": "adminpassword"}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(
        "https://keystone.domain.com/authentication/new/", 
        json=credentials, headers=headers)
    
    jwt = response.json()
    access_token = jwt["access"]
    refresh_token = jwt["refresh"]
    ```

=== "bash"

    ```bash
    jwt=$(curl \
      -X POST \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "adminpassword"}' \
      https://keystone.domain.com/authentication/new/)
    ```

To access API endpoints, specify the JWT access token in the request header. 
See the [OpenAPI specification](api.md) for documentation on available endpoints.

=== "python"

    ```python
    response = requests.get(
        "https://keystone.domain.com/endpoint'", 
        headers={"Authorization": f"Bearer {jwt['access']}"})
    ```

=== "bash"

    ```bash
    curl \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU" \
      https://keystone.domain.com/endpoint
    ```

The access token will expire after a short period (see the `SECURE_ACCESS_TOKEN_LIFETIME` value in the [application settings](install/settings.md)).
To generate a new access token, use the refresh token with the `authentication/refresh/` endpoint. 

=== "python"

    ```python
    foobar
    ```

=== "bash"

    ```bash
    curl \
      -X POST \
      -H "Content-Type: application/json" \
      -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"}' \
      http://localhost:8000/authentication/refresh/
    ```

After a long enough period of time, the refresh token will also expire (see the `SECURE_REFRESH_TOKEN_LIFETIME` value in the [application settings](install/settings.md)).
However, users may wish to manually invalidate their credentials.
The `authentication/blacklist/` endpoint will add any posted credentials to a blacklist and invalidate the corresponding user credentials.

=== "python"

    ```python
    foobar
    ```

=== "bash"

    ```bash
    foobar
    ```

## Query Expressions

When querying data from an API endpoint, the returned records can be filtered using URL parameters.
In the following example, returned records are limited to those where the `count` field equals `100`:

```
my.domain.com/endpoint?count=100
```

More advanced filtering is achieved by adding query filters.
Query filters are specified using a double underscre (`__`) followed by filter expression.
For example, the following API call will return records when the `count` field is greatr than `50` but less than `150`:

```
my.domain.com/endpoint?count__gt=50&count_lt=150
```

Available query filters are summarized in the tables below.

### General Filters

The following filters are available for all data types.

| Query Expression | Description                                              | Example              |
|------------------|----------------------------------------------------------|----------------------|
| `in`             | Whether the value is in a comma-separated list of values | `field__in=1,2,3`    |
| `isnull`         | Whether the value is none                                | `field__isnull=true` |

### Numeric Filters

The following filters are available for numerical data such as floats and integers.

| Query Expression | Description                                                 | Example          |
|------------------|-------------------------------------------------------------|------------------|
| `lt`             | Whether the value is less than another value                | `field__lt=100`  |
| `lte`            | Whether the value is less than or equal to another value    | `field__lte=100` |
| `gt`             | Whether the value is greater than another value             | `field__gt=100`  |
| `gte`            | Whether the value is greater than or equal to another value | `field__gte=100` |

### String Filters

The following filters are available for text and character values.

| Query Expression | Description                                  | Example                     |
|------------------|----------------------------------------------|-----------------------------|
| `contains`       | Whether the value contains subtext           | `field__contains=subtext`   |
| `startswith`     | Whether the value starts with the given text | `field__startswith=subtext` |
| `endswith`       | Whether the value ends with the given text   | `field__endswith=subtext`   |

### Date Filters

The following filters are available for date and datetime values in ISO-8601 format.

| Query Expression | Description                                                 | Example                 |
|------------------|-------------------------------------------------------------|-------------------------|
| `year`           | Whether the date value matches a given year                 | `field__year=2022`      |
| `month`          | Whether the date value matches a given month                | `field__month=12`       |
| `day`            | Whether the date value matches a given day                  | `field__day=25`         |
| `week`           | Whether the date value falls on a given week of the month   | `field__week=52`        |
| `week_day`       | Whether the date value falls a given day of the week        | `field__week_day=1`     |
| `lt`             | Whether the value is less than another value                | `field__lt=2020-01-22`  |
| `lte`            | Whether the value is less than or equal to another value    | `field__lte=2020-01-22` |
| `gt`             | Whether the value is greater than another value             | `field__gt=2020-01-22`  |
| `gte`            | Whether the value is greater than or equal to another value | `field__gte=2020-01-22` |

### Time Filters

The following filters are available for time and datetime values in ISO-8601 format.

| Query Expression | Description                                                 | Example               |
|------------------|-------------------------------------------------------------|-----------------------|
| `hour`           | Whether the time value matches a given hour                 | `field__hour=8`       |
| `minute`         | Whether the time value matches a given minute               | `field__minute=30`    |
| `second`         | Whether the time value matches a given second               | `field__second=45`    | 
| `lt`             | Whether the value is less than another value                | `field__lt=19:20:15`  |
| `lte`            | Whether the value is less than or equal to another value    | `field__lte=19:20:15` |
| `gt`             | Whether the value is greater than another value             | `field__gt=19:20:15`  |
| `gte`            | Whether the value is greater than or equal to another value | `field__gte=19:20:15` |
