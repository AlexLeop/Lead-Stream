# Phase 1: Fundação Executável - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-09
**Phase:** 1-Fundação Executável
**Areas discussed:** Topologia de serviços, Tenant e acesso interno, Saúde e prontidão, Deploy e segredos

---

## Topologia de serviços

| Option | Description | Selected |
|--------|-------------|----------|
| Stack completa recomendada | PostgreSQL, Django, Celery, RabbitMQ, Redis e Appwrite desacoplado | ✓ |
| Redis como broker único | Menos serviços, menor isolamento de responsabilidades | |
| API sem workers | Processamento limitado ao ciclo HTTP | |

**User's choice:** Configurações automáticas baseadas na melhor combinação recomendada.
**Notes:** PostgreSQL é nativo; Appwrite não substitui o ORM.

---

## Tenant e acesso interno

| Option | Description | Selected |
|--------|-------------|----------|
| Tenant interno + perímetro | Schema tenant-aware, sem login no v1 | ✓ |
| Sem tenant | Adiar isolamento para migração futura | |
| Autenticação completa agora | Criar usuários e RBAC no primeiro marco | |

**User's choice:** Uso interno sem autenticação, preservando evolução futura.
**Notes:** Perímetro de implantação protege a API.

---

## Saúde e prontidão

| Option | Description | Selected |
|--------|-------------|----------|
| Readiness por criticidade | PostgreSQL obrigatório e integrações diagnosticáveis separadamente | ✓ |
| Todas obrigatórias | Qualquer provedor fora do ar derruba readiness | |
| Somente processo vivo | Não detecta banco indisponível | |

**User's choice:** Selecionado automaticamente como padrão recomendado.
**Notes:** Appwrite é opcional para a API básica.

---

## Deploy e segredos

| Option | Description | Selected |
|--------|-------------|----------|
| Release command explícito | Migração única antes do rollout e secrets no EasyPanel | ✓ |
| Migrar em todo startup | Risco de concorrência entre processos | |
| Migração manual | Processo não reproduzível | |

**User's choice:** Selecionado automaticamente como padrão recomendado.
**Notes:** Nenhuma credencial real será persistida no Git.

## the agent's Discretion

- Organização interna de settings, biblioteca de logs e parâmetros iniciais de pool/timeouts.

## Deferred Ideas

None.
