# Deploying with Docker

The Keystone API can be deployed as a single container using Docker, or as several containers using Docker Compose.
Single container deployments are for those looking to test-drive Keystone's capabilities.
Deploying with Docker Compose is strongly recommended for HPC teams operating at scale.

## Using Docker Standalone

Start by pulling the latest `keystone-api` image from the GitHub container registry.

```bash
docker pull ghcr.io/pitt-crc/keystone-api
```

When launching a new container, make sure to expose the internal API from port `8000` to an external port of your choosing.
In the following example, the application is launched in a container named `keystone` with port `8000` mapped to port `80`.

```bash
docker run --detach --publish 8000:80 --name keystone ghcr.io/pitt-crc/keystone-api
```

Create an administrative account by executing the `createsuperuser` command from within the container and follow the onscreen prompts.

```bash
docker exec -it keystone keystone-api createsuperuser
```

You can test the new credentials by using them to generate a pair of JWT tokens.

```bash
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "[USERNAME]", "password": "[PASSWORD]"}' \
  http://localhost:80/api/token/
```

If successful, you will receive a response similar to the following:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"
}
```

!!! important

    The default container instance is **not** suitable for production out of the box.
    Supporting services will not save data between container restarts and should be deployed separately to ensure data persistence. 
    See the [Settings](../../settings/settings) page for a complete overview of configurable options and recommended settings.

## Using Docker Compose

The following compose recipe provides a general starting point for a production ready deployment.
Users are responsible for customizing the deployment to meet their specific needs.

```yaml
version: "3.7"

services:
  cache:
    image: redis
    container_name: keystone-cache
    command: redis-server
    restart: always
    volumes:
      - cache_data:/data

  db:
    image: postgres
    container_name: keystone-db
    restart: always
    env_file:
      - db.env
    volumes:
      - postgres_data:/var/lib/postgresql/data/

  api:
    image: ghcr.io/pitt-crc/keystone-api
    container_name: keystone-api
    entrypoint: sh
    command: |
      -c '
        keystone-api migrate --no-input
        keystone-api collectstatic --no-input
        gunicorn --bind 0.0.0.0:8000 keystone_api.main.wsgi:application'
    restart: always
    depends_on:
      - cache
      - db
    ports:
      - "8000:8000"
    env_file:
      - api.env
    volumes:
      - static_files:/app/static
      - uploaded_files:/app/upload_files

  celery-worker:
    image: ghcr.io/pitt-crc/keystone-api:${KEYSTONE_API_VERSION:-latest}
    container_name: keystone-celery-worker
    entrypoint: celery -A keystone_api.apps.scheduler worker --uid 900
    restart: always
    depends_on:
      - cache
      - db
      - api
    env_file:
      - api.env

  celery-beat:
    image: ghcr.io/pitt-crc/keystone-api:${KEYSTONE_API_VERSION:-latest}
    container_name: keystone-celery-beat
    entrypoint: celery -A keystone_api.apps.scheduler beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --uid 900
    restart: always
    depends_on:
      - cache
      - db
      - api
      - celery-worker
    env_file:
      - api.env

volumes:
  static_files:
  uploaded_files:
  postgres_data:
  cache_data:
```

Application settings are configured using environmental variables defined in various `.env` files.
The following example files provide preliminary settings for getting everything up and running.

!!! important

    The setting provided below are intended for demonstrative purposes only.
    These values should be customized to meet the needs at hand and credentials should be changed to secure values.

=== "api.env"

    ```
    # General Settings
    DJANGO_SETTINGS_MODULE="keystone_api.main.settings"
    STORAGE_STATIC_DIR="/app/static"
    STORAGE_UPLOAD_DIR="/app/upload_files"
    
    # Security Settings
    SECURE_ALLOWED_HOSTS="*"
    
    # Redis settings
    REDIS_HOST="cache"
    
    # Database settings
    DB_POSTGRES_ENABLE="true"
    DB_NAME="keystone"
    DB_USER="db_user"
    DB_PASSWORD="foobar123"
    DB_HOST="db"
    ```

=== "db.env"

    ```
    # Credential values must match api.env
    POSTGRES_DB="keystone"
    POSTGRES_USER="db_user"
    POSTGRES_PASSWORD="foobar123"
    ```
