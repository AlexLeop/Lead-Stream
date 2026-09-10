from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

from leadstream.tenancy.models import Tenant

from .models import Company, ContactPoint, Establishment, Person, Relationship, SocialProfile
from .services import (
    create_company,
    create_contact_point,
    create_person,
    create_relationship,
    create_social_profile,
)


class EstablishmentSerializer(serializers.ModelSerializer[Establishment]):
    entity_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Establishment
        fields = (
            "entity_id",
            "cnpj",
            "is_headquarters",
            "registration_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CompanyReadSerializer(serializers.ModelSerializer[Company]):
    entity_id = serializers.UUIDField(read_only=True)
    establishments = EstablishmentSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = (
            "entity_id",
            "cnpj_root",
            "legal_name",
            "trade_name",
            "registration_status",
            "opened_on",
            "establishments",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CompanyCreateSerializer(serializers.Serializer[Company]):
    cnpj = serializers.CharField(max_length=32)
    legal_name = serializers.CharField(max_length=255)
    trade_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    registration_status = serializers.CharField(max_length=32, required=False, allow_blank=True)
    is_headquarters = serializers.BooleanField(required=False)

    def create(self, validated_data: dict[str, object]) -> Company:
        tenant: Tenant = self.context["tenant"]
        identity = create_company(tenant=tenant, **validated_data)  # type: ignore[arg-type]
        return identity.company

    def update(self, instance: Company, validated_data: dict[str, object]) -> Company:
        del instance, validated_data
        raise NotImplementedError


class PersonReadSerializer(serializers.ModelSerializer[Person]):
    entity_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Person
        fields = (
            "entity_id",
            "full_name",
            "normalized_name",
            "cpf_masked",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PersonCreateSerializer(serializers.Serializer[Person]):
    full_name = serializers.CharField(max_length=255)
    external_key = serializers.CharField(max_length=255, required=False, allow_null=True)
    cpf = serializers.CharField(max_length=32, required=False, allow_null=True, write_only=True)

    def create(self, validated_data: dict[str, object]) -> Person:
        tenant: Tenant = self.context["tenant"]
        return create_person(
            tenant=tenant,
            hash_key=settings.DATA_HASH_KEY,
            **validated_data,  # type: ignore[arg-type]
        )

    def update(self, instance: Person, validated_data: dict[str, object]) -> Person:
        del instance, validated_data
        raise NotImplementedError


class RelationshipSerializer(serializers.ModelSerializer[Relationship]):
    class Meta:
        model = Relationship
        fields = (
            "id",
            "person",
            "company",
            "qualification",
            "observed_title",
            "normalized_title",
            "seniority",
            "buying_role",
            "buying_role_is_inferred",
            "started_on",
            "ended_on",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data: dict[str, object]) -> Relationship:
        tenant: Tenant = self.context["tenant"]
        return create_relationship(tenant=tenant, **validated_data)  # type: ignore[arg-type]


class ContactPointSerializer(serializers.ModelSerializer[ContactPoint]):
    class Meta:
        model = ContactPoint
        fields = (
            "id",
            "owner",
            "kind",
            "scope",
            "original_value",
            "normalized_value",
            "status",
            "capabilities",
            "last_observed_at",
            "stale_at",
            "expires_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "scope",
            "normalized_value",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data: dict[str, object]) -> ContactPoint:
        tenant: Tenant = self.context["tenant"]
        value = str(validated_data.pop("original_value"))
        return create_contact_point(
            tenant=tenant,
            value=value,
            **validated_data,  # type: ignore[arg-type]
        )


class SocialProfileSerializer(serializers.ModelSerializer[SocialProfile]):
    class Meta:
        model = SocialProfile
        fields = (
            "id",
            "owner",
            "network",
            "profile_url",
            "normalized_url",
            "handle",
            "status",
            "last_observed_at",
            "expires_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "normalized_url", "created_at", "updated_at")

    def create(self, validated_data: dict[str, object]) -> SocialProfile:
        tenant: Tenant = self.context["tenant"]
        return create_social_profile(tenant=tenant, **validated_data)  # type: ignore[arg-type]
