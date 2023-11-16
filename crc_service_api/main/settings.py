"""Top level Django application settings."""

import importlib.metadata
import os
import sys
from pathlib import Path

import ldap
from django.core.management.utils import get_random_secret_key
from django_auth_ldap.config import LDAPSearch
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
VERSION = importlib.metadata.version('crc-service-api')

sys.path.insert(0, str(BASE_DIR))
load_dotenv()

# Debugging features/settings
if DEBUG := (os.environ.get('DEBUG', default='0') != '0'):
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = Path(os.environ.get('EMAIL_FILE_PATH', BASE_DIR / 'email'))

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default="localhost 127.0.0.1").split(" ")
AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# LDAP Settings
AUTH_LDAP_MIRROR_GROUPS = True
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_START_TLS = os.environ.get("AUTH_LDAP_START_TLS", "1") != '0'
AUTH_LDAP_SERVER_URI = os.environ.get("AUTH_LDAP_SERVER_URI", "")
AUTH_LDAP_BIND_DN = os.environ.get("AUTH_LDAP_BIND_DN", "")
AUTH_LDAP_BIND_PASSWORD = os.environ.get("AUTH_LDAP_BIND_PASSWORD", "")
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.environ.get("AUTH_LDAP_USER_SEARCH", ""),
    ldap.SCOPE_SUBTREE,
    "(uid=%(user)s)"
)

if os.environ.get('OPT_X_TLS_REQUIRE_CERT', "1") == "0":
    AUTH_LDAP_GLOBAL_OPTIONS = {ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER}

# Application Configuration

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
        'DIRS': [BASE_DIR / 'templates', ],
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
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

if DEBUG:  # Disable the API GUI if not in debug mode
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append('rest_framework.renderers.BrowsableAPIRenderer')

else:  # Only enforce API permissions in production
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ['rest_framework.permissions.IsAuthenticated']

# Celery scheduler
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', "redis://127.0.0.1:6379/0")
CELERY_CACHE_BACKEND = 'django-cache'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

_driver = os.environ.get('DB_DRIVER', 'sqlite3')
_name = BASE_DIR / 'crc_service.sqlite3' if _driver == 'sqlite3' else 'crc_service'
DATABASES = {
    'default': {
        "ENGINE": f'django.db.backends.{_driver}',
        "NAME": os.environ.get('DB_NAME', _name),
        "USER": os.environ.get('DB_USER', ''),
        "PASSWORD": os.environ.get('DB_PASSWORD', ''),
        "HOST": os.environ.get('DB_HOST', 'localhost'),
        "PORT": os.environ.get('DB_PORT', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = os.environ.get('STATIC_URL', 'static/')
STATIC_ROOT = Path(os.environ.get('STATIC_ROOT', BASE_DIR / 'static_root'))
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
