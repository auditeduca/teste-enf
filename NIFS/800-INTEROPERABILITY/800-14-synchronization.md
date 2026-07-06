# NIFS-800-14: Synchronization

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-14                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS sincroniza dados entre fontes — NKOS datasets, Supabase, EHRs — mantendo consistência.

## 2. Sync Architecture

```
Source A (NKOS JSON)          Source B (Supabase)
        ↓                           ↓
    Sync Adapter               Sync Adapter
        ↓                           ↓
        └───── Conflict Resolver ───┘
                     ↓
              NIS Database (source of truth)
                     ↓
              Sync Logger
```

## 3. Sync Patterns

| Pattern | Direction | Trigger | Use Case |
|---------|-----------|---------|----------|
| Full sync | Source → NIS | Manual / scheduled | Initial load, major updates |
| Incremental | Source → NIS | Change detection | Ongoing updates |
| Bidirectional | NIS ↔ Source | Event-driven | EHR integration |
| One-way push | NIS → Target | On change | Push to analytics DW |

## 4. NKOS → NIS Sync

O CALENF-NKD já tem infraestrutura de sync:
- `datasets/backups/BKP.*/master-data/database-sync/supabase_schema.sql` — schema Supabase para sync
- `scripts/anvisa_open_data_agents/` — sync ANVISA (monthly CI)
- `.github/workflows/daily-platform-loop.yml` — CI daily sync
- `.github/workflows/monthly-anvisa-sync.yml` — CI monthly ANVISA

## 5. Sync Protocol

```
1. Detect changes (checksum, timestamp, version)
2. Fetch changed records from source
3. Map to NIS schema
4. Check conflicts (same record changed in both?)
5. Resolve: NIS is source of truth (or human review for conflicts)
6. Apply: insert/update/delete
7. Update sync metadata (last_sync, checksum)
8. Log to ni_interop.sync_logs
```

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_interop.sync_logs` | Sync audit trail |
| `ni_interop.sync_sources` | Source registry |
| `ni_interop.sync_conflicts` | Conflict log |
| `ni_interop.sync_metadata` | Last sync timestamps |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-09 | Import (one-way sync) |
| NIFS-800-10 | Export (push sync) |
| NIFS-1400-04 | Backup Strategy |
