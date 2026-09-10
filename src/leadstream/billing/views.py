from __future__ import annotations

from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from leadstream.batches.models import Batch
from leadstream.common.api import reject_tenant_override
from leadstream.tenancy.services import get_internal_tenant

from .models import PriceBook
from .serializers import FinancialSummarySerializer, PriceBookInputSerializer, PriceBookSerializer
from .services import create_price_book, ensure_default_price_book, financial_summary


def _domain_error(exc: DjangoValidationError) -> ValidationError:
    if hasattr(exc, "message_dict"):
        return ValidationError(exc.message_dict)
    return ValidationError({"erro": exc.messages})


class PriceBookCollectionView(APIView):
    @extend_schema(responses=PriceBookSerializer(many=True), tags=["Financeiro — preços"])
    def get(self, request: Request) -> Response:
        del request
        tenant = get_internal_tenant()
        ensure_default_price_book(tenant)
        queryset = PriceBook.objects.filter(tenant=tenant).prefetch_related("rules")
        return Response(PriceBookSerializer(queryset, many=True).data)

    @extend_schema(
        request=PriceBookInputSerializer,
        responses={201: PriceBookSerializer},
        tags=["Financeiro — preços"],
    )
    def post(self, request: Request) -> Response:
        reject_tenant_override(request.data)
        serializer = PriceBookInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            price_book = create_price_book(
                tenant=get_internal_tenant(), **serializer.validated_data
            )
        except DjangoValidationError as exc:
            raise _domain_error(exc) from exc
        price_book = PriceBook.objects.prefetch_related("rules").get(pk=price_book.pk)
        return Response(PriceBookSerializer(price_book).data, status=status.HTTP_201_CREATED)


class BatchFinancialSummaryView(APIView):
    @extend_schema(responses=FinancialSummarySerializer, tags=["Financeiro — lotes"])
    def get(self, request: Request, batch_id: UUID) -> Response:
        del request
        tenant = get_internal_tenant()
        try:
            batch = Batch.objects.get(pk=batch_id, tenant=tenant)
        except Batch.DoesNotExist as exc:
            raise Http404("Lote não encontrado.") from exc
        return Response(financial_summary(tenant=tenant, batch=batch))
