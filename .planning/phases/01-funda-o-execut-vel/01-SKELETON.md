# Walking Skeleton — LeadStream Backend

**Phase:** 1
**Generated:** 2026-09-09

## Capability Proven End-to-End

> O operador abre a documentação interativa, consulta o workspace interno e recebe do PostgreSQL o tenant criado por migration.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Django 5.2 LTS + DRF 3.18 | Domínio, API e migrações maduras |
| Data layer | PostgreSQL nativo + Django ORM | Fonte transacional de verdade |
| Auth | Sem autenticação de produto no v1; perímetro de implantação | Uso inicial interno |
| Deployment target | Containers no EasyPanel | Compatível com a VPS existente |
| Directory layout | Monólito modular em `src/leadstream/*` | Baixo custo operacional e fronteiras claras |
| Background jobs | Celery + RabbitMQ; Redis para coordenação | Lotes futuros exigem retries e quotas duráveis |
| External storage | Appwrite por adaptador | Evita acoplar domínio e ORM ao serviço externo |

## Stack Touched in Phase 1

- [ ] Project scaffold (framework, build, lint, test runner)
- [ ] Routing — at least one real route
- [ ] Database — at least one real read AND one real write
- [ ] UI — Swagger oferece interação real com a API
- [ ] Deployment — execução full-stack local documentada e manifesto EasyPanel preparado

## Out of Scope (Deferred to Later Slices)

- Empresas, pessoas, contatos, perfis e evidências completas.
- Importação e processamento de lotes.
- Provedores reais de enriquecimento.
- Exportações e conectores CRM.
- Autenticação de usuários e portal de clientes.

## Subsequent Slice Plan

- Phase 2: registrar empresas, pessoas, contatos e evidências confiáveis.
- Phase 3: processar lotes, higienizar dados e medir valor entregue.
- Phase 4: executar descoberta e enriquecimento reais sob orçamento.
- Phase 5: exportar, sincronizar CRMs e validar produção.
