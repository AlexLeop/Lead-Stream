<!-- GSD:project-start source:PROJECT.md -->
## Project

**LeadStream Backend**

LeadStream Backend é o novo núcleo independente e Brasil-first para extração, higienização e enriquecimento de leads empresariais. A API parte de uma empresa brasileira real, resolve seus decisores, encontra contatos e perfis públicos atribuíveis a essas pessoas e registra evidência, confiança, atualização, custo e cobrança por bloco efetivamente entregue.

O primeiro marco será usado internamente pelo proprietário e processará lotes de até 100 mil empresas sem modificar ou depender do backend atual. O desenho nasce preparado para múltiplos clientes e CRMs, mas sem autenticação de usuários na primeira versão.

**Core Value:** Entregar somente dados úteis atribuíveis à empresa ou ao decisor correto, com proveniência suficiente para distinguir fato, validação, inferência e ausência de dado.

### Constraints

- **Stack**: Python 3.13, Django 5.2 LTS, Django REST Framework, PostgreSQL, Celery, RabbitMQ, Redis, Polars e DuckDB.
- **Compatibilidade**: API versionada e contrato estável para permitir conexão posterior do frontend existente.
- **Capacidade**: a VPS coordena API e workers; arquivos brutos, exports extensos e snapshots ficam em object storage.
- **Volume**: um lote de 100 mil entradas precisa sobreviver a reinícios, timeouts e indisponibilidades externas.
- **Qualidade**: todo valor exportável deve possuir origem, instante, método, estado de evidência e confiança.
- **Privacidade**: dados pessoais exigem finalidade profissional, minimização, retenção, supressão e trilha de auditoria.
- **Custo**: cada chamada externa deve respeitar orçamento por job e custo máximo configurável por lead útil.
- **Segurança**: nenhum segredo pode ser versionado; a API interna deve permanecer protegida pelo perímetro do EasyPanel ou gateway.
- **Idioma**: mensagens, documentação operacional e exportações devem usar português do Brasil.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.13 | Runtime | Compatível com Django 5.2 e Celery, com ecossistema forte para dados |
| Django | 5.2 LTS | Domínio, ORM, migrações e administração | Suporte estendido até abril de 2028 e base madura para regras complexas |
| Django REST Framework | 3.18.x | API REST | Serialização, paginação, filtros e políticas consolidadas |
| PostgreSQL | 17+ | Fonte operacional de verdade | Transações, índices, JSONB, constraints e consultas relacionais |
| Celery | 5.6.x | Processamento assíncrono | Retentativas, roteamento, time limits e integração madura com Django |
| RabbitMQ | 4.x | Broker durável | Adequado a filas confiáveis e monitoráveis |
| Redis | 8.x | Cache, locks e rate limits | Operações atômicas e baixa latência para coordenação |
| Appwrite Python SDK | major atual compatível | Storage e serviços complementares | Aproveita a infraestrutura já provisionada sem substituir o ORM |
### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| psycopg | 3.x | Driver PostgreSQL | Todas as conexões do Django ao banco operacional |
| django-filter | 25.x | Filtros declarativos | Endpoints de empresas, pessoas, lotes e faturamento |
| drf-spectacular | 0.28+ | OpenAPI 3 | Contrato e documentação da API |
| pydantic | 2.x | Contratos de provedores | Validar respostas externas fora da camada HTTP |
| httpx | 0.28+ | Cliente HTTP | Adaptadores de BigDataCorp, Apify, Appwrite e demais fontes |
| tenacity | 9.x | Retentativas locais | Apenas em operações idempotentes e com política explícita |
| polars | 1.x | Transformações colunares | Normalização e higienização de CSV/Parquet |
| duckdb | 1.x | Consulta analítica local | Cruzamentos em arquivos sem carregá-los no PostgreSQL |
| structlog | 25.x | Logs estruturados | Correlação por tenant, job, chunk e provedor |
| prometheus-client | 0.x | Métricas | Custos, latência, filas, erros e taxa de acerto |
| pytest | 8+ | Testes | Unidade, integração e contratos de provedores |
| pytest-django | 4.x | Testes Django | Banco, API e transações |
### Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Dependências e lockfile | Builds reprodutíveis e rápidos |
| Ruff | Lint e formatação | Gate único para estilo e erros comuns |
| mypy + django-stubs | Tipos | Aplicar primeiro nos limites do domínio e provedores |
| Docker Compose | Ambiente local | PostgreSQL, RabbitMQ e Redis sem depender do EasyPanel |
| Flower | Operação Celery | Monitoramento interno, nunca público sem proteção |
## Installation
## Alternatives Considered
| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Django REST Framework | FastAPI | Microserviço isolado intensivo em I/O, sem necessidade do domínio Django |
| RabbitMQ | Redis como broker | MVP muito simples; migrar quando durabilidade e roteamento forem críticos |
| PostgreSQL | Appwrite TablesDB | Aplicação orientada diretamente ao SDK Appwrite e sem ORM Django |
| Polars/DuckDB | pandas | Manipulações pequenas e compatibilidade com bibliotecas legadas |
## What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| SQLite em produção | Escritas concorrentes, jobs e auditoria excedem seu perfil operacional | PostgreSQL |
| Appwrite TablesDB como ORM do Django | Impede migrações e relações nativas e adiciona round-trip HTTP | PostgreSQL + adaptador Appwrite |
| Uma tarefa Celery por lead | 100 mil mensagens aumentam overhead e dificultam orçamento | Chunks idempotentes de 25–100 leads |
| Segredos em `.env.example` | Exposição permanente em Git | Placeholders e secrets do EasyPanel |
| ORM linha a linha em importações | Latência e memória crescem rapidamente | Polars/DuckDB + bulk insert |
## Stack Patterns by Variant
## Version Compatibility
| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Django 5.2 LTS | Python 3.10–3.14 | Usar Python 3.13 no primeiro deploy |
| DRF 3.18.x | Django 5.2+ | Fixar minor e aceitar apenas patches testados |
| Celery 5.6.x | RabbitMQ e Redis | RabbitMQ como broker; estado de negócio permanece no PostgreSQL |
## Sources
- https://www.djangoproject.com/download/ — suporte do Django 5.2 LTS
- https://docs.djangoproject.com/en/5.2/releases/5.2/ — compatibilidade com Python
- https://www.django-rest-framework.org/community/release-notes/ — DRF 3.18
- https://docs.celeryq.dev/en/stable/ — Celery 5.6, brokers, retries e rate limits
- https://appwrite.io/docs/products/databases — tipos de banco Appwrite
- https://appwrite.io/docs/quick-starts/python — SDK server-side Python
- https://docs.pola.rs/ — processamento colunar
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
