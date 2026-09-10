---
phase: 02-dados-confi-veis
plan: "03"
subsystem: api-governance
tags: [drf, openapi, tenant, suppression, retention]
requires:
  - phase: 02-dados-confi-veis
    provides: domínio canônico, evidências e decisões versionadas
provides:
  - API v1 paginada para empresas, pessoas, vínculos, contatos e perfis
  - API de proveniência, canonização, conflitos, supressão e retenção
  - supressão por HMAC sem persistir o valor em claro
  - isolamento tenant-safe em listagens, gravações e referências
affects: [batches, providers, exports, crm]
tech-stack:
  added: []
  patterns: [tenant from context, write-only sensitive input, immutable decisions]
key-files:
  created:
    - src/leadstream/entities/serializers.py
    - src/leadstream/evidence/serializers.py
    - src/leadstream/governance/serializers.py
    - tests/test_data_api.py
  modified:
    - src/config/urls.py
    - src/config/settings/base.py
key-decisions:
  - "O tenant nunca é aceito do payload; é resolvido pelo contexto interno."
  - "Supressões persistem somente HMAC versionado e seus valores não retornam pela API."
  - "OpenAPI usa nomes de enum estáveis e validação sem warnings."
patterns-established:
  - "Qualquer referência cruzada entre tenants falha antes da persistência."
  - "Canonização exclui observações suprimidas e cria uma nova versão ABSENT."
requirements-completed: [COMP-03]
duration: 38min
completed: 2026-09-10
---

# Phase 2 Plan 03: API e Governança Summary

**Domínio canônico exposto por API tenant-safe, com supressão irreversível, retenção auditável e contrato OpenAPI validado**

## Accomplishments

- Fluxo HTTP completo de empresa até decisão canônica com proveniência.
- Supressão de pessoa, domínio, e-mail e telefone por HMAC versionado.
- Retenção marca contatos como desatualizados/expirados sem apagar auditoria.
- Testes impedem override de tenant e referências cruzadas entre clientes.

## Task Commits

1. **Aplicar supressão e retenção auditáveis** - `da6124a`
2. **Expor domínio canônico por API** - `f3137c7`
3. **Provar isolamento e governança** - `19ce872`

## Verification

- Ruff, mypy, migrations check e OpenAPI passaram.
- 52 testes passaram; o teste do trigger PostgreSQL fica a cargo da CI com PostgreSQL real.
- COMP-02 permanece aberto até a Phase 5 provar supressão antes de export e CRM.

## Next Phase Readiness

O grafo de dados e a governança estão prontos para receber ingestão em lote sem perder
originais, proveniência ou isolamento.

---
*Phase: 02-dados-confi-veis*
*Completed: 2026-09-10*
