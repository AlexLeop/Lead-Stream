from __future__ import annotations

from uuid import UUID

from celery import shared_task


@shared_task(name="leadstream.smoke", ignore_result=True)  # type: ignore[untyped-decorator]
def smoke_task(reference_id: str) -> dict[str, str]:
    if not isinstance(reference_id, str):
        raise TypeError("A tarefa aceita somente um identificador UUID em texto.")
    try:
        normalized_id = str(UUID(reference_id))
    except ValueError as exc:
        raise ValueError("O identificador da tarefa deve ser um UUID válido.") from exc
    return {"reference_id": normalized_id, "status": "ok"}
