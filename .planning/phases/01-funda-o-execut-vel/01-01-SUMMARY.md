---
phase: 01-funda-o-execut-vel
plan: "01"
subsystem: api
tags: [django, drf, postgresql, tenancy, migrations, uv]
requires: []
provides:
  - "Projeto Django 5.2/DRF instalável com settings por ambiente"
  - "Tenant internal provisionado por migration idempotente"
  - "GET /api/v1/workspace/ lendo dados persistidos"
affects: [dados-confiaveis, lotes, provedores, exportacao, crm]
tech-stack:
  added: [Django 5.2, DRF 3.18, psycopg 3, uv]
  patterns: [settings fail-closed, tenant-owned models, data migration idempotente]
key-files:
  created:
    - pyproject.toml
    - src/config/settings/production.py
    - src/leadstream/tenancy/models.py
    - src/leadstream/tenancy/migrations/0002_seed_internal_tenant.py
    - src/leadstream/tenancy/views.py
    - tests/test_workspace_api.py
  modified: []
key-decisions:
  - "PostgreSQL permanece a fonte operacional de verdade e Appwrite não aparece no ORM."
  - "O tenant internal usa slug estável e UUID determinístico provisionado por data migration."
  - "O v1 não carrega autenticação de produto; o acesso será protegido no perímetro de implantação."
patterns-established:
  - "Configuração: defaults somente em development/test; production exige valores e rejeita banco não PostgreSQL."
  - "Tenancy: entidades futuras herdam TenantOwnedModel com vínculo obrigatório e PROTECT."
requirements-completed: [FND-02, FND-03, FND-04, FND-07]
duration: 14 min
completed: 2026-09-09
---

# Phase 1 Plan 1: Fundação Django, PostgreSQL e tenant interno Summary

**Django 5.2/DRF com configuração fail-closed, tenant interno migrado e primeira leitura real em `/api/v1/workspace/`.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-09-09T19:39:01-03:00
- **Completed:** 2026-09-09T19:52:14-03:00
- **Tasks:** 3
- **Files modified:** 27

## Accomplishments

- Projeto Python reproduzível com `pyproject.toml`, `uv.lock` e settings separados.
- Migration idempotente cria exatamente um tenant `internal` em banco novo.
- Endpoint DRF sem autenticação de produto lê o tenant persistido e responde em pt-BR.
- Ruff, mypy, migration drift check e testes passaram sem rede externa.

## Task Commits

1. **Task 1: Estruturar pacote Python e settings fail-closed** - `097d3ff`
2. **Task 2: Criar tenant interno por migration** - `5f790a7`
3. **Task 3: Expor a primeira rota real e testá-la** - `6c1c5ad`

## Files Created/Modified

- `pyproject.toml` e `uv.lock` - dependências e resolução reproduzível.
- `src/config/settings/` - ambientes development, test e production.
- `src/leadstream/tenancy/models.py` - tenant e base abstrata tenant-aware.
- `src/leadstream/tenancy/migrations/` - schema e provisionamento do workspace interno.
- `src/leadstream/tenancy/views.py` - rota de leitura real.
- `tests/test_workspace_api.py` - prova migration → ORM → API.

## Decisions Made

- SQLite ficou restrito ao settings de teste; development/production usam URL PostgreSQL.
- O UUID do tenant interno é determinístico para facilitar automação e referências futuras.
- O DRF usa usuário não autenticado nulo para não ativar implicitamente o sistema Django Auth.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Adicionado settings de teste isolado**
- **Found during:** Task 1
- **Issue:** validar o novo backend localmente sem o PostgreSQL da VPS exigia banco efêmero.
- **Fix:** criado `config.settings.test` com SQLite somente para testes.
- **Verification:** migrations e testes da API passaram.
- **Committed in:** `6c1c5ad`

**2. [Rule 3 - Blocking] Adicionadas tipagens compatíveis do DRF**
- **Found during:** Task 3
- **Issue:** mypy estrito não podia analisar DRF sem stubs e a primeira combinação possuía conflito de versões.
- **Fix:** alinhados `django-stubs` 6.1 e `djangorestframework-stubs` 3.18 no grupo dev e no lockfile.
- **Verification:** `mypy src` passou sem erros.
- **Committed in:** `6c1c5ad`

---

**Total deviations:** 2 auto-fixed (2 bloqueios de validação). **Impact:** somente infraestrutura de teste/tipagem; nenhuma ampliação do produto.

## Issues Encountered

- O `uv` tentou baixar Python 3.13 e encontrou uma instalação parcial local; o lock foi gerado explicitamente com o Python já instalado, preservando compatibilidade declarada com 3.13–3.14.
- O usuário não autenticado padrão do DRF importa Django Auth; foi desativado porque esta fase deliberadamente não instala autenticação.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Banco, tenant e rota versionada estão prontos para health, OpenAPI e observabilidade do plano 01-02.
- A validação contra o PostgreSQL real ocorrerá pela topologia de containers do plano 01-03.

## Self-Check: PASSED

- Arquivos-chave existem e os três commits atômicos estão no histórico.
- Ruff, mypy, migrations check e 2 testes passaram.
- A busca por marcadores das credenciais compartilhadas retornou zero ocorrências.

---
*Phase: 01-funda-o-execut-vel*
*Completed: 2026-09-09*
