"""Status — Database Sync Agent."""
from __future__ import annotations

from config import (
    DATABASE_SYNC_DRY_RUN,
    ENTITY_TIERS,
    FIREBASE_CREDENTIALS_JSON,
    FIREBASE_FUNCTIONS_URL,
    FIREBASE_PROJECT_ID,
    SUPABASE_ANON_KEY,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
    all_entities,
)
from backup import list_backups
from finalize_graph import GRAPH_VERSION  # noqa: E402
from paths import BUNDLES, LOGS, MD, SCHEMA_OUT, last_log, load_json
from uploader_firebase import configured as firebase_configured
from uploader_supabase import configured as supabase_configured


def collect_status() -> dict:
    last = last_log()
    return {
        "program_code": "DATABASE_SYNC",
        "name": "NKOS Database Sync — Supabase + Firebase",
        "entities_total": len(all_entities()),
        "tiers": list(ENTITY_TIERS.keys()),
        "dry_run_default": DATABASE_SYNC_DRY_RUN(),
        "supabase": {
            "configured": supabase_configured(),
            "url_set": bool(SUPABASE_URL()),
            "service_role": bool(SUPABASE_SERVICE_ROLE_KEY()),
            "anon_key": bool(SUPABASE_ANON_KEY()),
        },
        "firebase": {
            "configured": firebase_configured(),
            "project_id": bool(FIREBASE_PROJECT_ID()),
            "credentials": bool(FIREBASE_CREDENTIALS_JSON()),
            "functions_url": bool(FIREBASE_FUNCTIONS_URL()),
        },
        "schema_sql": str(SCHEMA_OUT) if SCHEMA_OUT.is_file() else None,
        "bundles_dir": str(BUNDLES),
        "logs_dir": str(LOGS),
        "last_run": last,
        "last_backups": list_backups(5),
        "prompts_loaded": bool(load_json("prompts_registry.json")),
        "single_command": "python scripts/finalize_base.py --validate-only",
        "finalize_command": "python scripts/finalize_base.py --execute --live",
        "backup_command": "python scripts/finalize_base.py --backup-only",
        "engine": GRAPH_VERSION,
        "min_precision_score": 95.0,
        "guardrails": "whitelist_actions + conservative_review_merge + deviation_doc_factual_only",
        "reports": {
            "eval": str(MD / "last_eval_report.json"),
            "deviations": str(MD / "last_deviation_report.json"),
        },
        "api_routes": [
            "GET /api/database-sync/status",
            "POST /api/database-sync/validate",
            "POST /api/database-sync/schema",
            "POST /api/database-sync/upload",
            "POST /api/database-sync/sync",
            "POST /api/database-sync/finalize",
            "POST /api/database-sync/backup",
        ],
    }
