from collections.abc import Mapping

from rest_framework.exceptions import ValidationError


def reject_tenant_override(data: object) -> None:
    if isinstance(data, Mapping) and {"tenant", "tenant_id"}.intersection(data):
        raise ValidationError(
            {"tenant": "O tenant é aplicado automaticamente e não pode ser informado."}
        )
