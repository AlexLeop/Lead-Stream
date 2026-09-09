from __future__ import annotations

import os
import subprocess
import sys


def test_producao_falha_sem_variaveis_obrigatorias() -> None:
    environment = _clean_environment()

    result = _load_django(environment)

    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY" in result.stderr
    assert "obrigat" in result.stderr


def test_producao_rejeita_sqlite() -> None:
    environment = _clean_environment()
    environment.update(
        {
            "DJANGO_SECRET_KEY": "test-only-long-secret-that-is-never-used-in-production",
            "DJANGO_ALLOWED_HOSTS": "test.invalid",
            "DATABASE_URL": "sqlite:///test.sqlite3",
            "CELERY_BROKER_URL": "amqp://test:test@localhost:5672//",
            "REDIS_URL": "redis://localhost:6379/15",
        }
    )

    result = _load_django(environment)

    assert result.returncode != 0
    assert "DATABASE_URL" in result.stderr
    assert "PostgreSQL" in result.stderr


def _clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in (
        "DJANGO_SECRET_KEY",
        "DJANGO_ALLOWED_HOSTS",
        "DATABASE_URL",
        "CELERY_BROKER_URL",
        "REDIS_URL",
    ):
        environment.pop(name, None)
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
    environment["PYTHONIOENCODING"] = "utf-8"
    return environment


def _load_django(environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
