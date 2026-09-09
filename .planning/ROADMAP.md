# Roadmap: LeadStream Backend

## Overview

O backend evolui em cinco fatias verticais. Primeiro nasce um serviço implantável e observável; depois ganha modelo de dados com evidências; em seguida processa e cobra lotes com segurança; então conecta a cascata real de descoberta e enriquecimento; por fim entrega exports, CRMs e operação de produção. Cada fase preserva a independência do projeto atual.

## Phases

- [ ] **Phase 1: Fundação Executável** - Backend Django seguro, implantável e conectado à infraestrutura.
- [ ] **Phase 2: Dados Confiáveis** - Modelo canônico, evidências, qualidade e governança de pessoas e empresas.
- [ ] **Phase 3: Lotes com Valor Mensurável** - Importação, higienização, jobs duráveis, custos e cobrança idempotente.
- [ ] **Phase 4: Descoberta e Enriquecimento Real** - Cascata de provedores externos sob orçamento e limites.
- [ ] **Phase 5: Entrega e Operação Comercial** - Exports, Appwrite Storage, múltiplos CRMs e runbooks de produção.

## Phase Details

### Phase 1: Fundação Executável

**Goal**: Entregar uma API Django independente, segura e implantável, com PostgreSQL, tenant interno, infraestrutura e observabilidade básica.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: FND-01, FND-02, FND-03, FND-04, FND-05, FND-06, FND-07, OPS-01, OPS-04
**Success Criteria**:

  1. Operador inicia API e dependências por containers e recebe respostas distintas de vida e prontidão.
  2. Migrações criam o tenant interno no PostgreSQL e a API aplica esse tenant automaticamente.
  3. Appwrite pode ser verificado por adaptador sem segredos no repositório e sem participar do ORM.
  4. OpenAPI descreve `/api/v1` e logs correlacionados não expõem credenciais.
  5. Lint, tipos, migrations check e testes passam em um único comando de qualidade.

**Plans**: 3 plans

Plans:
**Wave 1**

- [ ] 01-01: Estruturar projeto, configuração, PostgreSQL e tenant interno.

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 01-02: Implementar health, OpenAPI, Appwrite adapter e observabilidade segura.

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 01-03: Empacotar containers, ambiente local/EasyPanel e gates de qualidade.

### Phase 2: Dados Confiáveis

**Goal**: Representar empresas, decisores, vínculos, contatos e evidências sem confundir observação, inferência e confirmação.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06, COMP-01, COMP-02, COMP-03
**Success Criteria**:

  1. Operador registra CNPJ, pessoa, vínculo, contato e perfil com isolamento por tenant.
  2. Todo valor enriquecido expõe fonte, data, método, confiança e estado de evidência.
  3. Políticas promovem e recanonizam valores determinísticamente, preservando conflitos.
  4. Supressão e expiração impedem uso futuro sem destruir a trilha de auditoria necessária.

**Plans**: 3 plans

Plans:

- [ ] 02-01: Modelar empresa, pessoa, vínculo, contato e perfil.
- [ ] 02-02: Implementar observações, evidências, canonização e conflitos.
- [ ] 02-03: Expor APIs do domínio e políticas de retenção/supressão.

### Phase 3: Lotes com Valor Mensurável

**Goal**: Transformar arquivos de até 100 mil entradas em jobs retomáveis, dados higienizados e eventos de custo/cobrança auditáveis.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: HYG-01, HYG-02, HYG-03, BATCH-01, BATCH-02, BATCH-03, BATCH-04, BATCH-05, BILL-01, BILL-02, BILL-03, BILL-04, BILL-05, OPS-03
**Success Criteria**:

  1. Operador envia 100 mil entradas e recebe imediatamente o ID de um lote persistente.
  2. Reiniciar API, broker ou worker não perde progresso nem repete efeitos confirmados.
  3. Higienização preserva originais e explica correções, duplicidades e invalidações.
  4. Replays não duplicam custo ou cobrança, e ausência/erro nunca é faturado.
  5. Operador consulta progresso, cobertura, custo, receita projetada e lucro bruto.

**Plans**: 3 plans

Plans:

- [ ] 03-01: Implementar lotes, chunks, state machines, leasing e comandos operacionais.
- [ ] 03-02: Implementar ingestão CSV, normalização e deduplicação em bulk.
- [ ] 03-03: Implementar custos, tabela de preços e ledger faturável idempotente.

### Phase 4: Descoberta e Enriquecimento Real

**Goal**: Descobrir empresas e complementar decisores, contatos e perfis usando a melhor cascata de fontes permitidas sob orçamento observável.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: DISC-01, DISC-02, PROV-01, PROV-02, PROV-03, PROV-04, PROV-05, PROV-06, PROV-07, OPS-02
**Success Criteria**:

  1. Operador filtra empresas brasileiras e transforma resultados em lote sem baixar a base nacional para a VPS.
  2. Provedores reais e fixtures obedecem ao mesmo contrato e geram observações, nunca fatos diretamente.
  3. Rate limits, circuit breakers e orçamentos funcionam entre múltiplos workers.
  4. A cascata encerra chamadas quando encontra resultado suficiente ou atinge o limite financeiro.
  5. Métricas mostram custo, latência, erro e cobertura por fonte, bloco e segmento.

**Plans**: 3 plans

Plans:

- [ ] 04-01: Criar provider SDK interno, quotas, circuit breaker e orçamento.
- [ ] 04-02: Integrar OpenCNPJ/BigQuery e BigDataCorp.
- [ ] 04-03: Integrar Apify, Open Enrich, fallback premium e orquestração da cascata.

### Phase 5: Entrega e Operação Comercial

**Goal**: Entregar resultados minimizados por CSV e múltiplos CRMs com efeitos idempotentes e uma implantação recuperável.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: EXP-01, EXP-02, EXP-03, CRM-01, CRM-02, CRM-03, CRM-04, COMP-04, OPS-05
**Success Criteria**:

  1. Operador gera CSV pt-BR e manifesto reproduzível após aplicar supressões.
  2. Entradas, saídas e evidências extensas são armazenadas pelo adaptador Appwrite com referências no PostgreSQL.
  3. Tenant mantém múltiplas conexões e envia leads idempotentemente para HubSpot, Pipedrive ou RD Station.
  4. Falha entre banco e CRM é retomada pela outbox sem duplicar contatos.
  5. Runbooks comprovam deploy, backup, restore, rotação de credenciais e recuperação de lote.

**Plans**: 3 plans

Plans:

- [ ] 05-01: Implementar exportação, manifesto, minimização e Appwrite Storage.
- [ ] 05-02: Implementar outbox e conectores HubSpot, Pipedrive e RD Station.
- [ ] 05-03: Validar produção, segurança operacional, backup, restore e piloto medido.

## Progress

**Execution Order:** 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Fundação Executável | 0/3 | Not started | - |
| 2. Dados Confiáveis | 0/3 | Not started | - |
| 3. Lotes com Valor Mensurável | 0/3 | Not started | - |
| 4. Descoberta e Enriquecimento Real | 0/3 | Not started | - |
| 5. Entrega e Operação Comercial | 0/3 | Not started | - |
