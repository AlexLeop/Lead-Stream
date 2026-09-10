from __future__ import annotations

from pathlib import Path

import dj_database_url

from leadstream.common.env import env, env_bool, env_int, env_list
from leadstream.common.logging import build_logging_config

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
    "leadstream.entities.apps.EntitiesConfig",
    "leadstream.evidence.apps.EvidenceConfig",
    "leadstream.governance.apps.GovernanceConfig",
    "leadstream.batches.apps.BatchesConfig",
    "leadstream.billing.apps.BillingConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "leadstream.common.request_context.RequestContextMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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

CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL",
    default="amqp://leadstream:leadstream@localhost:5672//",
)
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}
CELERY_RESULT_BACKEND = None
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_TRACK_STARTED = False
CELERY_TASK_TIME_LIMIT = env_int("CELERY_TASK_TIME_LIMIT", default=600)
CELERY_TASK_SOFT_TIME_LIMIT = env_int("CELERY_TASK_SOFT_TIME_LIMIT", default=540)
CELERY_BEAT_SCHEDULE = {
    "recover-stalled-batches": {
        "task": "leadstream.batches.recover",
        "schedule": 60.0,
    }
}
DEPENDENCY_CHECK_TIMEOUT_SECONDS = env_int("DEPENDENCY_CHECK_TIMEOUT_SECONDS", default=2)
APPWRITE_ENDPOINT = env("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = env("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = env("APPWRITE_API_KEY")
APPWRITE_TIMEOUT_SECONDS = env_int("APPWRITE_TIMEOUT_SECONDS", default=3)
DATA_HASH_KEY = env("DATA_HASH_KEY", default="dev-only-data-hash-key")
DATA_HASH_KEY_VERSION = env("DATA_HASH_KEY_VERSION", default="v1")
DATA_HASH_PREVIOUS_KEYS = env_list("DATA_HASH_PREVIOUS_KEYS", default=[])
BATCH_STORAGE_ROOT = Path(env("BATCH_STORAGE_ROOT", default=str(BASE_DIR / "data" / "batches")))
BATCH_MAX_UPLOAD_BYTES = env_int("BATCH_MAX_UPLOAD_BYTES", default=50 * 1024 * 1024)
BATCH_MAX_ROWS = env_int("BATCH_MAX_ROWS", default=100_000)
BATCH_LEASE_SECONDS = env_int("BATCH_LEASE_SECONDS", default=300)
LOG_LEVEL = env("LOG_LEVEL", default="INFO")
LOGGING = build_logging_config(LOG_LEVEL)

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
    "DEFAULT_PAGINATION_CLASS": "leadstream.common.pagination.StandardPagination",
    "PAGE_SIZE": 50,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "LeadStream API",
    "DESCRIPTION": "API interna para higienização e enriquecimento confiável de leads.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "ENUM_NAME_OVERRIDES": {
        "ContactStatusEnum": "leadstream.entities.models.CONTACT_POINT_STATUS_CHOICES",
        "EvidenceStatusEnum": "leadstream.evidence.models.EvidenceStatus.choices",
        "ConflictStatusEnum": ["OPEN", "RESOLVED"],
        "RetentionRunStatusEnum": ["RUNNING", "COMPLETED", "FAILED"],
        "ContactPointScopeEnum": "leadstream.entities.models.CONTACT_POINT_SCOPE_CHOICES",
        "SuppressionScopeEnum": "leadstream.governance.models.SUPPRESSION_SCOPE_CHOICES",
        "DataBlockEnum": "leadstream.billing.models.DATA_BLOCK_CHOICES",
    },
}
