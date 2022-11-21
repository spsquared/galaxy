"""
Django settings for siarnaq project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import json
import os
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

import siarnaq.gcloud as gcloud
from siarnaq.gcloud import secret

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Detect environment, in particular which backend system is in use
SIARNAQ_MODE = os.getenv("SIARNAQ_MODE", None)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-2r0p5r8#j1!4v%cb@w#_^)6+^#vs5b*9mqf)!q)pz!5tqnbx*("

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "play.battlecode.org",
    "staging.battlecode.org",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "siarnaq.api.user",
    "siarnaq.api.compete",
    "siarnaq.api.episodes",
    "siarnaq.api.teams",
    "drf_spectacular",
    "django_rest_passwordreset",
    "anymail",
]

MIDDLEWARE = [
    # Place CORS first. See https://stackoverflow.com/a/45376281
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "siarnaq.urls"

SITE_ID = 1

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "siarnaq/templates")],
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

WSGI_APPLICATION = "siarnaq.wsgi.application"

# Parse our secrets from secret manager
match SIARNAQ_MODE:
    case "PRODUCTION":
        SIARNAQ_SECRETS_JSON = secret.get_secret("production-siarnaq-secrets").decode()

    case "STAGING":
        SIARNAQ_SECRETS_JSON = secret.get_secret("staging-siarnaq-secrets").decode()

    case _:
        SIARNAQ_SECRETS_JSON = "{}"  # an empty json

SIARNAQ_SECRETS = defaultdict(lambda: None, json.loads(SIARNAQ_SECRETS_JSON))

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

match SIARNAQ_MODE:
    case "PRODUCTION":
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "NAME": "battlecode",
                "USER": "siarnaq",
                "PASSWORD": SIARNAQ_SECRETS["db-password"],
                "HOST": (
                    f"/cloudsql/{gcloud.project_id}:"
                    f"{gcloud.location}:production-siarnaq-db"
                ),
                "PORT": 5432,
            }
        }

    case "STAGING":
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "NAME": "battlecode",
                "USER": "siarnaq",
                "PASSWORD": SIARNAQ_SECRETS["db-password"],
                "HOST": "db.staging.battlecode.org",
                "PORT": 5432,
            }
        }

    case _:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(BASE_DIR / "db.sqlite3"),
            }
        }

# Custom user model
# https://docs.djangoproject.com/en/4.0/topics/auth/customizing

AUTH_USER_MODEL = "user.User"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
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

# Authentication with simple JWT
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "siarnaq.api.user.authentication.GoogleCloudAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
}


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Penalized Elo configuration

TEAMS_ELO_INITIAL = 1500.0
TEAMS_ELO_K = 24.0
TEAMS_ELO_SCALE = 400.0
TEAMS_ELO_PENALTY = 0.85

# Team limits

TEAMS_MAX_TEAM_SIZE = 4

# User avatar settings

USER_MAX_AVATAR_SIZE = (512, 512)

# Email config

EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
EMAIL_HOST_USER = "no-reply@battlecode.org"
ANYMAIL = {
    "MAILJET_API_KEY": SIARNAQ_SECRETS["mailjet-api-key"],
    "MAILJET_SECRET_KEY": SIARNAQ_SECRETS["mailjet-api-secret"],
}

# When testing, feel free to change this.
# ! Make sure to change it back before committing to main!
EMAIL_ENABLED = SIARNAQ_MODE == "PRODUCTION"
