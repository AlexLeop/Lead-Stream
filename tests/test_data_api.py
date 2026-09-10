from __future__ import annotations

from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from leadstream.entities.services import create_company
from leadstream.tenancy.models import Tenant

pytestmark = pytest.mark.django_db


def post_ok(client: APIClient, path: str, data: dict[str, Any]) -> dict[str, Any]:
    response = client.post(path, data, format="json")
    assert response.status_code == 201, response.json()
    result: dict[str, Any] = response.json()
    return result


def test_fluxo_http_canonico_com_proveniencia_e_supressao(api_client: APIClient) -> None:
    company = post_ok(
        api_client,
        "/api/v1/dados/empresas/",
        {
            "cnpj": "04.252.011/0001-10",
            "legal_name": "Empresa Exemplo S.A.",
            "trade_name": "Empresa Exemplo",
            "registration_status": "ATIVA",
        },
    )
    person = post_ok(
        api_client,
        "/api/v1/dados/pessoas/",
        {
            "full_name": "João da Silva",
            "external_key": "provider-person-1",
            "cpf": "529.982.247-25",
        },
    )
    assert "cpf" not in person
    assert "cpf_hash" not in person
    assert person["cpf_masked"] == "***.982.247-**"

    relationship = post_ok(
        api_client,
        "/api/v1/dados/vinculos/",
        {
            "person": person["entity_id"],
            "company": company["entity_id"],
            "qualification": "ADMINISTRATOR",
            "observed_title": "Diretor Comercial",
            "seniority": "DIRECTOR",
            "buying_role": "Decisor",
            "buying_role_is_inferred": True,
        },
    )
    assert relationship["observed_title"] == "Diretor Comercial"
    assert relationship["buying_role_is_inferred"] is True

    contact = post_ok(
        api_client,
        "/api/v1/dados/contatos/",
        {
            "owner": person["entity_id"],
            "kind": "EMAIL",
            "original_value": "JOAO@EXAMPLE.COM",
            "status": "OBSERVED",
            "capabilities": {"mx_domain": True, "mailbox": False},
        },
    )
    assert contact["original_value"] == "JOAO@EXAMPLE.COM"
    assert contact["normalized_value"] == "joao@example.com"
    assert contact["capabilities"]["mailbox"] is False

    profile = post_ok(
        api_client,
        "/api/v1/dados/perfis-sociais/",
        {
            "owner": person["entity_id"],
            "network": "LINKEDIN",
            "profile_url": "http://linkedin.com/in/joao/",
            "handle": "@joao",
        },
    )
    assert profile["normalized_url"] == "https://linkedin.com/in/joao"

    purpose = post_ok(
        api_client,
        "/api/v1/dados/finalidades/",
        {
            "code": "prospeccao-b2b",
            "name": "Prospecção B2B",
            "description": "Relacionamento profissional com decisores.",
            "operational_basis": "Legítimo interesse documentado.",
            "is_active": True,
        },
    )
    retention = post_ok(
        api_client,
        "/api/v1/dados/retencao/politicas/",
        {
            "code": "contato-profissional",
            "name": "Contato profissional",
            "stale_after_days": 90,
            "retention_days": 365,
            "is_active": True,
        },
    )
    source = post_ok(
        api_client,
        "/api/v1/dados/fontes/",
        {
            "slug": "fixture-publica",
            "name": "Fixture pública",
            "category": "PUBLIC_WEB",
            "priority": 50,
            "terms_url": "https://example.test/termos",
            "is_active": True,
        },
    )
    captured_at = timezone.now().isoformat()
    record = post_ok(
        api_client,
        "/api/v1/dados/fontes/registros/",
        {
            "source": source["id"],
            "purpose": purpose["id"],
            "retention_policy": retention["id"],
            "external_id": "public-profile-1",
            "source_url": "https://example.test/perfil/1",
            "captured_at": captured_at,
            "payload_hash": "a" * 64,
        },
    )
    evidence = post_ok(
        api_client,
        "/api/v1/dados/evidencias/",
        {
            "source_record": record["id"],
            "url": "https://example.test/perfil/1",
            "captured_at": captured_at,
            "observed_at": captured_at,
            "method": "WEB_PAGE",
            "excerpt_hash": "b" * 64,
            "content_hash": "c" * 64,
            "metadata": {"public": True},
        },
    )
    observation = post_ok(
        api_client,
        "/api/v1/dados/observacoes/",
        {
            "target": person["entity_id"],
            "source_record": record["id"],
            "field_path": "person.email",
            "value": "joao@example.com",
            "status": "CONFIRMED",
            "confidence": 95,
            "method": "WEB_PAGE",
            "observed_at": captured_at,
            "captured_at": captured_at,
            "evidence_ids": [evidence["id"]],
        },
    )
    assert observation["source_name"] == "Fixture pública"
    assert observation["purpose_code"] == "prospeccao-b2b"
    assert observation["status"] == "CONFIRMED"

    decision = post_ok(
        api_client,
        "/api/v1/dados/canonizar/",
        {
            "target": person["entity_id"],
            "field_path": "person.email",
            "policy_version": "canonical-v1",
        },
    )
    assert decision["decision_status"] == "CONFIRMED"
    assert decision["selected_value"] == "joao@example.com"
    assert decision["source_name"] == "Fixture pública"

    suppression = post_ok(
        api_client,
        "/api/v1/dados/supressoes/",
        {
            "scope": "EMAIL",
            "value": "joao@example.com",
            "reason": "Opt-out",
        },
    )
    assert "value" not in suppression
    assert "value_digest" not in suppression
    after_suppression = post_ok(
        api_client,
        "/api/v1/dados/canonizar/",
        {"target": person["entity_id"], "field_path": "person.email"},
    )
    assert after_suppression["version"] == 2
    assert after_suppression["decision_status"] == "ABSENT"
    assert after_suppression["selected_observation"] is None


def test_api_rejeita_tenant_arbitrario_e_isola_listagem(api_client: APIClient) -> None:
    rejected = api_client.post(
        "/api/v1/dados/empresas/",
        {
            "tenant_id": "00000000-0000-0000-0000-000000000999",
            "cnpj": "04.252.011/0001-10",
            "legal_name": "Não deve criar",
        },
        format="json",
    )
    assert rejected.status_code == 400

    created = post_ok(
        api_client,
        "/api/v1/dados/empresas/",
        {"cnpj": "04.252.011/0001-10", "legal_name": "Empresa interna"},
    )
    other = Tenant.objects.create(slug="other", name="Outro tenant")
    create_company(
        tenant=other,
        cnpj="11.222.333/0001-81",
        legal_name="Empresa invisível",
    )
    response = api_client.get("/api/v1/dados/empresas/?page_size=1000")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["results"][0]["entity_id"] == created["entity_id"]
