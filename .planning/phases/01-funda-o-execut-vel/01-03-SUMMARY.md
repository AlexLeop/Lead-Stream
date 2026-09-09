---
phase: 01-funda-o-execut-vel
plan: "03"
subsystem: infra
tags: [celery, rabbitmq, redis, docker, easypanel, ci]
requires:
  - phase: 01-01
    provides: "Django, PostgreSQL, configuração fail-closed e tenant interno"
  - phase: 01-02
    provides: "Health checks, Appwrite opcional, OpenAPI e logs redigidos"
provides:
  - "Worker Celery com RabbitMQ, payload mínimo e Redis separado"
  - "Imagem ASGI não-root e topologia local API/worker/release"
  - "Gate único de qualidade, CI e runbook de EasyPanel"
affects: [dados, lotes, provedores, deploy, operacao]
tech-stack:
  added: [celery, rabbitmq, redis, docker, github-actions, gunicorn, uvicorn-worker]
  patterns: [explicit release migration, immutable shared image, private service network]
key-files:
  created:
    - src/config/celery.py
    - src/leadstream/common/tasks.py
    - Dockerfile
    - compose.yaml
    - scripts/quality.ps1
    - scripts/quality.sh
    - .github/workflows/ci.yml
    - deploy/easypanel.md
  modified:
    - src/config/settings/base.py
    - src/config/settings/production.py
    - .planning/phases/01-funda-o-execut-vel/01-USER-SETUP.md
key-decisions:
  - "API, worker e release usam a mesma imagem, mas migrations são uma execução explícita e única."
  - "RabbitMQ transporta somente IDs pequenos; Redis permanece dedicado a cache, locks e rate limits."
  - "A API sem login só pode ser publicada atrás de controle de acesso no gateway."
  - "HSTS de subdomínios e preload são opt-in para não bloquear serviços fora do domínio controlado."
patterns-established:
  - "Publicação segue quality → build imutável → release migrate → API → worker."
  - "Serviços de estado não publicam portas e recebem segredos apenas pelo cofre do EasyPanel."
requirements-completed: [FND-01, FND-02, FND-06, OPS-04]
duration: 16 min
completed: 2026-09-09
---

# Phase 1 Plan 3: Workers, containers e implantação Summary

**Worker durável, imagem ASGI não-root e fluxo reproduzível de qualidade e implantação no EasyPanel.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-09-09T20:12:25-03:00
- **Completed:** 2026-09-09T20:28:00-03:00
- **Tasks:** 3
- **Files modified:** 19

## Accomplishments

- Celery usa RabbitMQ com acknowledgement tardio, prefetch conservador e payload restrito a UUID.
- A mesma imagem não-root executa API, worker ou release com comandos separados e migrations controladas.
- Compose mantém PostgreSQL, RabbitMQ e Redis privados, persistentes e com health checks.
- Um único comando executa Ruff, mypy, drift de migrations, check de produção e 20 testes.
- CI aplica migrations e consulta prontidão/workspace em PostgreSQL real antes dos gates e do build.
- Runbook pt-BR documenta recursos iniciais da VPS, probes, rollback, proteção perimetral e rotação.

## Task Commits

1. **Task 1: Configurar Celery, RabbitMQ e Redis** - `1349fbb`
2. **Task 2: Criar imagem e topologia local** - `f4343bc`
3. **Task 3: Consolidar qualidade, CI e runbook EasyPanel** - `036733d`

## Files Created/Modified

- `src/config/celery.py` - aplicação Celery ligada à configuração Django.
- `src/leadstream/common/tasks.py` - tarefa smoke idempotente com contrato de UUID.
- `Dockerfile` - build reproduzível, runtime enxuto, usuário 10001 e health check.
- `compose.yaml` - topologia local privada com release sob profile explícito.
- `scripts/release.sh` - migrations e validação de produção fora do startup concorrente.
- `scripts/quality.ps1`, `scripts/quality.sh` - gates equivalentes para Windows e Linux.
- `.github/workflows/ci.yml` - PostgreSQL de integração, quality gate e build da imagem.
- `tests/test_production_settings.py` - regressão para ausência de variáveis e rejeição de SQLite.
- `deploy/easypanel.md` - procedimento completo de primeira implantação e rollback.
- `deploy/env.production.example` - checklist de variáveis sem valores reais.
- `README.md` - estado, arquitetura, execução, qualidade e implantação.

## Decisions Made

- RabbitMQ é o broker durável; Redis não acumula resultados de jobs e serve somente a necessidades efêmeras.
- API e worker compartilham artefato imutável, enquanto release é uma ação única antes do rollout.
- Os defaults do Compose são exclusivamente locais; produção deve falhar fechada e receber tudo pelo ambiente.
- O domínio sem autenticação do produto requer barreira perimetral antes de qualquer exposição pública.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Endurecimento completo do check de implantação**
- **Found during:** Task 3 (gate de qualidade)
- **Issue:** o primeiro check permitia alertas de CSRF, clickjacking e HSTS.
- **Fix:** adicionados os middlewares, HSTS conservador e falha do gate no nível `WARNING`; somente os avisos deliberados de subdomínios/preload são silenciados.
- **Files modified:** `src/config/settings/base.py`, `src/config/settings/production.py`, scripts de qualidade.
- **Verification:** `manage.py check --deploy --fail-level WARNING` passou sem alertas não tratados.
- **Committed in:** `036733d`

**2. [Rule 2 - Missing Critical] Regressão fail-closed e smoke PostgreSQL no CI**
- **Found during:** verificação adversarial da fase
- **Issue:** o comportamento fail-closed existia, mas não tinha teste de regressão; o CI aplicava migrations no PostgreSQL sem consultar as rotas reais.
- **Fix:** adicionados dois testes isolados de settings e smoke de `/health/ready` e `/api/v1/workspace/` sobre o PostgreSQL do CI.
- **Files modified:** `tests/test_production_settings.py`, `.github/workflows/ci.yml`.
- **Verification:** quality gate passou com 20 testes; comandos equivalentes passaram localmente.
- **Committed in:** `e662c74`

---

**Total deviations:** 2 auto-fixed (2 controles críticos ausentes). **Impact:** endurecimento e cobertura necessários, sem ampliar o escopo funcional.

## Issues Encountered

- O cliente Docker e o Compose estão instalados, mas o daemon local não respondeu dentro do limite seguro. A configuração Compose passou; o build real permanece coberto pela CI e deve ser repetido quando o Docker Desktop estiver operacional.

## User Setup Required

**Serviços externos exigem configuração manual.** Consulte `01-USER-SETUP.md` para:

- revogar as credenciais compartilhadas anteriormente;
- cadastrar URLs e segredos no cofre do EasyPanel;
- criar RabbitMQ e Redis privados;
- proteger o domínio no gateway e executar o release inicial.

## Next Phase Readiness

- A fundação está pronta para receber o modelo canônico de empresa, pessoa, vínculo, contato e evidência na Fase 2.
- O deploy real depende da rotação das credenciais e acesso ao EasyPanel; isso não bloqueia desenvolvimento e testes locais.

## Self-Check: PASSED

- Ruff, mypy, migration check, check de produção e 20 testes passaram.
- `docker compose config --quiet` passou e nenhum marcador das credenciais reais foi encontrado.
- Dockerfile declara usuário não-root e health check; o build local ficou indisponível pelo daemon, não por erro detectado no projeto.

---
*Phase: 01-funda-o-execut-vel*
*Completed: 2026-09-09*
