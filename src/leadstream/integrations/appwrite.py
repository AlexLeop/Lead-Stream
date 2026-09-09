from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol, Self

import httpx
from django.conf import settings

from leadstream.common.health import HealthResult


@dataclass(frozen=True, slots=True)
class AppwriteConfig:
    endpoint: str
    project_id: str
    api_key: str = field(repr=False)
    timeout_seconds: float = 3.0

    @classmethod
    def from_settings(cls) -> Self | None:
        values = (
            settings.APPWRITE_ENDPOINT,
            settings.APPWRITE_PROJECT_ID,
            settings.APPWRITE_API_KEY,
        )
        if not all(values):
            return None
        return cls(
            endpoint=str(settings.APPWRITE_ENDPOINT).rstrip("/"),
            project_id=str(settings.APPWRITE_PROJECT_ID),
            api_key=str(settings.APPWRITE_API_KEY),
            timeout_seconds=float(settings.APPWRITE_TIMEOUT_SECONDS),
        )


class AppwriteHealthClient(Protocol):
    def check(self) -> None: ...


class HttpAppwriteHealthClient:
    def __init__(self, config: AppwriteConfig) -> None:
        self._config = config

    def check(self) -> None:
        headers = {
            "X-Appwrite-Project": self._config.project_id,
            "X-Appwrite-Key": self._config.api_key,
        }
        with httpx.Client(
            timeout=self._config.timeout_seconds,
            follow_redirects=False,
        ) as client:
            response = client.get(f"{self._config.endpoint}/health", headers=headers)
            response.raise_for_status()


def diagnose_appwrite(
    client_factory: Callable[[AppwriteConfig], AppwriteHealthClient] = HttpAppwriteHealthClient,
) -> HealthResult:
    config = AppwriteConfig.from_settings()
    if config is None:
        return HealthResult("degraded")
    try:
        client_factory(config).check()
    except httpx.HTTPError:
        return HealthResult("unavailable")
    except (OSError, ValueError):
        return HealthResult("unavailable")
    return HealthResult("ok")
