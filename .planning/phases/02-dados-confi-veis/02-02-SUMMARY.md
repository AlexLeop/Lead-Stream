---
phase: 02-dados-confi-veis
plan: "02"
subsystem: database
tags: [django, postgresql, provenance, append-only, canonicalization]
requires:
  - phase: 02-dados-confi-veis
    provides: Entity registry e grafo canônico
provides:
  - fontes, registros, finalidade, retenção, evidências e observações
  - trigger PostgreSQL append-only
  - conflitos e decisões canônicas versionadas/determinísticas
affects: [governance, providers, batches, exports]
tech-stack:
  added: []
  patterns: [append-only audit, deterministic ranking, versioned decisions]
key-files:
  created:
    - src/leadstream/evidence/models.py
    - src/leadstream/evidence/services.py
    - src/leadstream/evidence/migrations/0002_observation_append_only.py
  modified:
    - src/config/settings/base.py
key-decisions:
  - "Estado da observação é preservado pela decisão; inferência nunca vira confirmação."
  - "Imutabilidade é aplicada pelo ORM e por trigger PostgreSQL."
  - "Canonização ordena elegibilidade, estado, fonte, confiança, atualidade e UUID."
patterns-established:
  - "Correção cria Observation supersedente; nunca altera histórico."
  - "Recanonização cria versão nova sob lock da Entity."
requirements-completed: [DATA-04, DATA-05, DATA-06, COMP-01]
duration: 31min
completed: 2026-09-10
---

# Phase 2 Plan 02: Evidência e Canonização Summary

**Proveniência append-only com finalidade, conflitos auditáveis e decisões canônicas versionadas sem elevação de evidência**

## Performance

- **Duration:** 31 min
- **Started:** 2026-09-10T01:40:00-03:00
- **Completed:** 2026-09-10T02:11:00-03:00
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Modelos de origem, finalidade, retenção, evidência, observação, conflito e decisão.
- Proteção append-only tanto na aplicação quanto no PostgreSQL.
- Ranking determinístico que exclui estados inelegíveis e expirados.
- Recanonização preserva todas as decisões anteriores.

## Task Commits

1. **Modelar proveniência e decisões** - `79e0a66`
2. **Proteger observações append-only** - `11137f0`
3. **Canonizar observações deterministicamente** - `77644a8`

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- O teste do trigger é ignorado no SQLite local e obrigatório quando a CI injeta PostgreSQL.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

O domínio já oferece um ponto único para a supressão impedir canonização e para a API expor
proveniência, conflitos e versões de política.

## Self-Check: PASSED

- 6 testes de evidência/canonização passaram localmente e 1 gate PostgreSQL está preparado para CI.
- Ruff, mypy e migration drift passaram.
- DATA-04, DATA-05, DATA-06 e COMP-01 estão cobertos.

---
*Phase: 02-dados-confi-veis*
*Completed: 2026-09-10*
