# Firebase — Database Sync

Cloud Functions para receber bundles gerados por `scripts/database_sync_agents/` e gravar no Firestore.

## Setup

1. `npm install -g firebase-tools`
2. `firebase login`
3. `cd firebase/functions && npm install`
4. Configure secret (mesmo valor do `.env` raiz):

```bash
firebase functions:config:set nkos.sync_secret="SEU_SECRET"
```

Ou exporte `FIREBASE_SYNC_SECRET` no ambiente das functions.

## Deploy

```bash
cd firebase
firebase deploy --only functions
```

## Endpoints

| Function | Método | Body |
|----------|--------|------|
| `syncNkosBundle` | POST | `{ "secret", "bundle": { "collection", "rows": [...] } }` |
| `databaseSyncHealth` | GET | — |

## Fluxo integrado

1. Python valida JSON local (`POST /api/database-sync/validate`)
2. Gera bundles em `datasets/master-data/database-sync/bundles/`
3. Upload direto Firestore REST **ou** POST para `FIREBASE_FUNCTIONS_URL/syncNkosBundle`

Defina no `.env`:

```env
FIREBASE_FUNCTIONS_URL=https://REGION-PROJECT.cloudfunctions.net
FIREBASE_SYNC_SECRET=...
DATABASE_SYNC_DRY_RUN=0
```

## Anti-alucinação (guardrails)

| Limitador | Efeito |
|-----------|--------|
| `ALLOWED_ACTIONS` whitelist | Steps inventados pelo LLM são descartados |
| `merge_review_safe` | LLM não pode aprovar se determinístico rejeita |
| Score ceiling | `precision_score` LLM ≤ score determinístico |
| `temperature: 0.05` | Respostas mais determinísticas |
| Desvios DeepSeek | Documenta **apenas** errors/warnings detectados em código |

Relatórios gerados automaticamente:
- `datasets/master-data/database-sync/eval_reports/{RUN}_eval.json`
- `datasets/master-data/database-sync/deviation_reports/{RUN}_deviations.json`

## Grafo LangGraph v2

```
Read → Backup → Plan → Review ⇄ RevisePlan → Validate → Deviations → Execute? → Eval → Report
```

- **RevisePlan**: até 2 loops (Review → Generate)
- **Deviations**: DeepSeek redige desvios factuais
- **Eval**: confidence_score + hallucination_flags


Agente que **lê → interpreta → planeja → executa** (substitui planejamento Claude):

```powershell
# Só planejar
python scripts/finalize_base.py --plan

# Backup + plano + execução (dry-run)
python scripts/finalize_base.py --execute

# Upload real
python scripts/finalize_base.py --execute --live

# Só backup
python scripts/finalize_base.py --backup-only

# Restaurar (simular)
python scripts/finalize_base.py --restore BKP.20260621T120000Z
python scripts/finalize_base.py --restore BKP.20260621T120000Z --live
```

Backups em `datasets/backups/BKP.{timestamp}/` com `manifest.json` (SHA256).

API: `POST /api/database-sync/finalize` · `POST /api/database-sync/backup`
