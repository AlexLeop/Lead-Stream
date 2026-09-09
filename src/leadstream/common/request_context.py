from __future__ import annotations

import re
import uuid
from collections.abc import Callable
from contextvars import ContextVar, Token

from django.http import HttpRequest, HttpResponseBase
from structlog.contextvars import bind_contextvars, clear_contextvars

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestContextMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        request_id = _resolve_request_id(request.headers.get(REQUEST_ID_HEADER))
        token = _request_id.set(request_id)
        clear_contextvars()
        bind_contextvars(request_id=request_id, tenant="internal")
        try:
            response = self.get_response(request)
            response[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            clear_contextvars()
            _reset_request_id(token)


def current_request_id() -> str | None:
    return _request_id.get()


def bind_operation_context(
    *,
    batch_id: str | None = None,
    chunk_id: str | None = None,
    provider: str | None = None,
) -> None:
    values = {
        key: value
        for key, value in {
            "batch_id": batch_id,
            "chunk_id": chunk_id,
            "provider": provider,
        }.items()
        if value is not None
    }
    bind_contextvars(**values)


def _resolve_request_id(candidate: str | None) -> str:
    if candidate and REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return uuid.uuid4().hex


def _reset_request_id(token: Token[str | None]) -> None:
    _request_id.reset(token)
