# Deploying with Docker

Deploying Keystone API using container images is strongly recommended.
For situations where containers are not an option, see the documentation on [deploying with Python](python).

## Using Docker Standalone

The application image can be pulled and launched from the GitHub container registry:

```bash
docker pull ghcr.io/pitt-crc/keystone-api
docker run -p 8000:8000 ghcr.io/pitt-crc/keystone-api
```

The container will automatically deploy a fully functioning API server, including all supporting services.
Once the container is ready, you will need to manually create the first user account.
Execute the following command with the appropriate container name and follow the onscreen prompts.

```bash
docker exec -it [CONTAINER NAME] keystone-api createsuperuser
```

The REST API is now ready to us on port `8000`.

!!! important

    The default container instance is **not** suitable for production out of the box.
    Supporting services (PostgreSQL, Redis, etc.) will not persist data between container restarts and should be deployed separately to ensure proper data persistence. 
    See the [Settings](../../settings/settings) section for a complete overview of configurable options and recommended settings.

## Using Docker Compose

Deploying with Docker Compose provides several benefits over a single container deployment.
Most importantly, database services are configured to persist data on the host machine, preventing data loss between container restarts.
The configuration file is also easily customizable to fit individual use cases and is scalable to meet production loads.

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

    ```bash
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

    ```bash
    # Credential values must match api.env
    POSTGRES_DB="keystone"
    POSTGRES_USER="db_user"
    POSTGRES_PASSWORD="foobar123"
    ```
