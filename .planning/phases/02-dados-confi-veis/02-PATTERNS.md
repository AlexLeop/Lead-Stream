# Phase 2: Existing Code Patterns

## Reusable Assets

| New concern | Existing analog | Reuse |
|-------------|-----------------|-------|
| Tenant ownership | `src/leadstream/tenancy/models.py` | inherit or reference `TenantOwnedModel`; keep UUID tenant |
| Tenant resolution | `src/leadstream/tenancy/services.py` | call `get_internal_tenant()` at API boundary |
| DRF contract | `tenancy/serializers.py`, `tenancy/views.py`, `tenancy/urls.py` | typed serializers, `extend_schema`, pt-BR tags |
| App registration | `tenancy/apps.py`, `settings/base.py` | one Django app config and explicit `INSTALLED_APPS` entry |
| Migrations | `tenancy/migrations/0001`, `0002` | schema migration then explicit data/SQL migration |
| Tests | `tests/conftest.py`, `test_workspace_api.py` | `APIClient`, pytest-django, no network |
| Secret hygiene | `common/env.py`, `common/logging.py` | read environment without logging raw values |

## Established Patterns

- Python package under `src/leadstream/<bounded_context>`.
- UUID primary keys for tenant/root identities; explicit `db_table` names.
- Services own operational decisions; views remain thin.
- Portuguese response fields and stable OpenAPI operation IDs.
- Migrations are committed and checked with `makemigrations --check --dry-run`.
- PostgreSQL is mandatory in production; SQLite exists only in test settings.
- No product authentication; perimeter protection is a deployment invariant.

## Integration Map

```text
config/settings/base.py
  ├── leadstream.entities.apps.EntitiesConfig
  ├── leadstream.evidence.apps.EvidenceConfig
  └── leadstream.governance.apps.GovernanceConfig

config/urls.py
  └── /api/v1/dados/ → entities/evidence/governance API router

tenancy.get_internal_tenant()
  └── all write/query services → mandatory tenant scope

Entity
  ├── Company / Establishment / Person
  ├── ContactPoint / SocialProfile
  └── Observation → Evidence / SourceRecord → CanonicalDecision / Conflict
```

## New Files and Closest Analogs

| Planned file | Closest analog | Notes |
|--------------|----------------|-------|
| `entities/models.py` | `tenancy/models.py` | explicit constraints and tenant roots |
| `entities/services.py` | `tenancy/services.py` | normalization + transactional creation |
| `entities/serializers.py` | `tenancy/serializers.py` | hide tenant, preserve pt-BR contract |
| `entities/views.py` | `tenancy/views.py` | tenant-scoped querysets only |
| `evidence/services.py` | no direct analog | pure ranking plus transactional append-only decisions |
| `governance/services.py` | `tenancy/services.py` | HMAC/suppression and retention policies |
| `*/migrations/*.py` | tenancy migrations | Django schema plus PostgreSQL-specific guarded SQL |

## Corrections Applied to Legacy Patterns

- Do not copy the old TypeScript/SQLite monolith or inline migration pattern.
- Do not use generic foreign keys for observation ownership.
- Do not serialize source payloads or personal identifiers into logs.
- Do not expose unrestricted `.objects.all()` from API views.
- Do not let models silently elevate evidence status.

---

*Mapped: 2026-09-10*
