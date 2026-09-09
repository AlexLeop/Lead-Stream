from __future__ import annotations

from django.urls import path

from .views import WorkspaceView

app_name = "tenancy"

urlpatterns = [
    path("workspace/", WorkspaceView.as_view(), name="workspace"),
]
