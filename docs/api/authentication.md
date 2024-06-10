# Authentication

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

    See the `SECURE_ACCESS_TOKEN_LIFETIME` and `SECURE_REFRESH_TOKEN_LIFETIME` values in the [application settings](../install/settings.md)
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
