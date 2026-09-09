# Pitfalls Research

**Domain:** enriquecimento de dados B2B em grande volume
**Researched:** 2026-09-09
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Dado encontrado tratado como identidade confirmada

**What goes wrong:** um perfil, telefone ou e-mail de homônimo é atribuído ao decisor.

**Why it happens:** busca textual e snippets são tratados como prova de vínculo.

**How to avoid:** guardar observações, exigir sinais independentes, aplicar thresholds por campo e nunca ocultar o estado da evidência.

**Warning signs:** cobertura muito alta, poucos resultados ausentes e ausência de URL/trecho/data.

**Phase to address:** modelo canônico e política de qualidade.

---

### Pitfall 2: Duplicidade causada por retentativa

**What goes wrong:** o mesmo provedor é chamado ou o mesmo bloco é faturado várias vezes.

**Why it happens:** tarefas usam retry sem chave idempotente e sem checkpoint transacional.

**How to avoid:** idempotency keys, leasing de chunks, unique constraints e eventos de cobrança imutáveis.

**Warning signs:** custo superior ao número de itens, registros repetidos e progresso acima de 100%.

**Phase to address:** jobs e billing ledger.

---

### Pitfall 3: Explosão de custo por fallback

**What goes wrong:** todos os leads atravessam todos os provedores mesmo após sucesso ou baixa prioridade.

**Why it happens:** orquestração linear sem orçamento, stop condition ou score de valor.

**How to avoid:** budget reservation, circuit breaker, matriz campo-fonte e fallback apenas para pendências elegíveis.

**Warning signs:** custo médio cresce sem aumento proporcional da cobertura útil.

**Phase to address:** cascata de provedores.

---

### Pitfall 4: Segredos e dados pessoais vazando em logs

**What goes wrong:** tokens, valores completos, CSVs ou payloads aparecem em Git e observabilidade.

**Why it happens:** logging indiscriminado e exceptions contendo headers/payloads.

**How to avoid:** redaction central, hashes para correlação, secrets no EasyPanel e testes automatizados de vazamento.

**Warning signs:** headers de autorização ou telefone/e-mail completo em logs.

**Phase to address:** fundação de produção.

---

### Pitfall 5: Confundir Appwrite TablesDB com conexão PostgreSQL

**What goes wrong:** o domínio Django passa a depender de round-trips HTTP e perde migrações/consultas do ORM.

**Why it happens:** ambos são apresentados como bancos estruturados, mas possuem interfaces diferentes.

**How to avoid:** PostgreSQL nativo como banco operacional; Appwrite atrás de interface de storage.

**Warning signs:** models Django sem migrations e repositories chamando SDK para cada linha.

**Phase to address:** fundação de produção.

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Tenant fixo sem coluna | Menos código | Migração invasiva futura | Never |
| Um JSON gigante por lead | Entrega rápida | Consulta, conflito e proveniência frágeis | Apenas raw payload no storage |
| Mock com nome de fonte real | Demo convincente | Métricas falsas e risco comercial | Never |
| Sem outbox | Menos tabelas | Eventos perdidos entre banco e broker | Never para billing/CRM |
| Índices em todas as colunas | Consulta inicial fácil | Escrita cara e disco desperdiçado | Never sem evidência de query |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| BigQuery/OpenCNPJ | Baixar base inteira para a VPS | Consultas seletivas ou Parquet externo |
| BigDataCorp | Ignorar cobrança por dataset | Registrar custo estimado e confirmado por chamada |
| Apify | Polling agressivo e runs gigantes | Runs pequenos, webhooks e concorrência limitada |
| Appwrite | Enviar secret ao frontend | Usar exclusivamente no backend |
| CRM | Criar duplicata a cada replay | External ID, idempotency key e outbox |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| ORM por linha | CPU baixa e lote lento | `bulk_create`, COPY ou staging | Dezenas de milhares de linhas |
| Offset pagination | Páginas finais lentas | Cursor por ID estável | Centenas de milhares de linhas |
| Payloads grandes na fila | RabbitMQ e workers com memória alta | Passar IDs e guardar arquivos no storage | Milhares de tarefas |
| Task por lead | Broker congestionado | Chunks de 25–100 | 100 mil leads |
| Totais recalculados | Locks e queries caras | Contadores incrementais transacionais | Jobs concorrentes |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Credencial com acesso total permanente | Comprometimento completo | Chave de bootstrap temporária e chave runtime mínima |
| API interna exposta publicamente | Exfiltração de dados | Gateway privado/API key técnica e allowlist |
| Export sem aplicar supressões | Violação de direitos e finalidade | Política obrigatória antes da geração |
| Evidência com conteúdo excessivo | Retenção desnecessária | Trecho mínimo/hash e TTL por fonte |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Mostrar apenas percentual | Não explica espera ou falha | Etapa, processados, sucessos, custos e ETA |
| Misturar ausente com erro | Usuário não sabe se deve tentar novamente | Estados separados e motivo estruturado |
| Exportar confiança sem evidência | Score parece arbitrário | Fonte, data, método e rótulo legíveis |

## "Looks Done But Isn't" Checklist

- [ ] **Lote assíncrono:** reiniciar worker e confirmar retomada sem duplicidade.
- [ ] **Idempotência:** repetir requisição e provar que custo e cobrança não duplicam.
- [ ] **Qualidade:** resultado sem evidência nunca é exportado como confirmado.
- [ ] **WhatsApp:** celular não recebe esse rótulo sem sinal específico.
- [ ] **Multi-tenant:** queries e unique constraints incluem tenant.
- [ ] **Segurança:** secret scanner não encontra credenciais reais.
- [ ] **Exportação:** supressões são aplicadas imediatamente antes da geração.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Cobrança duplicada | MEDIUM | bloquear ledger, recalcular por idempotency key e emitir ajuste |
| Dados incorretos promovidos | HIGH | invalidar política, recanonizar observações e regenerar exports |
| Provider fora do ar | LOW | abrir circuit breaker, adiar fila e retomar do checkpoint |
| Secret exposto | MEDIUM | revogar, rotacionar, auditar uso e limpar histórico quando aplicável |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Segredos/Appwrite mal posicionado | Phase 1 | configuração falha fechada e nenhum secret no Git |
| Identidade sem evidência | Phase 2 | constraints e testes de promoção |
| Retry e custo duplicados | Phase 3 | testes de replay e concorrência |
| Fallback caro | Phase 4 | testes de orçamento e circuit breaker |
| Export/CRM inconsistente | Phase 5 | outbox, supressão e testes E2E |

## Sources

- https://docs.celeryq.dev/en/stable/userguide/tasks.html — retries e rate limits
- https://appwrite.io/docs/products/databases/tablesdb/bulk-operations — bulk e atomicidade
- https://appwrite.io/docs/products/databases/pagination — cursor pagination e custos de offset
- https://www.django-rest-framework.org/api-guide/throttling/ — limites do throttling da aplicação
- Restrições e problemas observados no LeadStream atual.

---
*Pitfalls research for: LeadStream Backend*
*Researched: 2026-09-09*
