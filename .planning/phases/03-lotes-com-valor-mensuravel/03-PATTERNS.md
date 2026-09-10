# Phase 3 Patterns

- Apps Django separados: `batches`, `hygiene` e `billing`.
- Serviços de escrita com `transaction.atomic`; views apenas validam e delegam.
- Estado de lote é monotônico e alterado por comandos explícitos.
- Celery recebe UUIDs, não payloads pessoais.
- Side effects possuem chave idempotente e registro de tentativa.
- CSV e respostas usam português do Brasil; contratos internos permanecem tipados.
- Testes executam tasks inline e não usam rede, RabbitMQ ou Redis reais.
