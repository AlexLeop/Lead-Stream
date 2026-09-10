from __future__ import annotations

import uuid
from typing import ClassVar

from django.db import models
from django.db.models import Q

from leadstream.evidence.models import RetentionPolicy
from leadstream.tenancy.models import TenantOwnedModel


class Suppression(TenantOwnedModel):
    class Scope(models.TextChoices):
        PERSON = "PERSON", "Pessoa"
        DOMAIN = "DOMAIN", "Domínio"
        EMAIL = "EMAIL", "E-mail"
        PHONE = "PHONE", "Telefone"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scope = models.CharField(max_length=16, choices=Scope.choices)
    value_digest = models.CharField(max_length=64)
    key_version = models.CharField(max_length=32)
    reason = models.CharField(max_length=255)
    effective_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "leadstream_suppression"
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("tenant", "scope", "value_digest", "key_version"),
                name="suppression_identity_uniq",
            ),
            models.CheckConstraint(
                condition=Q(expires_at__isnull=True) | Q(expires_at__gt=models.F("effective_at")),
                name="suppression_dates_valid",
            ),
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=("tenant", "scope", "value_digest", "effective_at"),
                name="suppression_lookup_idx",
            )
        ]

    def __str__(self) -> str:
        return f"{self.scope}:{self.value_digest[:10]}"


class RetentionRun(TenantOwnedModel):
    class Status(models.TextChoices):
        RUNNING = "RUNNING", "Em execução"
        COMPLETED = "COMPLETED", "Concluída"
        FAILED = "FAILED", "Falhou"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy = models.ForeignKey(RetentionPolicy, on_delete=models.PROTECT, related_name="runs")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RUNNING)
    stale_marked = models.PositiveIntegerField(default=0)
    expired_marked = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "leadstream_retention_run"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=("tenant", "started_at"), name="retention_run_time_idx")
        ]

    def __str__(self) -> str:
        return f"{self.policy.code}:{self.started_at.isoformat()}"


SUPPRESSION_SCOPE_CHOICES = Suppression.Scope.choices
