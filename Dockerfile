FROM python:3.11.4-slim

EXPOSE 8000

# Disable Python byte code caching and output buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Required for LDAP
    build-essential \
    libsasl2-dev \
    libldap2-dev \
    # Required for celery
    redis

# Copy only the files needed to build the application
WORKDIR /app
COPY keystone_api keystone_api
COPY pyproject.toml pyproject.toml
COPY README.md README.md

# Install the application
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install -e .

# Setup and launch the application
ENTRYPOINT ["keystone-api"]
CMD ["quickstart", "--static", "--migrate", "--celery", "--gunicorn", "--no-input"]
