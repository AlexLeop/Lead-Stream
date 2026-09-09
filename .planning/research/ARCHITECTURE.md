# Architecture Research

**Domain:** backend de dados B2B com processamento assíncrono em lote
**Researched:** 2026-09-09
**Confidence:** HIGH

## Standard Architecture

### System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    API / Control Plane                      │
│ DRF · OpenAPI · tenants · lotes · consultas · exports      │
└───────────────────────────┬─────────────────────────────────┘
                            │ cria comandos
┌───────────────────────────▼─────────────────────────────────┐
│                  Orquestração Assíncrona                    │
│ Celery · RabbitMQ · filas por provedor · scheduler          │
└───────────┬────────────────┬────────────────┬───────────────┘
            │                │                │
        Cadastro         Decisores        Contatos/CRM
            └────────────────┼────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Domínio Canônico                        │
│ empresa → pessoa → vínculo → perfil → contato → evidência  │
│ jobs · custos · eventos faturáveis · supressões             │
└───────────────────────┬───────────────────┬─────────────────┘
                        ▼                   ▼
                  PostgreSQL         Storage externo/Appwrite
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| API | Validar comandos, consultar estado e devolver DTOs | DRF ViewSets/serializers finos |
| Application services | Coordenar casos de uso e transações | Serviços Python explícitos |
| Domain | Entidades, estados e invariantes | Models + regras sem dependência de HTTP |
| Orchestrator | Dividir lotes, avançar etapas e retomar falhas | Celery tasks idempotentes |
| Provider adapters | Traduzir cada fonte ao contrato canônico | HTTPX + Pydantic + fixtures |
| Repository | Consultas e bulk operations | Django ORM e SQL específico quando necessário |
| Object storage | Entradas, exports e evidências extensas | Appwrite Storage ou S3 compatível |
| Billing ledger | Registrar somente entregas elegíveis | Eventos imutáveis com chave idempotente |

## Recommended Project Structure

```text
src/
├── config/                 # settings, URLs, ASGI, Celery
├── leadstream/
│   ├── common/             # IDs, dinheiro, erros, observabilidade
│   ├── tenancy/            # tenant interno e isolamento
│   ├── companies/          # empresa e dados cadastrais
│   ├── people/             # pessoa, vínculo e cargo
│   ├── contacts/           # e-mail, telefone, WhatsApp e perfis
│   ├── evidence/           # observações, fontes e confiança
│   ├── batches/            # lotes, itens, chunks e etapas
│   ├── providers/          # portas e adaptadores externos
│   ├── billing/            # custos e eventos faturáveis
│   ├── compliance/         # finalidade, retenção e supressão
│   ├── exports/            # CSV e manifestos
│   └── crm/                # conectores e sincronizações
├── tests/
└── manage.py
```

### Structure Rationale

- **Módulos por capacidade:** mantém modelos, API, serviços e testes próximos sem criar um arquivo monolítico.
- **Providers separado:** impede que DTOs da BigDataCorp ou Apify contaminem o modelo canônico.
- **Evidence separado:** um valor canônico pode possuir várias observações conflitantes ou complementares.
- **Batches separado:** o ciclo de vida do processamento não pertence ao provedor nem ao lead.

## Architectural Patterns

### Ports and Adapters

**What:** o domínio chama interfaces estáveis e os SDKs ficam nas bordas.
**When to use:** todas as fontes e todos os CRMs.
**Trade-offs:** adiciona classes pequenas, mas facilita fallback, fixtures e troca de fornecedor.

### Transactional State Machine

**What:** estados válidos de lote, etapa e item mudam por transações condicionais.
**When to use:** agendamento, leasing de chunks, retry, cancelamento e conclusão.
**Trade-offs:** exige invariantes explícitas; elimina progresso impossível e execução duplicada.

### Outbox

**What:** a transação grava a mudança de estado e um evento pendente; um publicador despacha depois.
**When to use:** CRM, webhooks, exportações e eventos de cobrança.
**Trade-offs:** consistência eventual controlada em troca de não perder eventos.

### Evidence-first Canonicalization

**What:** provedores criam observações; uma política separada promove o melhor valor ao registro canônico.
**When to use:** qualquer dado enriquecido.
**Trade-offs:** mais tabelas e consultas, porém auditabilidade e correção muito superiores.

## Data Flow

### Request Flow

```text
POST /lotes → valida metadados → grava lote → outbox → agenda ingestão
HTTP 202 + lote_id
GET /lotes/{id} → snapshot de progresso persistido → resposta
```

### Key Data Flows

1. **Importação:** arquivo vai ao storage, é lido em streaming/chunks, normalizado e inserido em bulk.
2. **Enriquecimento:** cada etapa seleciona pendências, reserva chunks e chama o adaptador sob orçamento e rate limit.
3. **Canonização:** observações são avaliadas por política de fonte, atualidade e confiança.
4. **Cobrança:** somente uma promoção elegível cria evento faturável idempotente.
5. **Exportação:** aplica supressões e produz CSV mais manifesto de cobertura, custos e evidências.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Até 10 mil por lote | Monólito modular, um worker e chunks de 25–100 |
| 10–100 mil por lote | Filas por provedor, bulk inserts, cursor pagination e workers separados |
| Acima de 100 mil concorrentes | PostgreSQL gerenciado, workers horizontais e storage direto compatível com S3 |

### Scaling Priorities

1. **Primeiro gargalo:** cotas e latência dos provedores; resolver com filas dedicadas, token bucket e backpressure.
2. **Segundo gargalo:** escrita de observações; resolver com batch, índices seletivos e particionamento somente após métricas.
3. **Terceiro gargalo:** exports e relatórios; mover para Parquet/object storage e consultas colunares.

## Anti-Patterns

### Long Request Processing

**What people do:** processar o lote dentro do endpoint.
**Why it's wrong:** desconexões, timeout e falta de retomada.
**Do this instead:** responder 202 e executar uma state machine durável.

### Provider DTO as Domain Model

**What people do:** salvar JSON do provedor diretamente como lead.
**Why it's wrong:** acoplamento, conflitos e impossibilidade de explicar origem.
**Do this instead:** preservar raw no storage e converter para observações canônicas.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenCNPJ/BigQuery | Adapter + consultas parametrizadas | Dados empresariais e societários |
| BigDataCorp | Adapter HTTP + fila e quota próprias | Contatos relacionados e custo por dataset |
| Apify | Adapter de actor/run + webhook/polling | Decisores e perfis públicos |
| Open Enrich | Adapter opcional | Aplicar apenas a pendências selecionadas |
| LeadsFactory | Fallback premium | Somente leads prioritários sob orçamento |
| Appwrite | Storage adapter server-side | Secret apenas no ambiente |
| CRMs | Connector + outbox | Upsert com chave externa e replay seguro |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| API ↔ application | chamada direta | API não contém regra de negócio |
| application ↔ providers | interface tipada | sem import de SDK no domínio |
| transaction ↔ Celery | outbox | nunca publicar antes do commit |
| canonical ↔ billing | evento de domínio | cobrar uma única vez por janela |

## Sources

- https://docs.djangoproject.com/en/5.2/ — Django e transações
- https://www.django-rest-framework.org/ — API, filtros e paginação
- https://docs.celeryq.dev/en/stable/ — filas, tarefas, retries e rate limits
- https://www.postgresql.org/docs/current/ — constraints, índices, JSONB e RLS
- https://appwrite.io/docs/products/databases — TablesDB e bancos nativos
- https://appwrite.io/docs/products/storage — storage e permissões

---
*Architecture research for: LeadStream Backend*
*Researched: 2026-09-09*
