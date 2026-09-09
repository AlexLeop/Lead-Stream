from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from django.conf import settings
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from kombu import Connection as BrokerConnection
from redis import Redis

HealthStatus = Literal["ok", "degraded", "unavailable"]
REQUIRED_MIGRATIONS = frozenset({("tenancy", "0002_seed_internal_tenant")})


@dataclass(frozen=True, slots=True)
class HealthResult:
    status: HealthStatus

    @property
    def available(self) -> bool:
        return self.status == "ok"

    def as_dict(self) -> dict[str, HealthStatus]:
        return {"status": self.status}


def check_database() -> HealthResult:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        applied = MigrationRecorder(connection).applied_migrations()
        if not REQUIRED_MIGRATIONS.issubset(applied):
            return HealthResult("unavailable")
    except Exception:  # noqa: BLE001 - health nunca devolve detalhes da infraestrutura
        return HealthResult("unavailable")
    return HealthResult("ok")


def check_redis() -> HealthResult:
    client: Redis | None = None
    try:
        client = Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=settings.DEPENDENCY_CHECK_TIMEOUT_SECONDS,
            socket_timeout=settings.DEPENDENCY_CHECK_TIMEOUT_SECONDS,
        )
        return HealthResult("ok" if client.ping() else "unavailable")
    except Exception:  # noqa: BLE001 - o contrato é propositalmente sanitizado
        return HealthResult("unavailable")
    finally:
        if client is not None:
            client.close()


def check_rabbitmq() -> HealthResult:
    broker: BrokerConnection | None = None
    try:
        broker = BrokerConnection(
            settings.CELERY_BROKER_URL,
            connect_timeout=settings.DEPENDENCY_CHECK_TIMEOUT_SECONDS,
        )
        broker.ensure_connection(max_retries=0)
        return HealthResult("ok")
    except Exception:  # noqa: BLE001 - o contrato é propositalmente sanitizado
        return HealthResult("unavailable")
    finally:
        if broker is not None:
            broker.release()


def check_appwrite() -> HealthResult:
    try:
        from leadstream.integrations.appwrite import diagnose_appwrite

        return diagnose_appwrite()
    except ImportError:
        return HealthResult("degraded")
    except Exception:  # noqa: BLE001 - adapter opcional nunca vaza exceção
        return HealthResult("unavailable")


def check_dependencies() -> dict[str, HealthResult]:
    return {
        "redis": check_redis(),
        "rabbitmq": check_rabbitmq(),
        "appwrite": check_appwrite(),
    }
