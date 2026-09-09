---
phase: 01-funda-o-execut-vel
plan: "02"
subsystem: observability
tags: [health, appwrite, openapi, structlog, request-id, redaction]
requires:
  - phase: 01-01
    provides: "Django, tenant internal e rota real do workspace"
provides:
  - "Liveness, readiness e diagnósticos opcionais com contratos separados"
  - "Adaptador Appwrite com timeout, TLS e falha sanitizada"
  - "OpenAPI/Swagger versionado e logs JSON com request ID e redação"
affects: [deploy, lotes, provedores, operacao]
tech-stack:
  added: [drf-spectacular, structlog, httpx]
  patterns: [optional dependency diagnostics, adapter boundary, recursive log redaction]
key-files:
  created:
    - src/leadstream/common/health.py
    - src/leadstream/integrations/appwrite.py
    - src/leadstream/common/request_context.py
    - src/leadstream/common/logging.py
    - tests/test_logging.py
  modified:
    - src/config/urls.py
    - src/config/settings/base.py
    - src/leadstream/common/views.py
key-decisions:
  - "Readiness depende somente de PostgreSQL e migrations; serviços opcionais ficam no diagnóstico separado."
  - "O SDK Appwrite 24 não expõe mais o serviço Health; o adapter consulta o endpoint oficial com httpx e mantém o SDK para Storage futuro."
  - "Request ID recebido é aceito somente em formato limitado; valores inválidos são substituídos."
patterns-established:
  - "Health público devolve apenas status estável, nunca detalhes de conexão ou exceções."
  - "Logs estruturados passam por redação recursiva de segredos e contatos."
requirements-completed: [FND-01, FND-05, FND-07, OPS-01]
duration: 9 min
completed: 2026-09-09
---

# Phase 1 Plan 2: Saúde, Appwrite, OpenAPI e observabilidade Summary

**Probes operacionais separados, Appwrite opcional e contrato OpenAPI navegável com request IDs e logs JSON redigidos.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-09T19:58:35-03:00
- **Completed:** 2026-09-09T20:07:08-03:00
- **Tasks:** 3
- **Files modified:** 12

## Accomplishments

- `/health/live` não faz I/O; `/health/ready` verifica PostgreSQL e migration essencial.
- Redis, RabbitMQ e Appwrite possuem estados separados sem expor topologia ou erro bruto.
- Swagger/ReDoc documenta workspace e health sob contrato OpenAPI v1.
- Middleware cria `X-Request-ID`; logs correlacionados removem segredos, e-mails e telefones.

## Task Commits

1. **Task 1: Implementar semântica de health e diagnósticos** - `30ae82d`
2. **Task 2: Criar porta Appwrite e diagnóstico desacoplado** - `43b432f`
3. **Task 3: Publicar OpenAPI e logging correlacionado** - `a956276`

## Files Created/Modified

- `src/leadstream/common/health.py` - probes críticos e opcionais.
- `src/leadstream/integrations/appwrite.py` - porta HTTP isolada com chave ocultada do repr.
- `src/leadstream/common/request_context.py` - contexto de request/tenant/lote/chunk/provedor.
- `src/leadstream/common/logging.py` - configuração structlog e redactor recursivo.
- `src/config/urls.py` - schema, Swagger e ReDoc.
- `tests/test_health.py`, `tests/test_appwrite_adapter.py`, `tests/test_logging.py` - falhas e não vazamento.

## Decisions Made

- Appwrite não bloqueia readiness porque não é fonte operacional de verdade.
- O diagnóstico Appwrite usa o endpoint `/health` diretamente com `httpx`: o SDK oficial 24 continua instalado para Storage futuro, mas não possui mais a classe `Health` pesquisada no plano.
- A configuração de logging é central e aplicada pelo Django, evitando `print` e payloads brutos.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Health do Appwrite implementado por endpoint oficial**
- **Found during:** Task 2
- **Issue:** o Appwrite Python SDK 24.0.0 não inclui o antigo serviço `Health`.
- **Fix:** criada porta tipada baseada em `httpx`, com o mesmo endpoint oficial, timeout e TLS obrigatório.
- **Verification:** fixtures de sucesso, ausência, 401 e timeout passaram sem rede.
- **Committed in:** `43b432f`

---

**Total deviations:** 1 auto-fixed (1 bloqueio de compatibilidade). **Impact:** preserva o contrato e reduz acoplamento ao SDK.

## Issues Encountered

None.

## User Setup Required

**A integração real requer rotação/configuração externa.** Consulte `01-USER-SETUP.md` para a nova chave mínima e as variáveis do EasyPanel.

## Next Phase Readiness

- Probes e logs estão prontos para serem usados pela imagem e pelo EasyPanel no plano 01-03.
- A conexão real do Appwrite permanece pendente até a chave compartilhada ser rotacionada e inserida no cofre de ambiente.

## Self-Check: PASSED

- 14 testes passaram; nenhum acessou rede externa.
- Ruff, mypy, migration check e validação OpenAPI passaram.
- Marcadores das credenciais reais não aparecem no repositório.

---
*Phase: 01-funda-o-execut-vel*
*Completed: 2026-09-09*
