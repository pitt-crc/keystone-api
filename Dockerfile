FROM python:3.11.4-slim

EXPOSE 8000

# Disable Python byte code caching and output buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    # Required for LDAP
    build-essential \
    libsasl2-dev \
    libldap2-dev \
    # Required for Celery
    redis \
    # Required for Docker health checks
    curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Create an unprivliged user for running background services
RUN groupadd --gid 900 keystone && useradd -m -u 900 -g keystone keystone

# Install the application
WORKDIR /app
COPY . src
RUN pip install ./src && rm -rf src

# Setup and launch the application
ENTRYPOINT ["keystone-api"]
HEALTHCHECK CMD curl --fail --location localhost:8000/health/ || exit 1
CMD ["quickstart", "--all"]
