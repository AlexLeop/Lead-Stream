# Project Research Summary

**Project:** LeadStream Backend
**Domain:** plataforma B2B Brasil-first de qualidade e enriquecimento de dados
**Researched:** 2026-09-09
**Confidence:** HIGH

## Executive Summary

O produto deve ser construído como monólito modular com API fina e processamento assíncrono durável. Django/DRF oferece o control plane, PostgreSQL mantém estado e invariantes, Celery/RabbitMQ executa lotes em chunks e Redis coordena cache, locks e limites. Polars e DuckDB tratam arquivos sem transformar o ORM em motor analítico.

O valor competitivo não está em acumular o maior número de campos, mas em separar empresa, decisor, contato e evidência, cobrando somente quando um bloco elegível é entregue. Appwrite agrega valor como storage e integração complementar, mas TablesDB não deve substituir a conexão PostgreSQL nativa do Django.

O maior risco é produzir cobertura artificial por falsos vínculos, retentativas duplicadas ou fallbacks sem orçamento. A mitigação deve nascer na fundação: proveniência por campo, state machines transacionais, idempotência, outbox e limites de custo antes das integrações reais.

## Key Findings

### Recommended Stack

**Core technologies:**
- Django 5.2 LTS + DRF 3.18: API, domínio, migrações e administração.
- PostgreSQL 17+: dados operacionais, transações, constraints e auditoria.
- Celery 5.6 + RabbitMQ: jobs duráveis, retries e filas por provedor.
- Redis: locks, cache e token buckets distribuídos.
- Polars + DuckDB: ingestão, higienização e consultas em arquivos.
- Appwrite SDK: storage e serviços externos ao domínio transacional.

### Expected Features

**Must have:**
- Lotes retomáveis com progresso e motivos de falha.
- Modelo normalizado de empresa, pessoa, vínculo, contato e evidência.
- Higienização, deduplicação, exportação e supressão.
- Custos e orçamento por provedor.
- Contratos de integração testáveis sem rede real.

**Should have:**
- Cobrança por bloco entregue.
- Resolução de identidade baseada em múltiplos sinais.
- WhatsApp como estado comprovável, nunca inferido de celular.
- Cascata que interrompe chamadas quando já existe resultado suficiente.
- Métrica de custo por lead útil e segmento.

**Defer:**
- Autenticação/RBAC e portal de clientes.
- Cobrança financeira automatizada.
- Catálogo amplo de CRMs antes de certificar o primeiro conector.

### Architecture Approach

Um monólito modular reduz custo operacional na VPS, enquanto filas e workers isolam o processamento pesado. A fronteira entre domínio e provedores permite substituir fontes sem alterar entidades ou faturamento; a fronteira de storage permite usar Appwrite agora e outro S3 posteriormente.

**Major components:**
1. API/control plane — comandos, consultas, OpenAPI e health.
2. Domínio canônico — entidades, observações, políticas e supressões.
3. Job engine — lotes, chunks, state machines, leasing e retries.
4. Provider layer — portas, adaptadores, cotas e custos.
5. Delivery layer — exportações, CRM, outbox e billing ledger.

### Critical Pitfalls

1. **Identidade falsa** — exigir evidências independentes e manter inferência rotulada.
2. **Retry duplicado** — unique constraints e idempotency keys em efeitos externos.
3. **Custo descontrolado** — reserva de orçamento e stop conditions antes de chamar fonte.
4. **Secret/data leakage** — redaction central e credenciais somente no ambiente.
5. **Appwrite como ORM remoto** — manter PostgreSQL como fonte de verdade.

## Implications for Roadmap

### Phase 1: Fundação Executável
**Rationale:** todas as capacidades dependem de configuração, banco, tenant e observabilidade corretos.
**Delivers:** projeto Django executável, PostgreSQL, health checks, Docker/EasyPanel e adaptador Appwrite seguro.
**Avoids:** segredos versionados e acoplamento do ORM ao Appwrite.

### Phase 2: Modelo Canônico e Qualidade
**Rationale:** integrações não podem preceder o contrato de empresa, pessoa, vínculo, contato e evidência.
**Delivers:** migrations, APIs e políticas básicas de canonização/supressão.
**Avoids:** promover resultados brutos a fatos.

### Phase 3: Lotes, Higienização e Billing
**Rationale:** jobs duráveis e idempotência devem existir antes de qualquer provedor pago.
**Delivers:** import, chunks, limpeza determinística, progresso, custos e eventos faturáveis.
**Avoids:** timeout, replay duplicado e cobrança por tentativa.

### Phase 4: Cascata de Enriquecimento
**Rationale:** com domínio e job engine estáveis, fontes reais podem entrar uma a uma.
**Delivers:** OpenCNPJ/BigQuery, BigDataCorp, Apify e fallbacks sob orçamento.
**Avoids:** dependência de fornecedor e explosão de custo.

### Phase 5: Entrega, CRM e Produção
**Rationale:** exports e sincronização devem consumir apenas dados consolidados e suprimidos.
**Delivers:** CSV, Appwrite Storage, primeiro CRM, outbox, dashboards operacionais e deploy validado.
**Avoids:** export inconsistente e efeitos externos perdidos.

### Phase Ordering Rationale

- Estado e qualidade precedem fontes externas.
- Jobs e billing precedem chamadas pagas.
- Export e CRM ficam após canonização e supressão.
- A primeira fase já produz um serviço implantável e verificável.

### Research Flags

- **Phase 4:** contratos comerciais, limites e payloads reais dos provedores precisam de validação antes da implementação.
- **Phase 5:** cada CRM requer documentação e ambiente de teste próprios.
- **Phase 1–3:** padrões estabelecidos; pesquisa adicional pontual é suficiente.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versões e capacidades verificadas em documentação oficial |
| Features | HIGH | Derivadas do objetivo e falhas já observadas no produto atual |
| Architecture | HIGH | Padrões consolidados de jobs, outbox e proveniência |
| Pitfalls | HIGH | Ligados diretamente ao volume, custo e qualidade exigidos |

**Overall confidence:** HIGH

### Gaps to Address

- Taxas reais de acerto e custo: medir em piloto de 5–10 mil empresas.
- Conectividade PostgreSQL local: hostname fornecido funciona apenas na rede do EasyPanel.
- Appwrite Storage: criar credencial runtime de menor privilégio após o bootstrap.
- CRMs prioritários: definir ordem antes da Phase 5.

## Sources

### Primary (HIGH confidence)
- https://www.djangoproject.com/download/ — suporte LTS.
- https://docs.djangoproject.com/en/5.2/ — framework e banco.
- https://www.django-rest-framework.org/ — API e políticas.
- https://docs.celeryq.dev/en/stable/ — jobs, brokers e retries.
- https://www.postgresql.org/docs/current/ — dados e transações.
- https://appwrite.io/docs/ — banco, SDK e storage.

### Secondary (MEDIUM confidence)
- Repositórios e documentação dos provedores de enriquecimento selecionados.
- Estimativas de custo e cobertura discutidas no planejamento do LeadStream.

---
*Research completed: 2026-09-09*
*Ready for roadmap: yes*
