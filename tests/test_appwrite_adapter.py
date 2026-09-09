from __future__ import annotations

from collections.abc import Callable

import httpx
from django.test import override_settings

from leadstream.integrations.appwrite import (
    AppwriteConfig,
    AppwriteHealthClient,
    diagnose_appwrite,
)


class SuccessfulClient:
    def __init__(self, config: AppwriteConfig) -> None:
        self.config = config

    def check(self) -> None:
        return None


class FailingClient:
    def __init__(self, config: AppwriteConfig, error_factory: Callable[[], Exception]) -> None:
        self.config = config
        self.error_factory = error_factory

    def check(self) -> None:
        raise self.error_factory()


CONFIGURED_SETTINGS = {
    "APPWRITE_ENDPOINT": "https://appwrite.example.com/v1",
    "APPWRITE_PROJECT_ID": "project-placeholder",
    "APPWRITE_API_KEY": "sentinel-private-key",
    "APPWRITE_TIMEOUT_SECONDS": 1,
}


@override_settings(
    APPWRITE_ENDPOINT=None,
    APPWRITE_PROJECT_ID=None,
    APPWRITE_API_KEY=None,
)
def test_appwrite_ausente_retorna_degradado_sem_rede() -> None:
    called = False

    def factory(config: AppwriteConfig) -> AppwriteHealthClient:
        nonlocal called
        called = True
        return SuccessfulClient(config)

    assert diagnose_appwrite(factory).status == "degraded"
    assert called is False


@override_settings(**CONFIGURED_SETTINGS)
def test_appwrite_saudavel_retorna_ok_e_oculta_chave() -> None:
    captured: AppwriteConfig | None = None

    def factory(config: AppwriteConfig) -> AppwriteHealthClient:
        nonlocal captured
        captured = config
        return SuccessfulClient(config)

    assert diagnose_appwrite(factory).status == "ok"
    assert captured is not None
    assert "sentinel-private-key" not in repr(captured)


@override_settings(**CONFIGURED_SETTINGS)
def test_appwrite_401_retorna_indisponivel_sem_expor_resposta() -> None:
    request = httpx.Request("GET", "https://appwrite.example.com/v1/health")
    response = httpx.Response(401, request=request)

    def factory(config: AppwriteConfig) -> AppwriteHealthClient:
        return FailingClient(
            config,
            lambda: httpx.HTTPStatusError(
                "sentinel-private-key",
                request=request,
                response=response,
            ),
        )

    assert diagnose_appwrite(factory).status == "unavailable"


@override_settings(**CONFIGURED_SETTINGS)
def test_appwrite_timeout_retorna_indisponivel() -> None:
    request = httpx.Request("GET", "https://appwrite.example.com/v1/health")

    def factory(config: AppwriteConfig) -> AppwriteHealthClient:
        return FailingClient(config, lambda: httpx.ReadTimeout("timeout", request=request))

    assert diagnose_appwrite(factory).status == "unavailable"
