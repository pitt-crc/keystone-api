"""Top level Django application settings."""

import importlib.metadata
import sys
from pathlib import Path

import environ
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

env = environ.Env()
DEBUG = env.bool('DEBUG', False)
VERSION = importlib.metadata.version('keystone-api')

# Core security settings

SECRET_KEY = env.str('SECURE_SECRET_KEY', get_random_secret_key())
ALLOWED_HOSTS = env.list("SECURE_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

_SECURE_SESSION_TOKENS = env.bool("SECURE_SESSION_TOKENS", default=False)
SESSION_COOKIE_SECURE = _SECURE_SESSION_TOKENS
CSRF_COOKIE_SECURE = _SECURE_SESSION_TOKENS

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_SUBDOMAINS", default=False)

# App Configuration

ROOT_URLCONF = 'main.urls'
LOGIN_REDIRECT_URL = '/'
SITE_ID = 1

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'health_check',
    'health_check.db',
    'health_check.storage',
    'health_check.contrib.migrations',
    'health_check.contrib.celery_ping',
    'health_check.contrib.redis',
    'rest_framework',
    'django_celery_beat',
    'django_celery_results',
    'apps.allocations',
    'apps.admin_utils',
    'apps.docs',
    'apps.health',
    'apps.research_products',
    'apps.scheduler',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Base styling for the Admin UI

JAZZMIN_SETTINGS = {
    "site_title": "CRC Self Service",
    "site_header": "CRC Self Service",
    "site_brand": "CRC Self Service",
    "hide_apps": ["sites"],
    "order_with_respect_to": [
        "users",
        "allocations",
        "research_products",
        "sites"
    ],
    "icons": {},
    "site_logo": "theme/img/logo/Shield_White.png",
    "login_logo": "theme/img/logo/Pitt_Primary_3Color_small.png",
}

# REST API settings

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env.str('API_THROTTLE_ANON', default='1000/day'),
        'user': env.str('API_THROTTLE_USER', default='10000/day')
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
}

if DEBUG:  # Disable the API GUI if not in debug mode
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append('rest_framework.renderers.BrowsableAPIRenderer')

# Celery scheduler

CELERY_BROKER_URL = env.url('CELERY_BROKER_URL', "redis://127.0.0.1:6379/0").geturl()
CELERY_RESULT_BACKEND = env.url('CELERY_RESULT_BACKEND', "redis://127.0.0.1:6379/0").geturl()
CELERY_CACHE_BACKEND = 'django-cache'

# Database

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_DB_PATH = BASE_DIR / 'keystone.db'
DATABASES = {
    'default': env.db('DATABASE_URL', f'sqlite:///{DEFAULT_DB_PATH}')
}

# Authentication

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

if AUTH_LDAP_SERVER_URI := env.url("AUTH_LDAP_SERVER_URI", "").geturl():
    import ldap
    from django_auth_ldap.config import LDAPSearch

    AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

    AUTH_LDAP_MIRROR_GROUPS = True
    AUTH_LDAP_ALWAYS_UPDATE_USER = True
    AUTH_LDAP_START_TLS = env.bool("AUTH_LDAP_START_TLS", True)
    AUTH_LDAP_BIND_DN = env.str("AUTH_LDAP_BIND_DN", "")
    AUTH_LDAP_BIND_PASSWORD = env.str("AUTH_LDAP_BIND_PASSWORD", "")
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        env.str("AUTH_LDAP_USER_SEARCH", ""),
        ldap.SCOPE_SUBTREE,
        "(uid=%(user)s)"
    )

    if env.bool('AUTH_LDAP_REQUIRE_CERT', True):
        AUTH_LDAP_GLOBAL_OPTIONS = {ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Static file handling (CSS, JavaScript, Images)

STATIC_URL = env.str('STATIC_URL', 'static/')
STATIC_ROOT = env.path('STATIC_ROOT', BASE_DIR / 'static_root')
