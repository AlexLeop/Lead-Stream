---
phase: 02-dados-confi-veis
plan: "01"
subsystem: database
tags: [django, postgresql, cnpj, tenant, entities]
requires:
  - phase: 01-funda-o-execut-vel
    provides: PostgreSQL, tenant interno e pipeline de qualidade
provides:
  - grafo canônico empresa-estabelecimento-pessoa-vínculo
  - contatos e perfis sociais com proprietário explícito
  - normalizadores Brasil-first e serviços transacionais tenant-safe
affects: [evidence, batches, providers, exports, crm]
tech-stack:
  added: []
  patterns: [entity registry, tenant-scoped services, original-plus-normalized]
key-files:
  created:
    - src/leadstream/entities/models.py
    - src/leadstream/entities/services.py
    - src/leadstream/entities/normalization.py
  modified:
    - src/config/settings/test.py
    - .github/workflows/ci.yml
key-decisions:
  - "Empresa usa raiz CNPJ e estabelecimento usa CNPJ completo por Entity tenant-aware."
  - "Pessoa não possui campo de CPF integral; correlação opcional usa máscara e HMAC."
  - "WhatsApp permanece canal distinto e não é confirmado por formato de celular."
patterns-established:
  - "Serviços recebem Tenant e rejeitam toda referência cruzada antes de persistir."
  - "CI usa TEST_DATABASE_URL para executar a suíte contra PostgreSQL real."
requirements-completed: [DATA-01, DATA-02, DATA-03]
duration: 24min
completed: 2026-09-10
---

# Phase 2 Plan 01: Identidade Canônica Summary

**Grafo relacional tenant-aware com CNPJ validado, decisores, vínculos, contatos e perfis sem CPF integral ou confirmação sintética de WhatsApp**

## Performance

- **Duration:** 24 min
- **Started:** 2026-09-10T01:15:00-03:00
- **Completed:** 2026-09-10T01:39:00-03:00
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Normalização determinística e idempotente de CNPJ, e-mail, domínio, telefone e JSON.
- Schema canônico com constraints, índices e vínculos temporais.
- Serviços transacionais/idempotentes com rejeição de tenant cruzado e CPF transitório.
- Test settings e CI preparados para validar semântica PostgreSQL.

## Task Commits

1. **Normalizar identificadores brasileiros** - `115ca58`
2. **Modelar grafo canônico de leads** - `4e32e7c`
3. **Criar serviços tenant-safe de identidade** - `a27e4bb`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Executar testes da CI no PostgreSQL**
- **Found during:** Task 3
- **Issue:** a etapa de qualidade ainda usaria SQLite apesar de a fase exigir caminhos críticos no PostgreSQL.
- **Fix:** a CI fornece `TEST_DATABASE_URL` para toda a suíte.
- **Verification:** settings selecionam PostgreSQL quando a variável existe; suíte local mantém fallback SQLite.
- **Committed in:** `a27e4bb`

**Total deviations:** 1 auto-fixed. **Impact:** reforça a validade produtiva sem ampliar o escopo.

## Issues Encountered

- O executável `uv` não estava no PATH; a validação usou a `.venv` reproduzível existente.
- Caches locais estavam sem permissão de escrita; Ruff e mypy rodaram com cache desabilitado.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

O `Entity` registry e os owners explícitos estão prontos para observações, conflitos e decisões
canônicas do plano 02-02.

## Self-Check: PASSED

- 18 testes direcionados passaram.
- Ruff, mypy e migration drift passaram.
- DATA-01, DATA-02 e DATA-03 possuem prova automatizada.

---
*Phase: 02-dados-confi-veis*
*Completed: 2026-09-10*
