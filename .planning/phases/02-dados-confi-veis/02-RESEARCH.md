# Phase 2: Dados Confiáveis - Research

**Researched:** 2026-09-10
**Domain:** modelo canônico multi-tenant, proveniência, canonização e governança LGPD
**Confidence:** HIGH

<research_summary>
## Summary

A implementação deve separar identidade, valor observado e decisão canônica. `Entity` será a
raiz tenant-aware para empresa, estabelecimento e pessoa; contatos e perfis pertencem a uma
entidade explícita. `Observation` será append-only e guardará origem, método, estado, confiança,
tempo e valor normalizado. `CanonicalDecision` será igualmente versionada e apontará para a
observação vencedora, preservando conflitos e recanonizações.

O PostgreSQL deve reforçar invariantes que não podem depender apenas da API: unicidade por
tenant, integridade de CNPJ, limites de confiança, referências do mesmo tenant e bloqueio de
`UPDATE`/`DELETE` em observações. A aplicação acrescenta serviços transacionais e testes de
isolamento. RLS fica para o endurecimento da Fase 6, porque proprietários de tabela e papéis com
`BYPASSRLS` podem contorná-la e porque a variável de tenant por conexão precisa ser integrada ao
pool com cuidado.

**Primary recommendation:** domínio relacional normalizado, JSONB somente para payloads de valor
e metadados variáveis, seleção determinística sob lock e APIs internas sempre tenant-scoped.
</research_summary>

<model_design>
## Recommended Model Design

| Aggregate | Purpose | Critical invariants |
|-----------|---------|---------------------|
| `Entity` | raiz comum de empresa, estabelecimento e pessoa | `(tenant, kind, natural_key)` único; tenant imutável |
| `Company` | raiz jurídica de 8 dígitos | `cnpj_root` válido e único no tenant |
| `Establishment` | matriz/filial por CNPJ de 14 dígitos | CNPJ válido; raiz igual à empresa; único no tenant |
| `Person` | decisor sem exigir CPF | CPF completo nunca persistido; hash HMAC e máscara opcionais |
| `Relationship` | vínculo temporal pessoa–empresa | mesma tenant; validade coerente; cargo observado separado do papel inferido |
| `ContactPoint` | e-mail, telefone ou WhatsApp | valor original + normalizado; proprietário explícito; canal não é inferido por formato |
| `SocialProfile` | LinkedIn, Instagram, Facebook etc. | proprietário explícito; URL/handle normalizados |
| `Source` / `SourceRecord` | provedor e registro de origem | prioridade, identificador externo e finalidade/retention obrigatórios |
| `Evidence` | URL/identificador/trecho ou hash | minimização; instante de captura; integridade por fingerprint |
| `Observation` | fato, inferência, validação ou ausência | append-only; estado explícito; confiança 0–100; expiração |
| `Conflict` | valores concorrentes | campo/entidade explícitos; participantes preservados |
| `CanonicalDecision` | seleção versionada | aponta para observação elegível; versão monotônica; nunca relabela estado |
| `Suppression` | bloqueio de pessoa/domínio/e-mail/telefone | HMAC do valor + escopo; precedência absoluta; sem valor bruto |

`Entity.natural_key` deve usar chaves de domínio estáveis: raiz CNPJ para empresa, CNPJ completo
para estabelecimento e identificador HMAC/UUID para pessoa. A raiz comum evita uma GenericFK e
permite FKs reais de observações, contatos e perfis.
</model_design>

<implementation_guidance>
## Implementation Guidance

### Normalization and identity

- Implemente funções puras para CNPJ, e-mail, domínio e telefone, com testes de vetores válidos e
  inválidos. O validador de CNPJ deve verificar tamanho, repetição e dois dígitos verificadores.
- Serviços `create_*` recebem o tenant resolvido internamente e executam `transaction.atomic`.
- Rejeite referências cujo `entity.tenant_id` não seja o tenant da operação antes de gravar.
- Não exponha `tenant_id` em serializers de escrita.
- CPF completo pode existir apenas como valor transitório de integração; persista máscara e HMAC.

### Append-only evidence

- Sobrescreva `save()` para impedir alteração depois da inserção e `delete()` para bloquear
  remoção. Isso melhora a mensagem de erro, mas não substitui proteção de banco.
- Uma migration PostgreSQL cria função/trigger `BEFORE UPDATE OR DELETE` que lança exceção. Em
  SQLite a operação da migration é no-op para manter testes unitários rápidos.
- A alteração legítima é uma nova observação com `supersedes_id`, nunca mutação da anterior.
- Guarde `value_json` em JSONB e `value_fingerprint` SHA-256 de JSON canônico. Índice B-tree não
  ajuda buscas internas no JSONB; use GIN somente se surgir consulta justificada.

### Canonicalization

- Execute sob `select_for_update()` na entidade/campo e gere versão seguinte dentro da transação.
- Elegibilidade exclui `ABSENT`, `REJECTED`, `CONFLICTING`, expirados e suprimidos.
- Ordenação: peso do estado, prioridade da fonte, confiança, `observed_at`, UUID. O UUID torna o
  desempate repetível.
- A decisão guarda `policy_version`, `reason`, `selected_observation` e o estado original. Ela não
  copia o valor como um novo fato.
- Conflitos agrupam observações divergentes e permanecem abertos até uma decisão explícita.

### Privacy and retention

- `ProcessingPurpose` e `RetentionPolicy` são tenant-aware e referenciados pelo registro de origem.
- `Suppression` usa HMAC-SHA-256 com segredo de ambiente separado (`DATA_HASH_KEY`) e inclui o
  escopo no material autenticado.
- A rotação do HMAC deve aceitar chave atual e chaves anteriores durante uma janela controlada;
  nunca registrar as chaves.
- Expiração muda o estado operacional para stale/expired, sem apagar `Evidence`, `Observation` ou
  `CanonicalDecision`.

### API and tests

- DRF ViewSets/ListAPIView com filtros explícitos, paginação global e limite máximo conservador.
- Endpoints de escrita usam o tenant interno do serviço; campos sensíveis e `tenant_id` são
  read-only/ausentes.
- Testes locais podem usar SQLite para serviços puros. A CI deve definir `TEST_DATABASE_URL` para
  PostgreSQL e executar migrations, trigger append-only e concorrência no banco real.
</implementation_guidance>

<pitfalls>
## Common Pitfalls

- **Tenant transitivo sem validação:** uma FK pode ligar pessoa de um tenant a empresa de outro.
  Controle com serviços, constraints possíveis e testes negativos.
- **`wa.me` como confirmação:** URL montada a partir de celular é apenas representação; não muda o
  estado do canal WhatsApp.
- **MX como caixa postal válida:** MX comprova capacidade do domínio, não existência/posse da caixa.
- **Canonização por maior score apenas:** ignora estado, supressão, expiração e prioridade da fonte.
- **JSON para tudo:** perde constraints e índices essenciais. JSONB fica limitado a valores e
  metadados de observação.
- **RLS parcial:** ativar sem `FORCE ROW LEVEL SECURITY` e papéis mínimos pode dar falsa sensação de
  isolamento. O gate completo pertence à Fase 6.
</pitfalls>

<validation_architecture>
## Validation Architecture

| Layer | Checks |
|-------|--------|
| Unit | normalizadores, CNPJ, HMAC, ranking e estados elegíveis |
| Model/service | unicidade, tenant cruzado, validade temporal, ausência de CPF integral |
| API | contrato pt-BR, paginação, filtros, proibição de `tenant_id`, proveniência |
| PostgreSQL CI | migrations, trigger append-only, JSONB, constraints e transações concorrentes |
| Security | busca por segredos/CPF integral, payloads suprimidos e logs redigidos |

Nyquist sampling: cada requirement da fase possui ao menos um teste automático; trigger e lock
devem rodar obrigatoriamente em PostgreSQL na CI.
</validation_architecture>

<sources>
## Sources

- [Django 5.2 — model constraints](https://docs.djangoproject.com/en/5.2/ref/models/constraints/)
- [Django 5.2 — model fields and JSONField](https://docs.djangoproject.com/en/5.2/ref/models/fields/)
- [Django — database transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/)
- [PostgreSQL 17 — row security policies](https://www.postgresql.org/docs/17/ddl-rowsecurity.html)
- [PostgreSQL 17 — CREATE TRIGGER](https://www.postgresql.org/docs/17/sql-createtrigger.html)
- [PostgreSQL 17 — encryption options](https://www.postgresql.org/docs/17/encryption-options.html)
- [Django REST Framework — pagination](https://www.django-rest-framework.org/api-guide/pagination/)
- [ANPD — documentos e regulamentação](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos)
</sources>

---

*Phase: 02-dados-confi-veis*
*Research completed: 2026-09-10*
*Ready for planning: yes*
