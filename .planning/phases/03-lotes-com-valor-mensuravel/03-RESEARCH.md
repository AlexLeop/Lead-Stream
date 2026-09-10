# Phase 3 Research

## Production Pattern

O padrão selecionado é transactional outbox-lite: a transação grava lote/chunks, e
`transaction.on_commit` publica IDs no Celery. O worker reivindica um chunk com lock e lease,
mantém checkpoint por item e pode reexecutar sem repetir itens concluídos.

Uploads são lidos em streaming, limitados por bytes e linhas, com SHA-256 e chave opaca.
Normalização reaproveita regras canônicas existentes. Deduplicação usa fingerprint estável
por tenant e lote, sem apagar a linha original.

Ledgers financeiros usam inteiros em centavos, moeda explícita e chave idempotente única.
Relatórios agregam eventos persistidos, nunca estimativas reconstruídas de logs.
