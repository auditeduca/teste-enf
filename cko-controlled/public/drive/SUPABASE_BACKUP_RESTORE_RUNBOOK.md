# Supabase Backup / Restore Runbook — Checkpoint Wave 5

## Estado deste checkpoint

Este checkpoint contém um snapshot inventarial e de estado do projeto Supabase `Calculadoras-Smart`.

Ele **não é, por si só, um backup 100% restaurável**.

### Para produzir o backup lógico restaurável do banco

Usar uma conexão autorizada e o Supabase CLI:

```bash
supabase db dump --db-url [CONNECTION_STRING] -f roles.sql --role-only
supabase db dump --db-url [CONNECTION_STRING] -f schema.sql
supabase db dump --db-url [CONNECTION_STRING] -f data.sql --use-copy --data-only -x "storage.buckets_vectors" -x "storage.vector_indexes"
```

### Storage

O backup lógico do Postgres preserva metadados do Storage, mas não os bytes dos objetos.

Exportar separadamente:
- objetos dos buckets;
- estrutura de buckets;
- políticas necessárias;
- evidência de contagem e reconciliação pós-restauração.

### Edge Functions

Exportar separadamente:
- source de cada função;
- `deno.json` / `deno.jsonc`;
- import maps;
- dependências relativas;
- configuração de `verify_jwt`;
- versão/status;
- varéaveis necessárias **sem armazenar secrets em claro**.

### Auth / configuração

Registrar separadamente:
- providers habilitados;
- redirect URLs;
- políticas/configurações relevantes;
- SMTP/branding quando aplicável;
- secrets somente por mecanismo seguro, nunca no pacote de backup.

### Teste de restauração

Um backup somente deve ser promovido a `RESTORE_VERIFIED` depois de:
1. restaurar em ambiente de teste;
2. reconciliar tabelas/migrações;
3. reconciliar Storage;
4. reconciliar Edge Functions;
5. validar Auth/config;
6. executar smoke tests;
7. produzir evidência da reperformance.
