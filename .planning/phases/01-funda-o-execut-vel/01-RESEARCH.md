# Phase 1: Fundação Executável - Research

**Researched:** 2026-09-09
**Domain:** Django production foundation on a constrained VPS
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- API Django/ASGI, worker Celery, RabbitMQ, PostgreSQL and Redis are separate processes.
- PostgreSQL is the source of truth; Appwrite is only accessed through a service/storage adapter.
- Queue messages contain identifiers, not files or large provider payloads.
- Every business table is tenant-aware; `internal` is the automatic v1 tenant.
- There is no signup, login, user session or RBAC in v1; access is protected at the deployment perimeter.
- Liveness has no dependency checks; readiness requires PostgreSQL; Redis, broker and Appwrite are reported separately.
- Secrets live only in runtime environment configuration and are redacted from logs.
- Database migrations run as one explicit release command before rollout.
- Containers run as a non-root user and dependencies are reproducible.

### the agent's Discretion
- Internal package names and exact settings split.
- Logging implementation and structured error envelope.
- Conservative initial timeout and pool values, as long as they remain configurable.

### Deferred Ideas (OUT OF SCOPE)
- Canonical company/person/contact/evidence models beyond the tenant skeleton.
- Batch processing, provider integrations, exports, CRM and user authentication.
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Versioned REST API | API/Backend | Gateway | DRF owns contracts; gateway owns exposure policy |
| Tenant bootstrap/read | Database/Storage | API/Backend | PostgreSQL persists identity; API exposes a minimal read |
| Liveness/readiness | API/Backend | Database/Storage | Process status is local; readiness performs bounded DB probe |
| Background execution | API/Backend | RabbitMQ | Celery workers consume commands from durable queues |
| Appwrite diagnostics | API/Backend | External service | Adapter isolates SDK and optional availability |
| Runtime configuration | Deployment | API/Backend | EasyPanel provides secrets; application validates them |
</architectural_responsibility_map>

<research_summary>
## Summary

The smallest meaningful walking skeleton is: migrations create the `internal` tenant, `/api/v1/workspace/` reads it from PostgreSQL, and Swagger can invoke that endpoint. This proves routing, serialization, a real database write and read, and an interactive API surface without violating the backend-only scope.

Django settings should be split into base/development/production modules with a typed helper for environment parsing. A custom system check validates production-only configuration. Health endpoints must be deliberately asymmetric: liveness always remains cheap; readiness uses `SELECT 1` with a bounded failure response; optional dependency probes never expose connection details.

RabbitMQ should be the Celery broker and Redis should remain cache/coordination infrastructure. Business progress is not stored in Celery's result backend. Docker Compose exists for reproducible local execution, while EasyPanel receives service-specific commands and an explicit migration release step.

**Primary recommendation:** build and test the tenant/workspace read path first, then add optional dependency diagnostics and production packaging around that proven slice.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 5.2.x LTS | ORM, migrations, settings and admin foundation | Stable LTS with Python 3.13 support |
| djangorestframework | 3.18.x | REST contracts | Mature serializers, views and exception handling |
| psycopg[binary,pool] | 3.x | PostgreSQL driver and pooling | Current PostgreSQL adapter for Python |
| celery | 5.6.x | Background workers | Mature task routing and retries |
| redis | 6+ Python client | Cache and coordination | Atomic primitives and Django cache support |
| appwrite | current compatible major | Optional service adapter | Official server SDK |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| drf-spectacular | 0.28+ | OpenAPI/Swagger | All API endpoints |
| django-environ | 0.12+ | DATABASE_URL and env parsing | Settings only |
| structlog | 25.x | JSON logs and context | Request/worker correlation |
| httpx | 0.28+ | Bounded external probes | Provider/Appwrite adapters |
| uvicorn | 0.35+ | ASGI server | Production API container |
| pytest + pytest-django | current | Test suite | Unit and integration tests |
| ruff | current | Lint/format | CI quality gate |
| mypy + django-stubs | current | Static typing | Service boundaries and settings |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| RabbitMQ broker | Redis broker | Fewer services, but conflates durable transport and cache |
| django-environ | pydantic-settings | Stronger typed object model, more glue with Django settings |
| Custom health views | django-health-check | Faster setup, but less precise public response and dependency policy |
| Uvicorn | Gunicorn/WSGI | Familiar sync deployment, less aligned with future async-facing API |

**Installation:** dependencies belong in `pyproject.toml`; `uv sync --frozen` installs the lockfile when available.
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### System Architecture Diagram

```text
Swagger/operator → GET /api/v1/workspace → DRF view → Tenant ORM query → PostgreSQL
       │
       ├── GET /health/live ───────────────→ process-only response
       ├── GET /health/ready ──────────────→ bounded SELECT 1
       └── GET /health/dependencies ───────→ DB + Redis + broker + Appwrite probes

API command → RabbitMQ → Celery worker (smoke task only in Phase 1)
```

### Recommended Project Structure
```text
src/
├── manage.py
├── config/
│   ├── settings/{base,development,production}.py
│   ├── urls.py
│   ├── asgi.py
│   └── celery.py
└── leadstream/
    ├── common/          # health, errors, logging, env helpers
    ├── tenancy/         # Tenant and internal workspace endpoint
    └── integrations/    # Appwrite port and adapter
tests/
```

### Pattern 1: Separate liveness and readiness
**What:** liveness returns a static success from the process; readiness performs only critical dependency checks.
**When to use:** container orchestration and rolling deployments.

### Pattern 2: Data migration for the default tenant
**What:** a migration creates `slug=internal` using `get_or_create`; the API reads it through a service.
**When to use:** bootstrap data required in every environment.

### Pattern 3: Optional adapter result
**What:** Appwrite probe returns `configured`, `status` and bounded latency without raising into global readiness.
**When to use:** non-critical external services.

### Anti-Patterns to Avoid
- Running `migrate` concurrently in API and every worker container.
- Treating a successful TCP connection as full application readiness.
- Returning exception text or connection strings in health responses.
- Adding business models merely to make a walking-skeleton database write.
- Using Celery result state as the durable job state.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| URL/database parsing | Custom string splitting | django-environ + psycopg | Escaping and query options are subtle |
| OpenAPI schema | Manual JSON document | drf-spectacular | Keeps schema aligned with code |
| Request IDs/log context | Ad-hoc print statements | structlog middleware/contextvars | Prevents secret leakage and lost correlation |
| Retry queue | Database polling loop | Celery + RabbitMQ | Delivery semantics and worker control are solved |
| Password/secret fallback | Generated production default | Mandatory environment value | Silent defaults create insecure deployments |

**Key insight:** the foundation should prove domain wiring and operational failure behavior, not invent infrastructure primitives.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Production starts with development defaults
**What goes wrong:** wildcard hosts, debug output or a known secret key reaches the internet.
**Why it happens:** one settings file silently fills missing values.
**How to avoid:** separate production settings and run `manage.py check --deploy` in the gate.
**Warning signs:** `DEBUG=True` or fallback `SECRET_KEY` outside tests.

### Pitfall 2: Optional Appwrite outage marks the API dead
**What goes wrong:** orchestration restarts a healthy API because an external service is unavailable.
**Why it happens:** all dependencies are bundled into one readiness boolean.
**How to avoid:** make PostgreSQL critical and report optional dependency status separately.
**Warning signs:** `/health/ready` performs internet calls.

### Pitfall 3: Credentials leak through diagnostics
**What goes wrong:** exception strings include URLs, headers or tokens.
**Why it happens:** raw exceptions are serialized or logged.
**How to avoid:** map failures to stable codes and apply centralized redaction.
**Warning signs:** health response changes with driver exception text.

### Pitfall 4: Local success cannot be deployed
**What goes wrong:** code expects localhost service names or Windows behavior.
**Why it happens:** deployment commands and environment contract are deferred.
**How to avoid:** containerize during the skeleton and document EasyPanel commands/resources now.
**Warning signs:** only `runserver` is documented.
</common_pitfalls>

<code_examples>
## Code Examples

### PostgreSQL readiness probe
```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    cursor.fetchone()
```

### Appwrite server client
```python
from appwrite.client import Client

client = Client().set_endpoint(endpoint).set_project(project_id).set_key(api_key)
```

### Celery configuration boundary
```python
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```
</code_examples>

<sota_updates>
## State of the Art (2026)

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| Non-LTS latest Django by default | Django 5.2 LTS for long-lived service | Longer security support and lower upgrade churn |
| WSGI-only baseline | ASGI entry point with sync-safe Django code | Enables future async endpoints without changing deployment shape |
| Redis for every queue concern | RabbitMQ broker + Redis coordination | Clearer durability and cache responsibilities |
| Appwrite TablesDB as generic database | Native PostgreSQL for Django ORM | Preserves relational migrations and direct SQL |

**Deprecated/outdated:** Django `runserver` is development-only and must never be the production command.
</sota_updates>

<open_questions>
## Open Questions

1. **Which public URL and gateway policy will expose the API?**
   - What we know: EasyPanel hosts the service and v1 has no product authentication.
   - What's unclear: final domain and whether Cloudflare Access or an EasyPanel-only network will be used.
   - Recommendation: keep these deployment variables documented but optional until first deploy.

2. **Is Appwrite Storage backed by external object storage?**
   - What we know: self-hosted Appwrite exists.
   - What's unclear: its current storage adapter and retention capacity.
   - Recommendation: Phase 1 verifies service access only; Phase 5 validates capacity before storing large files.
</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)
- https://docs.djangoproject.com/en/5.2/ — settings, migrations, ASGI and deployment checks.
- https://www.django-rest-framework.org/ — API conventions and schema integration.
- https://docs.celeryq.dev/en/stable/ — Celery 5.6 tasks, RabbitMQ and Redis.
- https://www.postgresql.org/docs/current/ — transactions and connection behavior.
- https://appwrite.io/docs/quick-starts/python — official server SDK configuration.
- https://appwrite.io/docs/references/cloud/server-python/health — authenticated health probes.
</sources>

<metadata>
## Metadata

**Research scope:** Django foundation, PostgreSQL, tenant bootstrap, health semantics, Appwrite adapter, containers and quality gates.

**Confidence breakdown:**
- Standard stack: HIGH — official current documentation.
- Architecture: HIGH — established Django/Celery deployment patterns.
- Pitfalls: HIGH — directly testable failure modes.
- Code examples: HIGH — official framework patterns reduced to minimal examples.

**Research date:** 2026-09-09
**Valid until:** 2026-10-09
</metadata>

---

*Phase: 01-funda-o-execut-vel*
*Research completed: 2026-09-09*
*Ready for planning: yes*
