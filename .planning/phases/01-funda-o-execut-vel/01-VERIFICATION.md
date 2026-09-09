---
phase: 01-funda-o-execut-vel
verified: 2026-09-09T20:39:00-03:00
status: human_needed
score: 13/14 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Executar release e subir a stack completa por containers"
    expected: "Release termina sem erro; API e worker permanecem saudáveis; live, ready, workspace e docs respondem conforme o contrato."
    why_human: "O daemon Docker desta máquina não inicia porque não há distribuição WSL disponível; a composição foi validada apenas estaticamente."
  - test: "Publicar a mesma tag no EasyPanel com credenciais rotacionadas e gateway privado"
    expected: "Readiness retorna 200, dependências reais ficam saudáveis ou explicitamente degradadas, e nenhuma porta/credencial interna fica exposta."
    why_human: "Exige acesso ao painel, nova chave Appwrite, serviços reais e domínio protegido que não estão disponíveis no ambiente de verificação."
---

# Phase 1: Fundação Executável Verification Report

**Phase Goal:** As an internal operator, I want to start an independent Django API securely connected to its infrastructure, so that I have a deployable and observable foundation for LeadStream.
**Verified:** 2026-09-09T20:39:00-03:00
**Status:** human_needed
**Re-verification:** No — initial verification

## User Flow Coverage

| Step | Expected | Evidence | Status |
|---|---|---|---|
| Preparar | Configurar somente variáveis e segredos externos | `production.py` falha sem valores; exemplos contêm placeholders | ✓ |
| Liberar banco | Executar migrations uma única vez | `release` usa profile explícito e chama `scripts/release.sh` | ✓ |
| Iniciar | Subir API, worker e dependências | Topologia Compose válida; daemon local indisponível | ? HUMANO |
| Observar | Consultar vida, prontidão, dependências e OpenAPI | Rotas reais testadas por Django Client | ✓ |
| Resultado | Obter fundação implantável e observável | Código, testes e runbook convergem; falta smoke do container/infra real | ? HUMANO |

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | Operador inicia API e dependências por containers e obtém probes reais | ? UNCERTAIN | Compose renderiza seis serviços e probes, mas o daemon local não pôde executar a imagem. |
| 2 | Migration cria tenant interno estável e a API o aplica automaticamente | ✓ VERIFIED | `0002_seed_internal_tenant.py` usa `get_or_create`; workspace consulta `get_internal_tenant`; teste lê o ORM. |
| 3 | Appwrite é verificável por adaptador sem participar do ORM | ✓ VERIFIED | `integrations/appwrite.py` lê ambiente e é chamado por `check_appwrite`; nenhuma migration/model importa Appwrite. |
| 4 | OpenAPI descreve `/api/v1` e logs correlacionados não expõem segredos | ✓ VERIFIED | Schema contém workspace/health; testes de request ID e redação cobrem segredo, token, e-mail e telefone. |
| 5 | Um comando bloqueia lint, tipos, drift de migrations, alertas de produção e testes | ✓ VERIFIED | `scripts/quality.ps1` executado: todos os gates e 20 testes passaram. |
| 6 | Produção rejeita variáveis ausentes e banco não PostgreSQL | ✓ VERIFIED | Spot-check e `tests/test_production_settings.py` cobrem ausência e SQLite. |
| 7 | Workspace lê o tenant do banco, em pt-BR e sem login | ✓ VERIFIED | `WorkspaceView` chama o serviço/ORM e retorna `nome`, `ativo`; dois testes retornam 200 sem token. |
| 8 | Liveness não faz I/O e readiness depende apenas do banco/migration | ✓ VERIFIED | `live` é constante; `ready` chama somente `check_database`; testes verificam não chamadas e erro 503 sanitizado. |
| 9 | Redis, RabbitMQ e Appwrite têm diagnósticos independentes e sanitizados | ✓ VERIFIED | `check_dependencies` retorna somente estado; falhas são capturadas e não incluem hosts/exceções. |
| 10 | Toda requisição recebe ID e logging redige valores sensíveis recursivamente | ✓ VERIFIED | Middleware liga e devolve `X-Request-ID`; redactor percorre mapas/coleções; testes exercitam ambos. |
| 11 | OpenAPI versionado permite executar a rota real do workspace | ✓ VERIFIED | URLs sob `/api/v1`; teste confirma schema, Swagger e os paths reais. |
| 12 | API, worker, broker, cache e banco são separados; fila aceita somente UUID | ✓ VERIFIED | Compose separa serviços; Celery restringe JSON/prefetch; `smoke_task` rejeita dict/list/texto não UUID. |
| 13 | A imagem não executa migrations no startup concorrente e roda sem root | ✓ VERIFIED | Dockerfile usa UID/GID 10001; API/worker não chamam migrate; release é isolado por profile. |
| 14 | EasyPanel pode ser configurado sem gravar credenciais | ✓ VERIFIED | Runbook, exemplo de ambiente e checklist usam placeholders; busca por marcadores reais retornou zero. |

**Score:** 13/14 truths verified; a verdade restante exige execução em ambiente com containers.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/config/settings/production.py` | Configuração fail-closed | ✓ VERIFIED | Exige segredo/hosts/PostgreSQL/broker/Redis e endurece HTTPS/cookies/HSTS. |
| `src/leadstream/tenancy/models.py` | Tenant e base tenant-owned | ✓ VERIFIED | Slug único/imutável e FK abstrata obrigatória/indexada. |
| `src/leadstream/tenancy/migrations/0002_seed_internal_tenant.py` | Seed idempotente | ✓ VERIFIED | ID determinístico e `get_or_create` histórico. |
| `src/leadstream/common/health.py` | Probes separados | ✓ VERIFIED | Banco/migration, Redis, RabbitMQ e Appwrite possuem contratos próprios. |
| `src/leadstream/integrations/appwrite.py` | Porta Appwrite | ✓ VERIFIED | Configuração somente do ambiente, timeout e erro sanitizado. |
| `src/leadstream/common/logging.py` | Logging JSON redigido | ✓ VERIFIED | Processadores reais, redação recursiva e JSON renderer. |
| `src/config/celery.py` | Worker configurado | ✓ VERIFIED | Carrega namespace Celery do Django e descobre tarefa. |
| `Dockerfile` | Imagem ASGI não-root | ✓ STATIC | Substantivo e conectado ao Compose; build runtime aguarda ambiente Docker. |
| `compose.yaml` | Topologia equivalente | ✓ VERIFIED | `docker compose --profile release config --services` listou os seis serviços. |
| `.github/workflows/ci.yml` | Gate automatizado | ✓ VERIFIED | PostgreSQL, smoke HTTP, quality e build Docker em ordem. |
| `deploy/easypanel.md` | Runbook operacional | ✓ VERIFIED | Rede privada, sizing, release, probes, rotação e rollback. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| settings | PostgreSQL | `DATABASE_URL` + `dj_database_url` | ✓ WIRED | Produção rejeita engine diferente de PostgreSQL. |
| workspace view | tenant service/ORM | `get_internal_tenant` | ✓ WIRED | Resultado persistido é serializado na resposta. |
| health views | health services | `check_database` / `check_dependencies` | ✓ WIRED | Testes exercitam sucesso e falha. |
| Appwrite adapter | environment | `APPWRITE_*` | ✓ WIRED | Factory só é criado com três valores presentes. |
| Compose | Dockerfile | mesma imagem para API/worker/release | ✓ WIRED | Anchor `app-service` compartilha build e imagem. |
| Dockerfile | liveness | `HEALTHCHECK /health/live` | ✓ WIRED | Rota existe e não depende de infraestrutura. |
| CI | quality/build | `scripts/quality.sh` antes de `docker build` | ✓ WIRED | Ordem explícita no workflow. |

### Data-Flow Trace (Level 4)

| Artifact | Data | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `/api/v1/workspace/` | tenant interno | Migration → ORM → service → serializer | Sim | ✓ FLOWING |
| `/health/ready` | disponibilidade operacional | `SELECT 1` + `MigrationRecorder` | Sim | ✓ FLOWING |
| `/health/dependencies` | estado por dependência | Redis ping, broker connection, Appwrite HTTP | Sim quando configurado | ✓ FLOWING |
| tarefa Celery | ID de referência | mensagem JSON com UUID | Sim, sem payload de lead | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Produção falha sem segredo | importar settings com ambiente limpo | processo não zero em `DJANGO_SECRET_KEY` | ✓ PASS |
| Produção rejeita SQLite | importar settings com URL SQLite sentinela | processo não zero em `DATABASE_URL`/PostgreSQL | ✓ PASS |
| Contratos da API e falhas | `pytest -q` | 20 passed | ✓ PASS |
| Drift de migrations | `manage.py makemigrations --check --dry-run` | No changes detected | ✓ PASS |
| Topologia completa | `docker compose --profile release config --services` | postgres, rabbitmq, redis, release, worker, api | ✓ PASS |
| Build/health em container | `docker build` / smoke | daemon sem WSL disponível | ? HUMAN |

### Probe Execution

Nenhum script `probe-*` foi declarado. Os probes HTTP estão cobertos por testes Django; a
execução do health check dentro do container foi encaminhada à verificação humana.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| FND-01 | 01-02, 01-03 | ✓ SATISFIED | Semântica e testes de live/ready/dependencies. |
| FND-02 | 01-01, 01-03 | ✓ SATISFIED | Ambiente fail-closed, redação e busca sem credenciais. |
| FND-03 | 01-01 | ✓ SATISFIED | PostgreSQL obrigatório em produção e migrations reproduzíveis. |
| FND-04 | 01-01 | ✓ SATISFIED | Tenant e base abstrata com vínculo obrigatório. |
| FND-05 | 01-02 | ✓ SATISFIED | Adapter Appwrite isolado do ORM. |
| FND-06 | 01-03 | ? NEEDS HUMAN | Topologia/runbook completos; execução real aguarda Docker/EasyPanel. |
| FND-07 | 01-01, 01-02 | ✓ SATISFIED | API v1/OpenAPI e respostas em pt-BR. |
| OPS-01 | 01-02 | ✓ SATISFIED | Contexto estruturado e redação testada. |
| OPS-04 | 01-03 | ✓ SATISFIED | Quality scripts e CI antes do build. |

Todos os nove requisitos da fase aparecem em pelo menos um plano; não há requisito órfão.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `tests/test_health.py` | 23 | Readiness automatizada usa SQLite em memória | ℹ️ Info | O CI agora aplica migrations e consulta readiness/workspace em PostgreSQL real; o container ainda requer smoke. |

Nenhum `TODO`, `FIXME`, `XXX`, `HACK`, placeholder executável ou implementação vazia foi encontrado nos arquivos da fase.

### Human Verification Required

#### 1. Stack completa por containers

**Test:** executar o serviço `release`, subir API/worker/dependências e consultar live, ready,
workspace e docs.
**Expected:** release termina sem erro; processos permanecem saudáveis; todas as rotas retornam
o contrato documentado.
**Why human:** o Docker Desktop local não possui distribuição WSL e o daemon não respondeu.

#### 2. EasyPanel e dependências reais

**Test:** publicar uma tag imutável usando o runbook, credenciais já rotacionadas e gateway
privado; consultar `/health/dependencies`.
**Expected:** PostgreSQL/readiness saudável; Redis, RabbitMQ e Appwrite informam estado real sem
expor segredo; somente a API fica acessível atrás do gateway.
**Why human:** exige acesso e configuração dos serviços externos de produção.

### Gaps Summary

Não foi encontrado gap de implementação. A fase permanece pendente exclusivamente pelos dois
smokes de ambiente acima; recursos funcionais de leads, lotes, provedores e CRMs pertencem às
Fases 2–5 e não foram tratados como lacunas desta fundação.

---

_Verified: 2026-09-09T20:39:00-03:00_
_Verifier: Codex (gsd-verifier inline)_
