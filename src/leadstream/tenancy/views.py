from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import WorkspaceSerializer
from .services import get_internal_tenant


class WorkspaceView(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        operation_id="consultar_workspace_interno",
        summary="Consultar workspace interno",
        description="Retorna o tenant interno aplicado automaticamente nesta primeira versão.",
        responses={200: WorkspaceSerializer},
        tags=["Operação interna"],
    )
    def get(self, request: Request) -> Response:
        del request
        tenant = get_internal_tenant()
        return Response(WorkspaceSerializer(tenant).data)
