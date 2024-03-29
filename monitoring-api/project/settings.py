"""
Django settings for monitoring project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import json
import logging
import os

import environ

log = logging.getLogger(__name__)

env = environ.Env()
# Reading .env file
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug on in production!
DEBUG = env("DEBUG", default=False)

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [env("MONITORING_API_HOST", default="localhost")]
    hosts = env("ALLOWED_HOSTS", default=None)
    if hosts:
        log.debug(f"Attempting to add hosts {hosts} to {ALLOWED_HOSTS}")
        ALLOWED_HOSTS += json.loads(hosts)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "lwf",
    "gcnet",
    "generic",
    "rest_framework",
    "drf_spectacular",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASE_ROUTERS = ["project.routers.MonitoringRouter"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
    },
    "lwf": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "OPTIONS": {"options": env("LWF_DB_SCHEMA")},
        "NAME": env("LWF_DB_NAME"),
        "USER": env("LWF_DB_USER"),
        "PASSWORD": env("LWF_DB_PASSWORD"),
        "HOST": env("LWF_DB_HOST"),
        "PORT": env("LWF_DB_PORT"),
    },
    "gcnet": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "OPTIONS": {"options": env("GCNET_DB_SCHEMA")},
        "NAME": env("GCNET_DB_NAME"),
        "USER": env("GCNET_DB_USER"),
        "PASSWORD": env("GCNET_DB_PASSWORD"),
        "HOST": env("GCNET_DB_HOST"),
        "PORT": env("GCNET_DB_PORT"),
    },
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": (
                "%(asctime)s.%(msecs)03d [%(levelname)s] "
                "%(name)s | %(funcName)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "": {
            "level": env("LOG_LEVEL", default="DEBUG"),
            "handlers": ["console"],
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

proxy_prefix = env("PROXY_PREFIX", default="")
FORCE_SCRIPT_NAME = f"{proxy_prefix}/"
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

app_version = "2.1.0"
SPECTACULAR_SETTINGS = {
    "TITLE": "EnviDat Monitoring API",
    "DESCRIPTION": "Django API for WSL long-term environmental monitoring data.",
    "VERSION": app_version,
    "SCHEMA_PATH_PREFIX_INSERT": f"{proxy_prefix}",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
if DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
STATIC_URL = f"{proxy_prefix}/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "..", "static")
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "..", "generic/static"),
    os.path.join(PROJECT_ROOT, "..", "lwf/static"),
    os.path.join(PROJECT_ROOT, "..", "gcnet/static"),
]

# # Dynamic output content is saved here
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'
#
# INTERNAL_IPS = [
#     '127.0.0.1',
#  ]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
