# Phase 1: Configuração externa necessária

**Generated:** 2026-09-09
**Phase:** 01-funda-o-execut-vel
**Status:** Incomplete

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
