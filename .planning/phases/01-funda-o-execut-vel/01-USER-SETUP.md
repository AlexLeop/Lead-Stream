# Phase 1: Configuração externa necessária

**Generated:** 2026-09-09
**Phase:** 01-funda-o-execut-vel
**Status:** Incomplete — aguardando rotação e cadastro no EasyPanel

O código, os mocks e os testes automatizados já estão prontos. Os itens abaixo exigem acesso humano ao Appwrite e, depois, ao painel do EasyPanel. Nunca copie os valores reais para arquivos versionados.

## Variáveis de ambiente — Appwrite

| Status | Variable | Source | Add to |
|---|---|---|---|
| [ ] | `APPWRITE_ENDPOINT` | Appwrite Console → API credentials → API Endpoint | EasyPanel → serviço API e worker |
| [ ] | `APPWRITE_PROJECT_ID` | Appwrite Console → API credentials → Project ID | EasyPanel → serviço API e worker |
| [ ] | `APPWRITE_API_KEY` | Appwrite Console → Overview → Integrations → API keys | EasyPanel → serviço API e worker |
| [ ] | `APPWRITE_TIMEOUT_SECONDS` | Valor operacional recomendado: `3` | EasyPanel → serviço API e worker |

## Configuração no painel

- [ ] **Revogar a chave compartilhada anteriormente e criar uma nova chave runtime**
  - Location: Appwrite Console → Overview → Integrations → API keys
  - Escopo nesta fase: `health.read` ou o menor escopo equivalente disponível na instalação.
  - Notes: Storage será habilitado somente quando a fase de exportação exigir.

- [ ] **Confirmar HTTPS válido na instância Appwrite**
  - Location: domínio público configurado no EasyPanel/proxy.
  - Set to: certificado confiável; o backend não desabilita verificação TLS.

## Variáveis de ambiente — aplicação e infraestrutura

Cadastre os nomes listados em `deploy/env.production.example` nos serviços `leadstream-api`,
`leadstream-worker` e `leadstream-release`. Os três devem usar a mesma tag imutável da imagem e
o mesmo conjunto de configurações, exceto pelo comando de execução.

- [ ] Gerar um `DJANGO_SECRET_KEY` novo e exclusivo.
- [ ] Definir `DJANGO_ALLOWED_HOSTS` com o domínio final da API.
- [ ] Cadastrar a URL do PostgreSQL já criado diretamente no cofre como `DATABASE_URL`.
- [ ] Manter `DATABASE_SSL_REQUIRED=false` somente se a conexão permanecer integralmente na
  rede privada do EasyPanel; habilitar TLS para banco externo.
- [ ] Criar RabbitMQ e Redis privados e cadastrar `CELERY_BROKER_URL` e `REDIS_URL`.
- [ ] Proteger o domínio com allowlist, VPN ou Cloudflare Access antes de publicá-lo, pois esta
  versão interna não possui autenticação no produto.
- [ ] Garantir volumes persistentes e backup do PostgreSQL antes de inserir dados reais.

## Ordem da primeira implantação

- [ ] Executar localmente `scripts/quality.ps1` ou `scripts/quality.sh`.
- [ ] Construir uma imagem com tag do commit e cadastrá-la nos três serviços.
- [ ] Executar `leadstream-release` uma única vez para aplicar migrations.
- [ ] Publicar a API e confirmar `/health/live` e `/health/ready`.
- [ ] Publicar o worker e confirmar `/health/dependencies`.
- [ ] Seguir integralmente `deploy/easypanel.md`.

## Verificação

Após definir as variáveis na implantação:

```bash
curl --fail --silent https://<dominio-da-api>/health/dependencies
```

Expected results:

- `appwrite.status` deve ser `ok`.
- Ausência/falha do Appwrite aparece como `degraded`/`unavailable`, sem host, token ou trace.
- `/health/ready` permanece saudável quando PostgreSQL e migrations estão disponíveis.

---

**Once all items complete:** altere o status no topo para `Complete`.
