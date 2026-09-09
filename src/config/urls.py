from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("health/", include("leadstream.common.urls")),
    path("api/v1/", include("leadstream.tenancy.urls")),
]
