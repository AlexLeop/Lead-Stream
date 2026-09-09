# Phase 1: Fundação Executável - Context

**Gathered:** 2026-09-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Esta fase entrega o novo backend Django executável e independente: configuração segura, PostgreSQL, tenant interno, API versionada, health checks, integração Appwrite desacoplada, observabilidade básica, containers e gates de qualidade. Modelos completos de leads, jobs em lote e provedores de enriquecimento pertencem às fases seguintes.

</domain>

<decisions>
## Implementation Decisions

### Topologia de serviços
- **D-01:** A primeira implantação terá processos separados para API Django/ASGI, worker Celery e broker RabbitMQ; PostgreSQL será a fonte de verdade e Redis atenderá cache/locks/rate limits.
- **D-02:** Mensagens da fila carregam IDs pequenos, nunca CSVs ou payloads extensos.
- **D-03:** Appwrite entra por uma porta de storage/serviços e não participa dos models ou migrations do Django.
- **D-04:** Desenvolvimento local pode usar containers próprios; produção usa o PostgreSQL já criado na rede interna do EasyPanel.

### Tenant e acesso interno
- **D-05:** Toda tabela de negócio criada nesta e nas próximas fases inclui tenant; o tenant `internal` é provisionado e aplicado automaticamente no v1.
- **D-06:** Não haverá cadastro, login, sessão de usuário ou RBAC nesta fase.
- **D-07:** A API deve assumir que o perímetro do EasyPanel/gateway impede acesso público irrestrito; um token técnico de gateway pode ser adicionado sem criar autenticação de produto.

### Saúde e prontidão
- **D-08:** `/health/live` indica somente que o processo está respondendo e nunca depende de serviços externos.
- **D-09:** `/health/ready` bloqueia quando PostgreSQL ou migrations essenciais não estão disponíveis.
- **D-10:** Broker, Redis e Appwrite possuem checks diagnósticos separados; Appwrite ausente não impede que a API básica fique pronta.
- **D-11:** Respostas de health não expõem hostnames, usuários, senhas, tokens ou traces.

### Deploy, configuração e segredos
- **D-12:** Configuração é validada na inicialização, com defaults apenas para desenvolvimento; produção falha fechada se segredo ou host obrigatório estiver ausente.
- **D-13:** Credenciais reais não serão copiadas da conversa nem gravadas em qualquer arquivo do repositório.
- **D-14:** `.env.example` terá placeholders seguros; EasyPanel fornece os valores reais.
- **D-15:** Migrations serão executadas como release command explícito antes de liberar a nova imagem, não por todos os processos concorrentes no startup.
- **D-16:** Containers executam como usuário não-root, têm health checks e limites documentados.
- **D-17:** Dependências são declaradas em `pyproject.toml`, com lockfile quando a ferramenta estiver disponível; Ruff, mypy, migrations check e pytest formam o gate.

### the agent's Discretion
- Nomes internos de pacotes, organização exata de settings, biblioteca de logging e detalhes do formato de erro podem seguir padrões maduros do ecossistema, desde que mantenham os contratos acima.
- Valores de timeout e pool podem começar conservadores e permanecer configuráveis por ambiente.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Produto e escopo
- `.planning/PROJECT.md` — valor central, limites, contexto de infraestrutura e decisões de arquitetura.
- `.planning/REQUIREMENTS.md` — requisitos FND-01–FND-07, OPS-01 e OPS-04 desta fase.
- `.planning/ROADMAP.md` — fronteira, critérios observáveis e sequência da Fase 1.

### Pesquisa técnica
- `.planning/research/STACK.md` — versões, dependências recomendadas e tecnologias proibidas.
- `.planning/research/ARCHITECTURE.md` — componentes, limites internos e fluxo de implantação.
- `.planning/research/PITFALLS.md` — riscos de segredos, Appwrite como ORM e jobs frágeis.
- `.planning/research/SUMMARY.md` — síntese e implicações para a primeira fase.

No external specs or ADRs were supplied; requirements are captured in the project planning artifacts above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Nenhum código de aplicação existe no novo repositório; a fundação será criada do zero.
- O projeto LeadStream anterior é apenas referência de domínio e não deve ser importado, editado ou acoplado.

### Established Patterns
- Planejamento usa GSD com commits atômicos e verificação por fase.
- Python/Django, PostgreSQL nativo e adaptadores externos são decisões já bloqueadas.

### Integration Points
- PostgreSQL será configurado por `DATABASE_URL` no EasyPanel.
- Appwrite será configurado por endpoint, Project ID e secret exclusivamente no ambiente.
- API futura consumirá `/api/v1`; não há integração com frontend nesta fase.

</code_context>

<specifics>
## Specific Ideas

- O hostname PostgreSQL informado pertence à rede interna do EasyPanel; desenvolvimento local precisa de URL distinta.
- A instância Appwrite é self-hosted e está acessível por endpoint HTTPS próprio.
- As credenciais anteriormente compartilhadas devem ser rotacionadas antes do deploy produtivo.
- Mensagens e documentação operacional devem estar em português do Brasil.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-funda-o-execut-vel*
*Context gathered: 2026-09-09*
