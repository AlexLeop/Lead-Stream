from __future__ import annotations

from rest_framework import serializers

from .models import Tenant


class WorkspaceSerializer(serializers.ModelSerializer[Tenant]):
    nome = serializers.CharField(source="name", read_only=True)
    ativo = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = Tenant
        fields = ("id", "slug", "nome", "ativo")
        read_only_fields = fields
