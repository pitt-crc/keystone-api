FROM python:3.11.4-slim

EXPOSE 8000

# Disable Python byte code caching and output buffering
ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    # Required for LDAP
    build-essential \
    libsasl2-dev \
    libldap2-dev \
    # Required for celery
    redis \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy application build files
WORKDIR /app
COPY keystone_api keystone_api
COPY pyproject.toml pyproject.toml
COPY README.md README.md

# Install the application
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install -e . && pip cache purge

# Add and unprivliged user for running services
RUN groupadd --gid 900 keystone && \
    useradd -m -u 999 -g keystone keystone && \
    chown keystone:keystone /app

# Setup and launch the application
ENTRYPOINT ["keystone-api"]
CMD ["quickstart", "--migrate", "--static", "--celery", "--gunicorn", "--no-input"]
