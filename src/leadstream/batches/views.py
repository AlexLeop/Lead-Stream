from __future__ import annotations

from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from leadstream.common.api import reject_tenant_override
from leadstream.common.pagination import StandardPagination
from leadstream.tenancy.services import get_internal_tenant

from .models import Batch, BatchChunk, BatchItem
from .serializers import (
    BatchChunkSerializer,
    BatchItemSerializer,
    BatchSerializer,
    BatchUploadSerializer,
)
from .services import cancel_batch, create_csv_batch, pause_batch, resume_batch


def _get_batch(batch_id: UUID) -> Batch:
    try:
        return Batch.objects.get(pk=batch_id, tenant=get_internal_tenant())
    except Batch.DoesNotExist as exc:
        raise Http404("Lote não encontrado.") from exc


def _domain_error(exc: DjangoValidationError) -> ValidationError:
    if hasattr(exc, "message_dict"):
        return ValidationError(exc.message_dict)
    return ValidationError({"erro": exc.messages})


class BatchCollectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(responses=BatchSerializer(many=True), tags=["Lotes"])
    def get(self, request: Request) -> Response:
        queryset = Batch.objects.filter(tenant=get_internal_tenant())
        requested_status = request.query_params.get("status")
        if requested_status:
            queryset = queryset.filter(status=requested_status)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(BatchSerializer(page, many=True).data)

    @extend_schema(
        request=BatchUploadSerializer,
        responses={200: BatchSerializer, 202: BatchSerializer},
        parameters=[OpenApiParameter(
            "Idempotency-Key", str, location=OpenApiParameter.HEADER, required=True,
            description="Chave estável da operação de upload.",
        )],
        tags=["Lotes"],
    )
    def post(self, request: Request) -> Response:
        reject_tenant_override(request.data)
        serializer = BatchUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = create_csv_batch(
                tenant=get_internal_tenant(), name=data.get("name", ""),
                upload=data["arquivo"], idempotency_key=request.headers.get("Idempotency-Key", ""),
                chunk_size=data["chunk_size"],
            )
        except DjangoValidationError as exc:
            raise _domain_error(exc) from exc
        response_status = status.HTTP_202_ACCEPTED if result.created else status.HTTP_200_OK
        return Response(BatchSerializer(result.batch).data, status=response_status)


class BatchDetailView(APIView):
    @extend_schema(responses=BatchSerializer, tags=["Lotes"])
    def get(self, request: Request, batch_id: UUID) -> Response:
        del request
        return Response(BatchSerializer(_get_batch(batch_id)).data)


class BatchItemsView(APIView):
    @extend_schema(responses=BatchItemSerializer(many=True), tags=["Lotes"])
    def get(self, request: Request, batch_id: UUID) -> Response:
        batch = _get_batch(batch_id)
        queryset = BatchItem.objects.filter(batch=batch, tenant=batch.tenant).order_by("row_number")
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(BatchItemSerializer(page, many=True).data)


class BatchChunksView(APIView):
    @extend_schema(responses=BatchChunkSerializer(many=True), tags=["Lotes"])
    def get(self, request: Request, batch_id: UUID) -> Response:
        batch = _get_batch(batch_id)
        queryset = (BatchChunk.objects.filter(batch=batch, tenant=batch.tenant)
                    .prefetch_related("attempts").order_by("sequence"))
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(BatchChunkSerializer(page, many=True).data)


class PauseBatchView(APIView):
    @extend_schema(request=None, responses=BatchSerializer, tags=["Lotes — comandos"])
    def post(self, request: Request, batch_id: UUID) -> Response:
        del request
        try:
            batch = pause_batch(tenant=get_internal_tenant(), batch_id=batch_id)
        except DjangoValidationError as exc:
            raise _domain_error(exc) from exc
        return Response(BatchSerializer(batch).data)


class ResumeBatchView(APIView):
    @extend_schema(request=None, responses=BatchSerializer, tags=["Lotes — comandos"])
    def post(self, request: Request, batch_id: UUID) -> Response:
        del request
        try:
            batch = resume_batch(tenant=get_internal_tenant(), batch_id=batch_id)
        except DjangoValidationError as exc:
            raise _domain_error(exc) from exc
        return Response(BatchSerializer(batch).data)


class CancelBatchView(APIView):
    @extend_schema(request=None, responses=BatchSerializer, tags=["Lotes — comandos"])
    def post(self, request: Request, batch_id: UUID) -> Response:
        del request
        batch = cancel_batch(tenant=get_internal_tenant(), batch_id=batch_id)
        return Response(BatchSerializer(batch).data)
