from __future__ import annotations

from django.urls import path

from . import views

app_name = "health"

urlpatterns = [
    path("live", views.live, name="live"),
    path("ready", views.ready, name="ready"),
    path("dependencies", views.dependencies, name="dependencies"),
]
