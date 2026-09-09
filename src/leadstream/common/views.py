from __future__ import annotations

from django.http import HttpRequest, JsonResponse

from .health import HealthResult, check_database, check_dependencies


def live(request: HttpRequest) -> JsonResponse:
    del request
    return JsonResponse({"status": "ok"})


def ready(request: HttpRequest) -> JsonResponse:
    del request
    database = check_database()
    status_code = 200 if database.available else 503
    return JsonResponse(
        {"status": "ok" if database.available else "unavailable"},
        status=status_code,
    )


def dependencies(request: HttpRequest) -> JsonResponse:
    del request
    results = check_dependencies()
    overall = _aggregate_dependency_status(results)
    return JsonResponse(
        {
            "status": overall,
            "dependencias": {name: result.as_dict() for name, result in results.items()},
        }
    )


def _aggregate_dependency_status(results: dict[str, HealthResult]) -> str:
    return "ok" if all(result.available for result in results.values()) else "degraded"
