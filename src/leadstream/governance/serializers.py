from __future__ import annotations

from typing import Any

from rest_framework import serializers

from leadstream.evidence.models import RetentionPolicy
from leadstream.tenancy.models import Tenant

from .models import RetentionRun, Suppression
from .services import apply_retention, create_suppression


class SuppressionReadSerializer(serializers.ModelSerializer[Suppression]):
    class Meta:
        model = Suppression
        fields = (
            "id",
            "scope",
            "key_version",
            "reason",
            "effective_at",
            "expires_at",
            "created_at",
        )
        read_only_fields = fields


class SuppressionCreateSerializer(serializers.Serializer[Suppression]):
    scope = serializers.ChoiceField(choices=Suppression.Scope.choices)
    value = serializers.CharField(max_length=1024, write_only=True)
    reason = serializers.CharField(max_length=255)
    effective_at = serializers.DateTimeField(required=False, allow_null=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def create(self, validated_data: dict[str, Any]) -> Suppression:
        tenant: Tenant = self.context["tenant"]
        return create_suppression(tenant=tenant, **validated_data)

    def update(self, instance: Suppression, validated_data: dict[str, Any]) -> Suppression:
        del instance, validated_data
        raise NotImplementedError


class RetentionRunSerializer(serializers.ModelSerializer[RetentionRun]):
    class Meta:
        model = RetentionRun
        fields = (
            "id",
            "policy",
            "status",
            "stale_marked",
            "expired_marked",
            "started_at",
            "completed_at",
            "created_at",
        )
        read_only_fields = fields


class ApplyRetentionSerializer(serializers.Serializer[RetentionRun]):
    policy = serializers.PrimaryKeyRelatedField(queryset=RetentionPolicy.objects.all())

    def create(self, validated_data: dict[str, Any]) -> RetentionRun:
        tenant: Tenant = self.context["tenant"]
        return apply_retention(tenant=tenant, policy=validated_data["policy"])

    def update(self, instance: RetentionRun, validated_data: dict[str, Any]) -> RetentionRun:
        del instance, validated_data
        raise NotImplementedError
