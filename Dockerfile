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
    # Required for celery
    redis \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Create an unprivliged user for running services
RUN groupadd --gid 900 keystone && useradd -m -u 999 -g keystone keystone \
    && mkdir /app && chown keystone /app

USER keystone
WORKDIR /app
ENV PATH="${PATH}:/home/keystone/.local/bin"

COPY --chown=keystone . src
RUN pip install ./src && rm -rf src

# Setup and launch the application
ENTRYPOINT ["keystone-api"]
CMD ["quickstart", "--migrate", "--static", "--celery", "--gunicorn", "--no-input"]
