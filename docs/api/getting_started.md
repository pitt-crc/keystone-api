# Getting Started

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
    
    auth_request = requests.post(
        url="https://keystone.domain.com/authentication/new/",
        json=credentials,
        headers=headers)
    
    jwt = auth_request.json()
    access_token = jwt["access"]
    refresh_token = jwt["refresh"]
    ```

=== "bash"

    ```bash
    credentials='{"username": "admin", "password": "adminpassword"}'
    headers='Content-Type: application/json'
    
    response=$(curl -s -X POST \
      -H "$headers" \
      -d "$credentials" \
      https://keystone.domain.com/authentication/new/)
    
    access_token=$(echo "$response" | jq -r '.access')
    refresh_token=$(echo "$response" | jq -r '.refresh')
    ```

Future requests to API endpoints are authenticated by including the JWT access token in the request header. 
See the [OpenAPI specification](api.md) for documentation on available endpoints.

=== "python"

    ```python
    data_request = requests.get(
        url="https://keystone.domain.com/allocations/allocations/",
        headers={"Authorization": f"Bearer {access_token}"})

    print(data_request.json())
    ```

=== "bash"

    ```bash
    data_request=$(curl -s -X GET \
      -H "Authorization: Bearer $access_token" \
      "https://keystone.domain.com/allocations/allocations/")

    echo "$data_request"
    ```

The access token will expire after a short period.
To generate a new access token, use the refresh token with the `authentication/refresh/` endpoint. 

!!! note

    See the `SECURE_ACCESS_TOKEN_LIFETIME` and `SECURE_REFRESH_TOKEN_LIFETIME` values in the [application settings](install/settings.md)
    for more information on token expiration.

=== "python"

    ```python
    refresh_request = requests.post(
        url="https://keystone.domain.com/authentication/refresh/",
        json={"refresh": refresh_token})

    access_token = refresh_request["access"]
    ```

=== "bash"

    ```bash
    refresh_request=$(curl -s -X POST \
      -H "Content-Type: application/json" \
      -d '{"refresh": "'"$refresh_token"'"}' \
      "https://keystone.domain.com/authentication/refresh/")
    
    access_token=$(echo "$refresh_request" | jq -r '.access')
    ```

After a long enough period of time, the refresh token will also expire.
Users can invalidate their credentials early using the `authentication/blacklist/` endpoint.

=== "python"

    ```python
    blacklist_request = requests.post(
        url="https://keystone.domain.com/authentication/blacklist/",
        json={"refresh": refresh_token})
    ```

=== "bash"

    ```bash
    blacklist_request=$(curl -s -X POST \
      -H "Content-Type: application/json" \
      -d '{"refresh": "'"$refresh_token"'"}' \
      "https://keystone.domain.com/authentication/blacklist/")
    ```

## Query Expressions

When querying data from an API endpoint, the returned records can be filtered using URL parameters.
In the following example, returned records are limited to those where the `example` field equals `100`:

```
my.domain.com/endpoint?example=100
```

More advanced filtering is achieved by adding query filters.
Query filters are specified using a double underscre (`__`) followed by filter expression.
For example, the following API call will return records when the `example` field is greater than `50` but less than `150`:

```
my.domain.com/endpoint?example__gt=50&example_lt=150
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
