# Phase 3 Context — Lotes com Valor Mensurável

## Objective

Aceitar até 100 mil registros sem manter a requisição HTTP aberta, higienizar e deduplicar
de forma reproduzível, sobreviver a reinícios e registrar custo, receita e lucro somente
quando um bloco útil for efetivamente entregue.

## Locked Decisions

- CSV é persistido antes de enfileirar trabalho; API devolve `202` e ID do lote.
- Jobs são estado durável no PostgreSQL; Celery transporta apenas IDs.
- Chunks usam lease, checkpoint e tentativa idempotente.
- Original, normalizado, regra e motivo são preservados por item.
- Custo e cobrança são ledgers append-only em centavos; ausência e erro não faturam.
- Preço é versionado por bloco e copiado ao evento no momento da entrega.
- Pausa/cancelamento não desfaz resultado já confirmado.

## Constraints

- API e worker precisam compartilhar o backend de objetos; armazenamento local só é fallback
  de desenvolvimento e será substituído pelo adaptador Appwrite na Phase 5.
- Redis não é fonte de verdade.
- Nenhuma chamada externa real pertence a esta fase; providers entram na Phase 4.
