from __future__ import annotations

from typing import Any

from celery import shared_task

from .services import ingest_batch, process_chunk


@shared_task(name="leadstream.batches.ingest", ignore_result=True)  # type: ignore[untyped-decorator]
def ingest_batch_task(batch_id: str) -> None:
    ingest_batch(batch_id)


@shared_task(  # type: ignore[untyped-decorator]
    bind=True,
    name="leadstream.batches.process_chunk",
    ignore_result=True,
    max_retries=5,
)
def process_chunk_task(self: Any, chunk_id: str) -> None:
    request = self.request
    result = process_chunk(chunk_id=chunk_id, worker_id=str(request.id))
    if result.retryable:
        raise self.retry(countdown=10)
