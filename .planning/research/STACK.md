# Stack Research

**Domain:** plataforma B2B de higienização e enriquecimento de leads em lote
**Researched:** 2026-09-09
**Confidence:** HIGH

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

As dependências devem ser declaradas em `pyproject.toml` e congeladas por `uv.lock`; ambientes de produção instalam pelo lockfile.

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

**Uso interno inicial:** tenant padrão, autenticação de usuário desabilitada e proteção no gateway.

**Clientes externos:** autenticação e autorização plugáveis, isolamento por tenant e políticas no banco antes de liberar acesso.

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

---
*Stack research for: LeadStream Backend*
*Researched: 2026-09-09*
