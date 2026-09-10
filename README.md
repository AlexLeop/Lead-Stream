# LeadStream Backend

Novo backend Brasil-first, separado do protótipo original, para higienização e enriquecimento
de leads com evidência, rastreabilidade de custo e processamento assíncrono.

> Estado atual: a Fase 1 entrega somente a fundação executável e implantável. Descoberta,
> higienização, enriquecimento, conectores de CRM e cobrança entram nas fases seguintes. A meta
> deste repositório é produção real, mas nenhum release será classificado como pronto para dados
> reais antes de concluir os seis gates e emitir o relatório de aceite de produção sem bloqueios.

## Fundação entregue

- Django REST Framework com contrato OpenAPI em `/api/v1/schema/` e interface em `/api/v1/docs/`;
- PostgreSQL como fonte canônica e um tenant interno provisionado por migration;
- Celery com RabbitMQ para jobs e Redis para cache/coordenação;
- health checks separados para vida, prontidão e dependências;
- logs JSON com `request_id` e remoção de segredos e contatos sensíveis;
- adapter Appwrite isolado, opcional e sem papel de banco principal;
- imagem não-root, Docker Compose local e runbook para EasyPanel;
- gates reproduzíveis de tipos, lint, migrations, segurança e testes.

## Arquitetura desta fase

```text
gateway privado -> API Django/DRF -> PostgreSQL
                         |          Redis
                         +--------> RabbitMQ -> worker Celery
                         +--------> Appwrite (dependência complementar)
```

A aplicação não possui login por decisão de escopo. Em produção, proteja o domínio no gateway
com allowlist, VPN ou Cloudflare Access.

## Executar localmente com Docker

Crie um `.env` a partir de `.env.example`, usando apenas valores de desenvolvimento. Em seguida:

```bash
docker compose --profile release run --rm release
docker compose up -d api worker
```

A API estará disponível somente em `http://127.0.0.1:8000`. Consulte:

- `http://127.0.0.1:8000/health/live`
- `http://127.0.0.1:8000/health/ready`
- `http://127.0.0.1:8000/api/v1/docs/`

## Executar sem Docker

Requer Python 3.13, PostgreSQL, RabbitMQ e Redis:

```bash
uv sync --extra dev
uv run python manage.py migrate
uv run python manage.py runserver
```

Em outro terminal:

```bash
uv run celery -A config.celery:app worker --loglevel=INFO --concurrency=2
```

## Qualidade

No Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/quality.ps1
```

No Linux/CI:

```bash
sh scripts/quality.sh
```

O pipeline valida lint, tipos, migrations pendentes, configuração de produção, testes e build
da imagem. Testes automatizados não fazem chamadas reais ao Appwrite ou a provedores externos.

## Implantação

Siga o [runbook do EasyPanel](deploy/easypanel.md) e use
[`deploy/env.production.example`](deploy/env.production.example) somente como checklist. Valores
reais pertencem ao cofre do EasyPanel e nunca ao Git.

O planejamento executável e o roadmap ficam em [`.planning/`](.planning/).

## Definition of Done para produção

“Funciona” não é suficiente. O go-live exige, cumulativamente:

- fluxo completo de dados e provedores sem resultados sintéticos;
- lote de 100 mil entradas com custo, throughput e consumo de memória medidos;
- retomada após falhas sem perda, cobrança duplicada ou duplicação em CRM;
- isolamento de tenant, minimização, retenção, supressão e auditoria verificadas;
- scans de segredo, dependência e imagem sem bloqueador crítico;
- backup/restore e rollback ensaiados com RPO/RTO registrados;
- métricas, alertas, runbooks e aceite operacional em staging.

O status verificável de cada item vive em `.planning/REQUIREMENTS.md` e na Fase 6 do roadmap.
