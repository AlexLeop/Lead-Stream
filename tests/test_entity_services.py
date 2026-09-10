from __future__ import annotations

from datetime import date

import pytest
from django.core.exceptions import ValidationError

from leadstream.entities.models import ContactPoint, Entity, Person, Relationship
from leadstream.entities.normalization import DataValidationError
from leadstream.entities.services import (
    create_company,
    create_contact_point,
    create_person,
    create_relationship,
    create_social_profile,
)
from leadstream.tenancy.models import Tenant
from leadstream.tenancy.services import get_internal_tenant

pytestmark = pytest.mark.django_db


def test_criacao_empresa_e_estabelecimento_e_idempotente() -> None:
    tenant = get_internal_tenant()
    first = create_company(
        tenant=tenant,
        cnpj="04.252.011/0001-10",
        legal_name="Empresa Exemplo S.A.",
    )
    second = create_company(
        tenant=tenant,
        cnpj="04252011000110",
        legal_name="Empresa Exemplo S.A.",
    )
    assert first.company.pk == second.company.pk
    assert first.establishment.pk == second.establishment.pk
    assert first.company.cnpj_root == "04252011"
    assert first.establishment.is_headquarters is True


def test_rejeita_cnpj_invalido() -> None:
    with pytest.raises(DataValidationError, match="CNPJ inválido"):
        create_company(tenant=get_internal_tenant(), cnpj="123", legal_name="Inválida")


def test_pessoa_vinculo_contato_e_perfil_sem_cpf_integral() -> None:
    tenant = get_internal_tenant()
    identity = create_company(
        tenant=tenant,
        cnpj="04.252.011/0001-10",
        legal_name="Empresa Exemplo S.A.",
    )
    person = create_person(
        tenant=tenant,
        full_name="João da Silva",
        cpf="529.982.247-25",
        hash_key="test-only-hash-key",
    )
    same_person = create_person(
        tenant=tenant,
        full_name="João da Silva",
        cpf="52998224725",
        hash_key="test-only-hash-key",
    )
    relationship = create_relationship(
        tenant=tenant,
        person=person,
        company=identity.company,
        qualification=Relationship.Qualification.ADMINISTRATOR,
        observed_title="Diretor Comercial",
        normalized_title="diretor comercial",
        seniority=Relationship.Seniority.DIRECTOR,
        buying_role="Decisor",
        buying_role_is_inferred=True,
        started_on=date(2020, 1, 1),
    )
    email = create_contact_point(
        tenant=tenant,
        owner=person.entity,
        kind=ContactPoint.Kind.EMAIL,
        value="JOAO@EXEMPLO.COM.BR",
    )
    whatsapp = create_contact_point(
        tenant=tenant,
        owner=person.entity,
        kind=ContactPoint.Kind.WHATSAPP,
        value="(11) 99876-5432",
    )
    profile = create_social_profile(
        tenant=tenant,
        owner=person.entity,
        network="LINKEDIN",
        profile_url="http://LinkedIn.com/in/joao/",
        handle="@joao",
    )

    assert same_person.pk == person.pk
    assert person.cpf_masked == "***.982.247-**"
    assert person.cpf_hash and "52998224725" not in person.cpf_hash
    assert "cpf" not in {field.name for field in Person._meta.fields}
    assert relationship.buying_role_is_inferred is True
    assert email.normalized_value == "joao@exemplo.com.br"
    assert whatsapp.status == ContactPoint.Status.OBSERVED
    assert whatsapp.capabilities == {}
    assert profile.normalized_url == "https://linkedin.com/in/joao"


def test_rejeita_referencias_entre_tenants() -> None:
    internal = get_internal_tenant()
    other = Tenant.objects.create(slug="other", name="Outro tenant")
    person = create_person(tenant=internal, full_name="Decisor", external_key="person-1")
    company = create_company(
        tenant=other,
        cnpj="11.222.333/0001-81",
        legal_name="Outra Empresa Ltda.",
    ).company

    with pytest.raises(ValidationError, match="mesmo tenant"):
        create_relationship(
            tenant=internal,
            person=person,
            company=company,
            qualification=Relationship.Qualification.ADMINISTRATOR,
        )

    other_entity = Entity.objects.get(pk=company.entity_id)
    with pytest.raises(ValidationError, match="mesmo tenant"):
        create_contact_point(
            tenant=internal,
            owner=other_entity,
            kind=ContactPoint.Kind.PHONE,
            value="1134567890",
        )


def test_rejeita_cpf_invalido_sem_persistir_identificador() -> None:
    with pytest.raises(DataValidationError, match="CPF inválido"):
        create_person(
            tenant=get_internal_tenant(),
            full_name="Pessoa Inválida",
            cpf="529.982.247-26",
            hash_key="test-only-hash-key",
        )
    assert Person.objects.count() == 0
