from __future__ import annotations

from typing import Any

from rest_framework import serializers

from leadstream.tenancy.models import Tenant

from .models import (
    CanonicalDecision,
    Conflict,
    Evidence,
    Observation,
    ProcessingPurpose,
    RetentionPolicy,
    Source,
    SourceRecord,
)
from .services import CanonicalPolicy, append_observation, canonicalize, open_conflict


class PurposeSerializer(serializers.ModelSerializer[ProcessingPurpose]):
    class Meta:
        model = ProcessingPurpose
        fields = ("id", "code", "name", "description", "operational_basis", "is_active")
        read_only_fields = ("id",)

    def create(self, validated_data: dict[str, Any]) -> ProcessingPurpose:
        instance = ProcessingPurpose(tenant=self.context["tenant"], **validated_data)
        instance.full_clean()
        instance.save()
        return instance


class RetentionPolicySerializer(serializers.ModelSerializer[RetentionPolicy]):
    class Meta:
        model = RetentionPolicy
        fields = (
            "id",
            "code",
            "name",
            "stale_after_days",
            "retention_days",
            "is_active",
        )
        read_only_fields = ("id",)

    def create(self, validated_data: dict[str, Any]) -> RetentionPolicy:
        instance = RetentionPolicy(tenant=self.context["tenant"], **validated_data)
        instance.full_clean()
        instance.save()
        return instance


class SourceSerializer(serializers.ModelSerializer[Source]):
    class Meta:
        model = Source
        fields = (
            "id",
            "slug",
            "name",
            "category",
            "priority",
            "terms_url",
            "is_active",
        )
        read_only_fields = ("id",)

    def create(self, validated_data: dict[str, Any]) -> Source:
        instance = Source(tenant=self.context["tenant"], **validated_data)
        instance.full_clean()
        instance.save()
        return instance


class SourceRecordSerializer(serializers.ModelSerializer[SourceRecord]):
    class Meta:
        model = SourceRecord
        fields = (
            "id",
            "source",
            "purpose",
            "retention_policy",
            "external_id",
            "source_url",
            "captured_at",
            "payload_hash",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def create(self, validated_data: dict[str, Any]) -> SourceRecord:
        instance = SourceRecord(tenant=self.context["tenant"], **validated_data)
        instance.full_clean()
        instance.save()
        return instance


class EvidenceSerializer(serializers.ModelSerializer[Evidence]):
    class Meta:
        model = Evidence
        fields = (
            "id",
            "source_record",
            "url",
            "external_id",
            "captured_at",
            "observed_at",
            "method",
            "excerpt",
            "excerpt_hash",
            "content_hash",
            "metadata",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def create(self, validated_data: dict[str, Any]) -> Evidence:
        instance = Evidence(tenant=self.context["tenant"], **validated_data)
        instance.full_clean()
        instance.save()
        return instance


class ObservationSerializer(serializers.ModelSerializer[Observation]):
    evidence_ids = serializers.PrimaryKeyRelatedField(
        queryset=Evidence.objects.all(),
        many=True,
        required=False,
        source="evidence",
    )
    source_name = serializers.CharField(source="source_record.source.name", read_only=True)
    purpose_code = serializers.CharField(source="source_record.purpose.code", read_only=True)

    class Meta:
        model = Observation
        fields = (
            "id",
            "target",
            "source_record",
            "source_name",
            "purpose_code",
            "field_path",
            "value",
            "value_fingerprint",
            "status",
            "confidence",
            "method",
            "observed_at",
            "captured_at",
            "expires_at",
            "supersedes",
            "evidence_ids",
            "created_at",
        )
        read_only_fields = ("id", "value_fingerprint", "created_at")

    def create(self, validated_data: dict[str, Any]) -> Observation:
        evidence_items = validated_data.pop("evidence", [])
        tenant: Tenant = self.context["tenant"]
        return append_observation(
            tenant=tenant,
            evidence_items=evidence_items,
            **validated_data,
        )


class CanonicalDecisionSerializer(serializers.ModelSerializer[CanonicalDecision]):
    selected_value = serializers.JSONField(source="selected_observation.value", read_only=True)
    source_name = serializers.CharField(
        source="selected_observation.source_record.source.name", read_only=True
    )

    class Meta:
        model = CanonicalDecision
        fields = (
            "id",
            "target",
            "field_path",
            "version",
            "policy_version",
            "selected_observation",
            "selected_value",
            "source_name",
            "decision_status",
            "reason",
            "decided_at",
            "created_at",
        )
        read_only_fields = fields


class CanonicalizeInputSerializer(serializers.Serializer[CanonicalDecision]):
    target = serializers.UUIDField()
    field_path = serializers.CharField(max_length=255)
    policy_version = serializers.CharField(max_length=64, default="canonical-v1")

    def create(self, validated_data: dict[str, Any]) -> CanonicalDecision:
        tenant: Tenant = self.context["tenant"]
        target = validated_data["target"]
        from leadstream.entities.models import Entity

        entity = Entity.objects.get(pk=target, tenant=tenant)
        return canonicalize(
            tenant=tenant,
            target=entity,
            field_path=validated_data["field_path"],
            policy=CanonicalPolicy(version=validated_data["policy_version"]),
        )

    def update(
        self, instance: CanonicalDecision, validated_data: dict[str, Any]
    ) -> CanonicalDecision:
        del instance, validated_data
        raise NotImplementedError


class ConflictSerializer(serializers.ModelSerializer[Conflict]):
    observation_ids = serializers.PrimaryKeyRelatedField(
        queryset=Observation.objects.all(),
        many=True,
        source="observations",
    )

    class Meta:
        model = Conflict
        fields = (
            "id",
            "target",
            "field_path",
            "status",
            "reason",
            "observation_ids",
            "resolved_at",
            "created_at",
        )
        read_only_fields = ("id", "status", "resolved_at", "created_at")

    def create(self, validated_data: dict[str, Any]) -> Conflict:
        observations = validated_data.pop("observations")
        tenant: Tenant = self.context["tenant"]
        return open_conflict(tenant=tenant, observations=observations, **validated_data)
