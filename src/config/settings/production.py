from __future__ import annotations

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from leadstream.common.env import env_bool, env_int, env_list, required_env

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = required_env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", required=True)

production_database_url = required_env("DATABASE_URL")
DATABASES = {
    "default": dj_database_url.parse(
        production_database_url,
        conn_max_age=env_int("DATABASE_CONN_MAX_AGE", default=60),
        conn_health_checks=True,
        ssl_require=env_bool("DATABASE_SSL_REQUIRED", default=False),
    )
}

if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("DATABASE_URL deve apontar para PostgreSQL em produção.")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
