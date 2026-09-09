# Feature Research

**Domain:** inteligência comercial B2B Brasil-first
**Researched:** 2026-09-09
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Importação CSV e filtros | Entrada habitual de bases comerciais | MEDIUM | Upload direto para storage e validação assíncrona |
| Higienização e deduplicação | Evita desperdício e duplicidade no CRM | HIGH | Preservar original e explicar cada alteração |
| Progresso retomável | Lotes grandes demoram horas | HIGH | Job, etapa, chunk, checkpoint e retry |
| Empresa e decisor separados | Contato genérico não atende ao objetivo | HIGH | Pessoa e vínculo possuem ciclo de vida próprio |
| Evidência e confiança | Usuário precisa distinguir fato de inferência | HIGH | Obrigatório para qualquer valor exportável |
| Exportação CSV | Resultado precisa entrar na operação comercial | MEDIUM | Colunas pt-BR e manifesto de qualidade |
| Custos e orçamento | Provedores são cobrados por chamada | HIGH | Limite por job e por fonte |
| Auditoria e supressão | Dados pessoais exigem governança | HIGH | Retenção, finalidade e remoção rastreável |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cobrança por bloco entregue | Cliente paga somente por valor comprovado | HIGH | Ledger imutável e idempotente |
| Resolução de identidade baseada em evidência | Reduz falso positivo entre homônimos | HIGH | Regras determinísticas antes de IA |
| WhatsApp sem presunção | Evita vender celular como WhatsApp | HIGH | Estado próprio e fonte específica |
| Cascata custo-aware | Maximiza cobertura respeitando orçamento | HIGH | Stop conditions e fallback seletivo |
| Proveniência por campo | Facilita auditoria e revisão humana | HIGH | Observação independente do valor canônico |
| Métrica de custo por lead útil | Permite otimizar margem real | MEDIUM | Custo por bloco, provedor e segmento |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Enriquecer tudo em uma única requisição | Parece simples | Timeouts, falhas irreparáveis e ausência de progresso | Jobs assíncronos |
| Alta confiança gerada por IA sem fonte | Aumenta cobertura aparente | Produz falsos fatos | Inferência rotulada e não faturável |
| Scraping com contorno de bloqueios | Reduz custo aparente | Risco jurídico, operacional e de reputação | Fontes permitidas e provedores contratados |
| Guardar toda a Receita na VPS | Acesso local rápido | Disco insuficiente e operação pesada | Parquet em object storage + consultas seletivas |
| Sincronização CRM genérica | Promete muitos logos | Mapeamentos e idempotência variam | Adaptadores certificados um a um |

## Feature Dependencies

```text
Modelo canônico + tenant
    └──> evidências e proveniência
          └──> provedores
                └──> cascata de enriquecimento
                      └──> cobrança por bloco

Jobs duráveis ──> chunks ──> retentativas ──> progresso/exportação
Supressão LGPD ─────────────────────────────> exportação e CRM
```

## MVP Definition

### Launch With (v1)

- [ ] API de saúde e configuração segura.
- [ ] Tenant interno e modelo canônico mínimo.
- [ ] Lotes persistentes com chunks e estados auditáveis.
- [ ] Importação e higienização determinística.
- [ ] Contrato de provedores e um provedor simulado para testes.
- [ ] Ledger de custo e cobrança sem duplicidade.
- [ ] Exportação CSV com evidências.

### Add After Validation (v1.x)

- [ ] OpenCNPJ/BigQuery, BigDataCorp e Apify reais.
- [ ] Appwrite Storage para entradas, resultados e evidências extensas.
- [ ] Primeiro conector CRM real.
- [ ] Dashboards operacionais e de margem.

### Future Consideration (v2+)

- [ ] Autenticação e RBAC para clientes externos.
- [ ] Portal de autoatendimento e cobrança automatizada.
- [ ] Conectores adicionais certificados.
- [ ] Revisão humana assistida para identidades ambíguas.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Jobs duráveis | HIGH | HIGH | P1 |
| Modelo de evidência | HIGH | HIGH | P1 |
| Higienização | HIGH | MEDIUM | P1 |
| Cascata de provedores | HIGH | HIGH | P1 |
| Billing ledger | HIGH | MEDIUM | P1 |
| CRM múltiplo | HIGH | HIGH | P2 |
| Portal com autenticação | MEDIUM | HIGH | P3 |

## Competitor Feature Analysis

| Feature | Plataformas generalistas | Ferramentas Brasil-first | Our Approach |
|---------|---------------------------|--------------------------|--------------|
| Cadastro empresarial | Cobertura brasileira irregular | Boa cobertura cadastral | OpenCNPJ/BigQuery verificável |
| Decisor | Nome e cargo sem vínculo forte | Cobertura variável | Vínculo temporal + evidência |
| WhatsApp | Frequentemente inferido | Nem sempre atribuído à pessoa | Estado específico, nunca presumido |
| Cobrança | Crédito por tentativa | Pacotes fechados | Evento por bloco entregue |

## Sources

- Contexto e restrições fornecidos pelo proprietário do LeadStream.
- Documentação oficial dos provedores selecionados na pesquisa anterior.
- Princípios de minimização, proveniência e idempotência aplicáveis ao domínio.

---
*Feature research for: LeadStream Backend*
*Researched: 2026-09-09*
