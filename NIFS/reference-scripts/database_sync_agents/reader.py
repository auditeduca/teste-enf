"""Leitura de contexto — inventário para o agente DeepSeek planejar."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from config import ENTITY_TIERS, all_entities  # noqa: E402
from validate_program import run_validation  # noqa: E402


def build_context_snapshot(*, tiers: list[str] | None = None) -> dict:
    """Snapshot completo: entidades, validação, pendências, env (sem secrets)."""
    from agent_common.env_loader import env_status  # noqa: WPS433
    from agent_common.pending_inventory import collect  # noqa: WPS433

    tier_keys = tiers or list(ENTITY_TIERS.keys())
    entity_keys = []
    for t in tier_keys:
        entity_keys.extend(e["entity_key"] for e in ENTITY_TIERS.get(t, []))

    validation = run_validation(entity_keys)
    env = env_status()

    entities_summary = {}
    for key, info in validation.entities.items():
        entities_summary[key] = {
            "record_count": info.get("record_count"),
            "ok": info.get("ok"),
            "issues": info.get("issues", [])[:5],
        }

    pending = collect()
    cloud = {
        "supabase_url": bool(__import__("os").environ.get("SUPABASE_URL")),
        "supabase_key": bool(__import__("os").environ.get("SUPABASE_SERVICE_ROLE_KEY") or __import__("os").environ.get("SUPABASE_ANON_KEY")),
        "firebase_project": bool(__import__("os").environ.get("FIREBASE_PROJECT_ID")),
        "firebase_credentials": bool(__import__("os").environ.get("FIREBASE_CREDENTIALS_JSON")),
        "firebase_functions": bool(__import__("os").environ.get("FIREBASE_FUNCTIONS_URL")),
        "deepseek": env.get("keys", {}).get("DEEPSEEK_API_KEY", False),
        "dry_run_default": __import__("os").environ.get("DATABASE_SYNC_DRY_RUN", "1"),
    }

    phase_report = ROOT / "datasets" / "metadata" / "validation_phases_1_7_report.json"
    phase_summary = None
    if phase_report.is_file():
        phase = json.loads(phase_report.read_text(encoding="utf-8"))
        phase_summary = {
            "checks": phase.get("checks"),
            "error_count": len(phase.get("errors", [])),
            "warning_count": len(phase.get("warnings", [])),
            "sample_errors": phase.get("errors", [])[:8],
        }

    return {
        "program": "NKOS_DATABASE_FINALIZE",
        "tiers": tier_keys,
        "entities_total": len(all_entities()),
        "entities_summary": entities_summary,
        "validation_ok": validation.ok,
        "validation_errors": validation.errors[:15],
        "validation_warnings": validation.warnings[:15],
        "pending_inventory": pending.get("summary"),
        "pending_actions_count": len(pending.get("actions", [])),
        "cloud_configured": cloud,
        "phase_1_7": phase_summary,
        "goal_hint": (
            "Finalizar base NKOS: backup → validar → schema Supabase → upload integra "
            "(Supabase JSONB + Firebase Firestore). Substituir papel de planejamento Claude."
        ),
    }
