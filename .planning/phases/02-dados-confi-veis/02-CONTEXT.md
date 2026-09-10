# Phase 2: Dados Confiáveis - Context

**Gathered:** 2026-09-09
**Status:** Ready for planning
**Source:** contrato canônico fornecido pelo proprietário + correção explícita para produção real

<domain>
## Phase Boundary

Esta fase entrega o núcleo relacional de produção para representar empresa brasileira,
estabelecimento, pessoa, vínculo, contato, perfil social, fonte, evidência, observação,
seleção canônica, conflito, finalidade de tratamento, retenção e supressão. Ela também expõe
APIs internas para registrar e consultar essas entidades sob o tenant `internal`.

Provedores reais, descoberta, execução em lote, cobrança, exportação e sincronização CRM não
entram nesta fase; eles consumirão este domínio nas fases seguintes.

</domain>

<decisions>
## Implementation Decisions

### Identidade e organização empresarial

- **D-01:** `Company` representa a raiz jurídica de oito dígitos; `Establishment` representa o CNPJ completo de 14 dígitos e identifica matriz ou filial.
- **D-02:** CNPJ é normalizado e validado por dígitos verificadores antes da persistência. A unicidade é por tenant, nunca global entre clientes.
- **D-03:** Uma entidade-registro comum fornece UUID, tenant, tipo e chave natural; observações apontam a essa entidade por FK, evitando referências polimórficas órfãs.
- **D-04:** Pessoa física não depende de CPF completo. Quando houver CPF, somente valor mascarado e hash não reversível podem ser persistidos; homônimos permanecem entidades distintas até correlação comprovada.
- **D-05:** Vínculo pessoa–empresa possui validade temporal, qualificação legal, cargo declarado/normalizado, senioridade e papel de compra; inferência comercial não sobrescreve o cargo observado.

### Contatos e perfis

- **D-06:** E-mail, telefone e canal WhatsApp são registros distintos. Ser celular ou possuir link `wa.me` não confirma WhatsApp.
- **D-07:** Perfis LinkedIn, Instagram, Facebook e outras redes pertencem explicitamente a uma pessoa, empresa ou estabelecimento por referência de entidade.
- **D-08:** Valores originais e normalizados são preservados. Normalização técnica não eleva sozinha o vínculo entre um contato e um decisor.
- **D-09:** DNS/MX valida o domínio, não a existência da caixa postal. Cada capacidade técnica possui campo e evidência próprios.

### Evidência append-only e canonização

- **D-10:** Estados canônicos são `ABSENT`, `OBSERVED`, `INFERRED`, `TECHNICALLY_VALIDATED`, `CONFIRMED`, `CONFLICTING` e `REJECTED`.
- **D-11:** Toda observação registra fonte, registro de origem, URL/identificador, instante de captura/observação, método, trecho ou hash, confiança de 0 a 100, expiração e finalidade de tratamento.
- **D-12:** Observações são append-only na aplicação e por trigger PostgreSQL; correções criam nova observação, nunca editam a anterior.
- **D-13:** Valor canônico é uma decisão versionada que aponta para uma observação existente. A decisão não copia ou transforma inferência em fato.
- **D-14:** Política determinística ordena primeiro elegibilidade do estado, depois prioridade da fonte, confiança, atualidade e UUID como desempate estável.
- **D-15:** `ABSENT`, `REJECTED` e `CONFLICTING` nunca são promovidos. `INFERRED` pode ser selecionado apenas como inferência e jamais devolvido com rótulo superior.
- **D-16:** Valores concorrentes permanecem ligados a um conflito explícito; recanonização adiciona uma nova decisão com versão de política e preserva toda decisão anterior.

### Privacidade, retenção e supressão

- **D-17:** Todo registro de origem possui finalidade profissional, base operacional/documentada e política de retenção.
- **D-18:** Supressão armazena hash HMAC do valor normalizado e escopo (pessoa, domínio, e-mail ou telefone), evitando manter o dado pessoal bruto apenas para bloqueá-lo.
- **D-19:** Supressão prevalece sobre canonização, exportação e integrações futuras. Nenhum replay pode reativar um valor suprimido.
- **D-20:** Expiração marca dados operacionais como `STALE`/`EXPIRED` sem apagar observações, evidências ou decisões necessárias à auditoria.
- **D-21:** Dados e decisões retornados pela API carregam proveniência e estado; ausência deve ser explícita, não substituída por valor inventado.

### Tenant e operação interna

- **D-22:** Todas as tabelas de negócio têm vínculo obrigatório e indexado com tenant, diretamente ou por entidade-raiz, e serviços rejeitam referências cruzadas entre tenants.
- **D-23:** A API continua sem login por decisão do proprietário e aplica automaticamente o tenant `internal`; nenhum endpoint aceita `tenant_id` arbitrário do cliente.
- **D-24:** Operações compostas usam `transaction.atomic`, locks de linha quando houver decisão concorrente e constraints/indexes no banco para invariantes de identidade.
- **D-25:** PostgreSQL é o contrato produtivo. Testes rápidos podem usar SQLite apenas onde a semântica não depende de recursos PostgreSQL; CI cobre migrations e caminhos críticos em PostgreSQL.

### Supersessões do documento de origem

- A menção anterior a SQLite/pg-boss/Node não rege este backend: PostgreSQL, Django e Celery são decisões atuais.
- Geração de link `wa.me` não equivale a confirmação de canal.
- Validação MX/SPF/DMARC não equivale a validação da caixa postal.
- Campos bancários, fiscais, tecnológicos e jurídicos permanecem no contrato futuro, mas seus provedores e payloads entram nas Fases 4–5.

### the agent's Discretion

- Nomes finais das tabelas, serializers, managers, paginação e composição exata dos serviços.
- Estratégia de hash/HMAC e formato de fingerprint, desde que determinísticos, não reversíveis e configurados por ambiente.
- Índices adicionais guiados pelas consultas previstas, sem armazenar duplicações desnecessárias.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Produto e produção

- `.planning/PROJECT.md` — produto, volume, infraestrutura, privacidade e definição de produção.
- `.planning/REQUIREMENTS.md` — DATA-01–DATA-06 e COMP-01–COMP-03.
- `.planning/ROADMAP.md` — fronteira e critérios da Fase 2 e gate final de produção.

### Fundação já implementada

- `.planning/phases/01-funda-o-execut-vel/01-CONTEXT.md` — decisões de tenant, banco, acesso interno e configuração.
- `.planning/phases/01-funda-o-execut-vel/01-VERIFICATION.md` — evidência real e pendências de infraestrutura.
- `src/leadstream/tenancy/models.py` — Tenant e base abstrata existentes.
- `src/leadstream/tenancy/services.py` — resolução automática do tenant interno.
- `src/config/settings/production.py` — contrato fail-closed de produção.

### Especificação fornecida

- Contrato Canônico de Dados, Arquitetura de Entrega & Stack Oficial: LeadStream v1 — taxonomia, entidades, campos e DTO consolidado fornecidos na conversa.

</canonical_refs>

<specifics>
## Specific Ideas

- A API e a documentação continuam em português do Brasil.
- O formato de saída deve permitir reconstruir o JSON consolidado discutido, sem criar uma tabela plana monolítica.
- Contato de departamento/empresa nunca pode ser apresentado como contato de decisor.
- Ausência, inferência, validação técnica, confirmação e conflito precisam ser distinguíveis pelo consumidor sem consultar documentação externa.
- A modelagem deve aceitar futuras fontes BigQuery, BigDataCorp, Apify e Open Enrich sem acoplá-las ao domínio.

</specifics>

<deferred>
## Deferred Ideas

- Importação CSV, chunks, retries e cobrança: Fase 3.
- Execução de provedores, busca e orçamento: Fase 4.
- DTO consolidado de exportação, Appwrite Storage e CRMs: Fase 5.
- RLS, scans, carga, chaos, backup/restore e aceite final: Fase 6.

</deferred>

---

*Phase: 02-dados-confi-veis*
*Context gathered: 2026-09-09 via supplied canonical contract*
