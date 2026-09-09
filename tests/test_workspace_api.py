from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from leadstream.tenancy.models import Tenant


@pytest.mark.django_db
def test_workspace_retorna_tenant_interno_persistido(api_client: APIClient) -> None:
    tenant = Tenant.objects.get(slug="internal")

    response = api_client.get("/api/v1/workspace/")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(tenant.id),
        "slug": "internal",
        "nome": "Operação interna",
        "ativo": True,
    }


@pytest.mark.django_db
def test_workspace_nao_exige_sessao_ou_token(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/workspace/")

    assert response.status_code == 200
