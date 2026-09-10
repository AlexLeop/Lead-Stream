# LeadStream Backend

## What This Is

LeadStream Backend é o novo núcleo independente e Brasil-first para extração, higienização e enriquecimento de leads empresariais. A API parte de uma empresa brasileira real, resolve seus decisores, encontra contatos e perfis públicos atribuíveis a essas pessoas e registra evidência, confiança, atualização, custo e cobrança por bloco efetivamente entregue.

O primeiro marco será usado internamente pelo proprietário e processará lotes de até 100 mil empresas sem modificar ou depender do backend atual. A entrega alvo é um backend de produção completo — não uma demonstração ou MVP — preparado para múltiplos clientes e CRMs, mas sem autenticação de usuários enquanto a operação permanecer interna e protegida no perímetro.

## Core Value

Entregar somente dados úteis atribuíveis à empresa ou ao decisor correto, com proveniência suficiente para distinguir fato, validação, inferência e ausência de dado.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Expor uma API REST versionada em português do Brasil para importar, acompanhar e exportar lotes.
- [ ] Processar até 100 mil registros por jobs duráveis, idempotentes, retomáveis e independentes de uma requisição HTTP.
- [ ] Usar PostgreSQL como banco operacional e Appwrite como integração complementar para arquivos e serviços, sem segredos versionados.
- [ ] Modelar empresa, pessoa, vínculo, cargo, perfil social, ponto de contato, evidência e observação como entidades distintas.
- [ ] Higienizar, normalizar, deduplicar e correlacionar empresas e pessoas sem promover inferências a fatos.
- [ ] Implementar uma cascata de provedores desacoplada: OpenCNPJ/BigQuery, BigDataCorp, Apify, Open Enrich e fallback premium seletivo.
- [ ] Remover a Casa dos Dados da arquitetura e respeitar licenças, permissões, termos, robots e limites de cada fonte.
- [ ] Registrar custo, consumo, taxa de acerto e cobrança por bloco somente quando um resultado elegível for entregue.
- [ ] Manter isolamento por tenant desde o schema inicial, usando um tenant interno padrão enquanto não houver autenticação.
- [ ] Permitir conectores independentes para múltiplos CRMs, com idempotência, mapeamento de campos e auditoria.
- [ ] Aplicar minimização, retenção, supressão e rastreabilidade compatíveis com o tratamento profissional de dados pessoais.
- [ ] Oferecer observabilidade operacional, health checks, métricas, logs estruturados e rastreamento de falhas por provedor.
- [ ] Ser implantável no EasyPanel com recursos limitados, mantendo dados brutos e arquivos volumosos fora da VPS.
- [ ] Passar por testes de carga, retomada após falhas, backup/restore, segurança de dependências e aceite operacional antes de receber dados reais em produção.
- [ ] Definir SLOs, alertas, RPO/RTO e rollback verificáveis, sem classificar código apenas funcional como pronto para produção.

### Out of Scope

- Alterar o projeto LeadStream atual — o novo backend deve permanecer em repositório e implantação independentes.
- Criar interface web ou refazer o frontend no primeiro marco — a entrega inicial é API, workers e documentação operacional.
- Criar autenticação de usuários na primeira versão — o uso inicial é interno e protegido no perímetro de implantação.
- Armazenar a base bruta nacional da Receita Federal na VPS — snapshots e Parquet devem residir em armazenamento externo.
- Fazer engenharia reversa ou scraping da Casa dos Dados — a fonte foi explicitamente removida da solução.
- Inferir WhatsApp ativo, vínculo profissional ou propriedade de contato sem evidência compatível.
- Automatizar acesso a conteúdo privado, contornar controles de acesso ou coletar dados fora da finalidade profissional documentada.

## Context

- O sistema atual usa React/TypeScript, Express e SQLite, mas não será alterado durante a construção deste backend.
- A VPS disponível possui 4 vCPUs, 16 GB de RAM e aproximadamente 193 GB de disco, compartilhados com serviços existentes.
- O PostgreSQL foi criado no ambiente EasyPanel e será acessado por configuração de ambiente; o hostname informado é interno à rede de containers.
- Existe uma instância Appwrite própria. A integração será configurada por endpoint, Project ID e API key fornecida somente no ambiente de execução.
- As credenciais compartilhadas durante o planejamento devem ser rotacionadas antes da implantação produtiva.
- O custo de referência da cascata completa é R$ 0,16 por registro de entrada, ainda sujeito a validação em lote piloto.
- O preço máximo projetado é R$ 0,80 por lead quando todos os blocos de informação forem entregues.
- Um resultado não encontrado, repetido, inalterado, expirado, de baixa confiança ou proveniente de falha do provedor não pode gerar cobrança.
- A latência dominante será de APIs externas e pesquisas públicas; a API web deve apenas controlar jobs e disponibilizar resultados.

## Constraints

- **Stack**: Python 3.13, Django 5.2 LTS, Django REST Framework, PostgreSQL, Celery, RabbitMQ, Redis, Polars e DuckDB.
- **Compatibilidade**: API versionada e contrato estável para permitir conexão posterior do frontend existente.
- **Capacidade**: a VPS coordena API e workers; arquivos brutos, exports extensos e snapshots ficam em object storage.
- **Volume**: um lote de 100 mil entradas precisa sobreviver a reinícios, timeouts e indisponibilidades externas.
- **Qualidade**: todo valor exportável deve possuir origem, instante, método, estado de evidência e confiança.
- **Privacidade**: dados pessoais exigem finalidade profissional, minimização, retenção, supressão e trilha de auditoria.
- **Custo**: cada chamada externa deve respeitar orçamento por job e custo máximo configurável por lead útil.
- **Segurança**: nenhum segredo pode ser versionado; a API interna deve permanecer protegida pelo perímetro do EasyPanel ou gateway.
- **Idioma**: mensagens, documentação operacional e exportações devem usar português do Brasil.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Criar um repositório independente | Preservar o projeto atual e permitir evolução sem compatibilidade acidental | — Pending |
| Django 5.2 LTS e DRF como control plane | Ecossistema maduro para domínio, migrações, administração e APIs | — Pending |
| PostgreSQL como fonte operacional de verdade | Necessário para relações, transações, auditoria, cobrança e consultas consistentes | — Pending |
| Appwrite como serviço complementar | Evita substituir o ORM do Django por chamadas remotas e preserva uso de storage e serviços do Appwrite | — Pending |
| Celery e RabbitMQ para jobs duráveis | Lotes extensos não podem depender de requisições HTTP ou memória de um processo | — Pending |
| Redis para cache e rate limiting | Permite cotas atômicas e coordenação entre workers | — Pending |
| Jobs em chunks, não um job por registro | Reduz overhead de fila sem perder retomada e isolamento de falhas | — Pending |
| Multi-tenant desde o primeiro schema | Evita uma migração estrutural futura, mantendo tenant interno padrão durante a operação interna | — Pending |
| Cobrança por bloco entregue | Alinha preço ao valor recebido e torna falhas e ausências não faturáveis | — Pending |
| Evidência como requisito do dado | Impede que heurísticas, snippets e dados sintéticos sejam vendidos como fatos | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition**:
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone**:
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-09 after production-scope correction*
