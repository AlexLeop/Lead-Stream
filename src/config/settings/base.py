from __future__ import annotations

from pathlib import Path

import dj_database_url

from leadstream.common.env import env, env_bool, env_int, env_list

BASE_DIR = Path(__file__).resolve().parents[3]

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-only-unsafe-secret-key")
DEBUG = env_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "leadstream.tenancy.apps.TenancyConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

DATABASE_URL = env(
    "DATABASE_URL",
    default="postgresql://leadstream:leadstream@localhost:5432/leadstream",
)
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=env_int("DATABASE_CONN_MAX_AGE", default=60),
        conn_health_checks=True,
    )
}

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "UNAUTHENTICATED_USER": None,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "LeadStream API",
    "DESCRIPTION": "API interna para higienização e enriquecimento confiável de leads.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
