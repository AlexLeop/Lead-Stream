# Implantação no EasyPanel

Este runbook instala somente a fundação do novo backend. A API, o worker, o PostgreSQL,
o RabbitMQ e o Redis ficam na rede privada do projeto. Como a primeira versão não possui
login no produto, o domínio da API **não deve ficar público sem uma barreira de acesso**.

## Topologia recomendada

| Serviço | Origem | Comando | Exposição |
|---|---|---|---|
| `leadstream-api` | imagem deste repositório | comando padrão da imagem | HTTPS, protegido no gateway |
| `leadstream-worker` | mesma imagem | `celery -A config.celery:app worker --loglevel=INFO --concurrency=2` | somente rede privada |
| `leadstream-release` | mesma imagem, execução manual | `sh scripts/release.sh` | nenhuma |
| PostgreSQL | serviço já existente | padrão do provedor | somente rede privada |
| RabbitMQ | `rabbitmq:4-management-alpine` | padrão da imagem | somente rede privada |
| Redis | `redis:8-alpine` | `redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy noeviction` | somente rede privada |

O Appwrite é uma dependência complementar para serviços da plataforma. O banco canônico
do Django continua sendo o PostgreSQL; o Appwrite não substitui o ORM nem recebe migrations.

## 1. Proteja a entrada

Antes de publicar o domínio, aplique no proxy uma allowlist de IP, VPN ou uma camada como
Cloudflare Access. A ausência de autenticação interna foi uma decisão consciente para uso
próprio, mas não autoriza exposição anônima na internet. Não publique as portas do PostgreSQL,
RabbitMQ, Redis ou Appwrite pela aplicação.

## 2. Configure os serviços de estado

1. Reutilize o PostgreSQL criado no EasyPanel e confirme que API e worker alcançam o nome
   interno do serviço.
2. Crie RabbitMQ e Redis dentro do mesmo projeto/rede privada.
3. Use volumes persistentes para PostgreSQL, RabbitMQ e Redis.
4. Crie usuários e senhas exclusivos de produção; os valores do `compose.yaml` servem apenas
   ao ambiente local.

Na VPS de 4 vCPUs e 16 GB, comece com esta distribuição e ajuste após observar o uso real:

| Serviço | CPU | Memória |
|---|---:|---:|
| API, 2 processos | 1 vCPU | 1 GB |
| Worker, concorrência 2 | 2 vCPUs | 4 GB |
| PostgreSQL | 1 vCPU | 4 GB |
| RabbitMQ | 0,5 vCPU | 1 GB |
| Redis | 0,5 vCPU | 512 MB |

Limites não precisam somar exatamente a capacidade física, mas preserve memória para o
sistema, proxy, Appwrite e picos. Não aumente a concorrência do worker antes de medir memória,
latência e quotas dos provedores.

## 3. Cadastre os segredos

Use [`env.production.example`](env.production.example) como checklist de nomes. Cadastre os
valores reais diretamente no cofre de variáveis do EasyPanel para API, worker e release.

- `DATABASE_SSL_REQUIRED=false` é aceitável apenas para a conexão dentro da rede privada do
  EasyPanel. Para um PostgreSQL externo, habilite TLS e use `true`.
- Gere `DJANGO_SECRET_KEY` exclusivamente para esta aplicação.
- Use uma nova chave Appwrite de runtime com o menor escopo possível. A chave compartilhada
  durante o planejamento deve ser revogada.
- Nunca grave URLs com senha, tokens ou chaves na imagem, no repositório ou nos logs.

## 4. Publique com ordem segura

1. Execute `powershell -File scripts/quality.ps1` no Windows ou `sh scripts/quality.sh` no Linux.
2. Construa e publique a imagem imutável com uma tag de commit, não `latest`.
3. Atualize o serviço manual `leadstream-release` para essa imagem e execute-o uma única vez.
4. Confirme que a saída contém migrations concluídas e verificação de produção sem erros.
5. Atualize a API e espere `/health/ready` ficar saudável.
6. Atualize o worker com a mesma tag da API.
7. Verifique `/health/dependencies`; dependências opcionais podem aparecer degradadas sem
   derrubar a prontidão do PostgreSQL.

Migrations não são executadas no início da API nem do worker. Isso evita concorrência entre
réplicas e torna falhas de implantação explícitas.

## 5. Configure o domínio e os health checks

- Rota de vida: `GET /health/live` — use para reiniciar um processo travado.
- Rota de prontidão: `GET /health/ready` — exige PostgreSQL e migrations aplicadas.
- Diagnóstico: `GET /health/dependencies` — mostra estados sanitizados de PostgreSQL, Redis,
  RabbitMQ e Appwrite.
- Documentação: `GET /api/v1/docs/` — mantenha atrás da mesma barreira de acesso.

O proxy deve terminar HTTPS e enviar `X-Forwarded-Proto: https`. A aplicação força HTTPS nas
rotas de negócio; os health checks são isentos para permitir sondagem interna.

## 6. Valide e reverta

Após a publicação, confirme:

```text
GET /health/live          -> 200
GET /health/ready         -> 200
GET /api/v1/workspace/    -> 200 e tenant interno
GET /api/v1/schema/       -> 200
```

Em caso de falha, restaure API e worker para a tag anterior. Não reverta migrations cegamente:
primeiro confirme se a migration é compatível com a versão anterior e restaure um backup do
PostgreSQL quando necessário. As migrations desta fase são somente aditivas.

## Operação inicial

- Retenha logs JSON no EasyPanel e pesquise pelo campo `request_id` ao investigar uma chamada.
- Não exponha `/health/dependencies` fora da barreira de acesso; ele não revela segredos, mas
  informa a saúde da infraestrutura.
- Faça backup automatizado do PostgreSQL antes das próximas fases de dados reais.
- O object storage externo será configurado na fase de importação/exportação; não use o disco
  da VPS para snapshots nacionais da Receita Federal.
