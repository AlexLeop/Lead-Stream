from __future__ import annotations

from functools import lru_cache
from uuid import UUID

from django.core.exceptions import ImproperlyConfigured

from .models import Tenant

INTERNAL_TENANT_ID = UUID("00000000-0000-4000-8000-000000000001")
INTERNAL_TENANT_SLUG = "internal"


def get_internal_tenant() -> Tenant:
    try:
        return Tenant.objects.get(slug=INTERNAL_TENANT_SLUG, is_active=True)
    except Tenant.DoesNotExist as exc:
        raise ImproperlyConfigured(
            "O tenant interno não foi provisionado. Execute as migrations antes de iniciar a API."
        ) from exc


@lru_cache(maxsize=1)
def get_internal_tenant_id() -> UUID:
    return get_internal_tenant().pk
