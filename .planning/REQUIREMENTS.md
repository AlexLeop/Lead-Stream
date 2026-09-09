# Requirements: LeadStream Backend

**Defined:** 2026-09-09
**Core Value:** Entregar somente dados úteis atribuíveis à empresa ou ao decisor correto, com proveniência suficiente para distinguir fato, validação, inferência e ausência de dado.

## v1 Requirements

### Fundação e configuração

- [x] **FND-01**: Operador pode consultar endpoints de vida e prontidão que verificam aplicação e dependências separadamente.
- [x] **FND-02**: Aplicação carrega configuração exclusivamente do ambiente, falha de forma segura e nunca registra segredos.
- [x] **FND-03**: Aplicação usa PostgreSQL nativo como fonte operacional de verdade com migrações reproduzíveis.
- [x] **FND-04**: Toda entidade de negócio pertence a um tenant, com tenant interno aplicado automaticamente no uso inicial.
- [x] **FND-05**: Operador pode verificar a integração Appwrite sem usar TablesDB como substituto do ORM Django.
- [ ] **FND-06**: Operador pode executar API, worker, broker, cache e banco em ambiente local e implantar serviços equivalentes no EasyPanel.
- [x] **FND-07**: API publica contrato OpenAPI versionado sob `/api/v1` e mensagens operacionais em português do Brasil.

### Modelo canônico e evidências

- [ ] **DATA-01**: Operador pode registrar empresa brasileira por CNPJ normalizado sem duplicidade dentro do tenant.
- [ ] **DATA-02**: Operador pode registrar uma pessoa e seus vínculos temporais com empresas, cargos e papéis decisórios.
- [ ] **DATA-03**: Operador pode registrar e-mail, telefone, estado de WhatsApp e perfis sociais como pontos de contato independentes.
- [ ] **DATA-04**: Todo dado enriquecido mantém fonte, URL ou identificador, instante, método, trecho ou hash, confiança e estado de evidência.
- [ ] **DATA-05**: Política determinística promove observações ao valor canônico sem transformar inferência ou busca isolada em fato confirmado.
- [ ] **DATA-06**: Conflitos entre fontes permanecem auditáveis e podem ser recanonizados quando a política muda.

### Descoberta e higienização

- [ ] **DISC-01**: Operador pode descobrir empresas por filtros de segmento, localização, porte, situação, CNAE e características disponíveis nas fontes cadastradas.
- [ ] **DISC-02**: Descoberta retorna resultados paginados e pode materializar seleção como lote sem baixar a base nacional para a VPS.
- [ ] **HYG-01**: Sistema normaliza CNPJ, razão social, domínio, e-mail e telefone por regras determinísticas e testadas.
- [ ] **HYG-02**: Sistema deduplica e correlaciona registros preservando o valor original, a regra aplicada e o motivo da decisão.
- [ ] **HYG-03**: Sistema diferencia valor inválido, ausente, inalterado, corrigido, inferido e validado.

### Lotes e execução

- [ ] **BATCH-01**: Operador pode enviar CSV ou uma seleção de descoberta com até 100 mil empresas e recebe um ID sem aguardar o processamento.
- [ ] **BATCH-02**: Sistema divide lotes em chunks configuráveis e persiste o estado de cada lote, etapa, item e tentativa.
- [ ] **BATCH-03**: Job interrompido retoma do checkpoint sem repetir efeitos já confirmados.
- [ ] **BATCH-04**: Operador pode pausar, retomar ou cancelar trabalho ainda não iniciado sem corromper resultados concluídos.
- [ ] **BATCH-05**: Progresso expõe totais, etapa atual, sucessos, ausências, erros, custo, cobertura e estimativa de conclusão.

### Provedores e cascata

- [ ] **PROV-01**: Todo provedor implementa um contrato tipado comum com suporte a fixture, timeout, retry, quota, custo e proveniência.
- [ ] **PROV-02**: OpenCNPJ/BigQuery fornece cadastro empresarial e quadro societário por consultas seletivas.
- [ ] **PROV-03**: BigDataCorp complementa e-mails e telefones de pessoas relacionadas sob orçamento configurável.
- [ ] **PROV-04**: Apify resolve decisores e perfis públicos por actors configuráveis sem acessar conteúdo privado.
- [ ] **PROV-05**: Open Enrich e provedor premium podem atuar como fallback somente para pendências elegíveis e priorizadas.
- [ ] **PROV-06**: Sistema aplica rate limit global por credencial/fonte, backoff, circuit breaker e limite financeiro antes de cada chamada.
- [ ] **PROV-07**: Sistema interrompe a cascata de um campo quando já existe resultado suficiente ou quando o orçamento é atingido.

### Custos e cobrança

- [ ] **BILL-01**: Sistema registra custo estimado e confirmado de cada chamada externa em centavos e moeda de origem.
- [ ] **BILL-02**: Sistema cria cobrança apenas para bloco efetivamente entregue e elegível, nunca por tentativa, erro, ausência ou baixa confiança.
- [ ] **BILL-03**: Cobrança é idempotente por tenant, registro, bloco, valor e janela de atualização.
- [ ] **BILL-04**: Operador pode consultar receita projetada, custo, lucro bruto e cobertura por lote, provedor e bloco.
- [ ] **BILL-05**: Tabela de preços possui histórico; alterações não modificam eventos já gerados.

### Privacidade e governança

- [ ] **COMP-01**: Todo tratamento pessoal registra finalidade profissional, base operacional, origem e política de retenção.
- [ ] **COMP-02**: Operador pode suprimir pessoa, domínio, e-mail ou telefone e a supressão é aplicada antes de exportar ou sincronizar.
- [ ] **COMP-03**: Sistema expira ou marca como desatualizados contatos conforme política configurável sem apagar a trilha de auditoria necessária.
- [ ] **COMP-04**: Exportações e logs minimizam dados e nunca incluem segredos de provedores.

### Exportação e CRM

- [ ] **EXP-01**: Operador pode gerar CSV em pt-BR contendo apenas colunas e estados selecionados.
- [ ] **EXP-02**: Cada exportação acompanha manifesto com filtros, cobertura, custos, data, versão da política e contagem de evidências.
- [ ] **EXP-03**: Arquivos de entrada, saída e evidências extensas podem ser armazenados pelo adaptador Appwrite com IDs persistidos no PostgreSQL.
- [ ] **CRM-01**: Sistema oferece contrato de conector com mapeamento de campos, credenciais por tenant, upsert e relatório de erros.
- [ ] **CRM-02**: Tenant pode manter múltiplas conexões CRM e escolher destino por job ou exportação.
- [ ] **CRM-03**: Sincronizações são idempotentes, passam por outbox e nunca recriam um contato já vinculado.
- [ ] **CRM-04**: HubSpot, Pipedrive e RD Station usam o mesmo contrato e possuem testes por fixture antes de conexão real.

### Operação e qualidade

- [x] **OPS-01**: Logs estruturados correlacionam request, tenant, lote, chunk e provedor com redação de dados sensíveis.
- [ ] **OPS-02**: Métricas mostram filas, latência, erros, retries, circuit breakers, custo e cobertura por fonte.
- [ ] **OPS-03**: Testes não dependem de rede real e cobrem transações, idempotência, replay, promoção de evidência e isolamento de tenant.
- [ ] **OPS-04**: Pipeline de qualidade executa lint, tipos, migrations check e testes antes do build de produção.
- [ ] **OPS-05**: Operador possui runbook de implantação, backup, restore, rotação de credenciais e recuperação de lote.

## v2 Requirements

### Acesso externo

- **AUTH-01**: Cliente pode autenticar usuários e gerenciar sessões.
- **AUTH-02**: Cliente pode atribuir papéis e permissões dentro do tenant.
- **AUTH-03**: Administrador pode usar MFA e revogar sessões.

### Comercial

- **PAY-01**: Cliente pode contratar créditos e receber cobrança financeira automatizada.
- **PORTAL-01**: Cliente pode operar lotes em portal próprio sem acesso ao painel interno.

### Expansão

- **AI-01**: Revisão assistida por IA pode priorizar casos ambíguos sem promover resultados automaticamente.
- **CRM-05**: Novos conectores são adicionados conforme demanda e certificação.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Alterar o LeadStream atual | O backend novo deve ser independente até integração posterior explícita |
| Autenticação de usuários no v1 | Operação inicial interna; proteção ocorre no perímetro |
| Casa dos Dados | Fonte removida por decisão do proprietário |
| Contorno de paywall, login, CAPTCHA ou robots | Incompatível com operação sustentável e requisitos de fonte |
| WhatsApp inferido apenas por ser celular | Não há evidência suficiente de disponibilidade no canal |
| Base bruta nacional na VPS | Capacidade de armazenamento é insuficiente |
| Cobrança por tentativa | Contraria a proposta comercial de pagar por resultado entregue |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FND-01, FND-02, FND-03, FND-04, FND-05, FND-06, FND-07 | Phase 1 | Pending |
| OPS-01, OPS-04 | Phase 1 | Pending |
| DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06 | Phase 2 | Pending |
| COMP-01, COMP-02, COMP-03 | Phase 2 | Pending |
| HYG-01, HYG-02, HYG-03 | Phase 3 | Pending |
| BATCH-01, BATCH-02, BATCH-03, BATCH-04, BATCH-05 | Phase 3 | Pending |
| BILL-01, BILL-02, BILL-03, BILL-04, BILL-05 | Phase 3 | Pending |
| OPS-03 | Phase 3 | Pending |
| DISC-01, DISC-02 | Phase 4 | Pending |
| PROV-01, PROV-02, PROV-03, PROV-04, PROV-05, PROV-06, PROV-07 | Phase 4 | Pending |
| OPS-02 | Phase 4 | Pending |
| EXP-01, EXP-02, EXP-03 | Phase 5 | Pending |
| CRM-01, CRM-02, CRM-03, CRM-04 | Phase 5 | Pending |
| COMP-04, OPS-05 | Phase 5 | Pending |

**Coverage:**

- v1 requirements: 51 total
- Mapped to phases: 51
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-09*
*Last updated: 2026-09-09 after roadmap creation*
