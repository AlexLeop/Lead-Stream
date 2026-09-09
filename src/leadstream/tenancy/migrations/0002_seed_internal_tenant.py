from __future__ import annotations

import uuid

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps

INTERNAL_TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")


def create_internal_tenant(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    tenant_model = apps.get_model("tenancy", "Tenant")
    tenant_model.objects.using(schema_editor.connection.alias).get_or_create(
        slug="internal",
        defaults={
            "id": INTERNAL_TENANT_ID,
            "name": "Operação interna",
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("tenancy", "0001_initial")]

    operations = [migrations.RunPython(create_internal_tenant, migrations.RunPython.noop)]
