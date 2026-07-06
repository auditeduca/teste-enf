"""Validação semântica com DeepSeek — schema, integridade e readiness para upload."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from paths import load_json  # noqa: E402
from validate_program import run_validation  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _baseline_report(entity_keys: list[str] | None = None) -> dict:
    rep = run_validation(entity_keys)
    total_records = sum(e.get("record_count", 0) for e in rep.entities.values())
    return {
        "mode": "deterministic",
        "upload_ready": rep.ok,
        "overall_score": 100.0 if rep.ok else max(0, 100 - len(rep.errors) * 5),
        "passed": rep.ok,
        "checks": rep.checks,
        "errors": rep.errors[:30],
        "warnings": rep.warnings[:20],
        "entities": rep.entities,
        "total_records": total_records,
        "validated_at": rep.validated_at or _now(),
    }


def validate_with_deepseek(
    *,
    entity_keys: list[str] | None = None,
    use_llm: bool = True,
    payload: dict | None = None,
) -> dict:
    """DeepSeek analisa snapshot do banco e recomenda ajustes Supabase/Firebase."""
    payload = payload or {}
    baseline = _baseline_report(entity_keys)

    if not use_llm:
        baseline["llm_skipped"] = True
        return baseline

    from llm_router import llm_enabled, route_chat_json  # noqa: WPS433

    if not llm_enabled(payload):
        baseline["llm_skipped"] = True
        baseline["llm_reason"] = "DEEPSEEK_API_KEY não configurada"
        return baseline

    prompts = load_json("prompts_registry.json")
    system = _default_system_prompt()
    for p in prompts.get("prompts", []):
        if p.get("prompt_id") == "DATABASE_VALIDATE_SYSTEM":
            system = p.get("template", system)
            break
    snapshot = {
        "entities": baseline["entities"],
        "errors": baseline["errors"],
        "warnings": baseline["warnings"],
        "total_records": baseline["total_records"],
        "supabase_tables": [e.get("table") for e in _entity_list(entity_keys)],
    }

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                "Analise este snapshot do banco NKOS (JSON local) e retorne JSON estrito:\n"
                "{ overall_score, upload_ready, blockers[], recommendations[], "
                "supabase_adjustments[], firebase_adjustments[], table_mappings[] }\n\n"
                f"```json\n{json.dumps(snapshot, ensure_ascii=False, indent=2)[:12000]}\n```"
            ),
        },
    ]

    try:
        llm = route_chat_json(messages, task="database_validation", payload=payload)
        content = llm.get("content") or llm.get("parsed") or {}
        if isinstance(content, str):
            content = json.loads(content)
        merged = {**baseline, **content, "mode": "deepseek", "llm_model": llm.get("model")}
        merged["upload_ready"] = merged.get("upload_ready", baseline["upload_ready"]) and baseline["passed"]
        merged["validated_at"] = _now()
        return merged
    except Exception as exc:
        baseline["llm_error"] = str(exc)[:300]
        return baseline


def _entity_list(entity_keys: list[str] | None) -> list[dict]:
    from config import resolve_entities, all_entities  # noqa: E402
    return resolve_entities(entity_keys) or all_entities()


def _default_system_prompt() -> str:
    return (
        "Você é um agente DeepSeek de validação de banco de dados NKOS. "
        "Avalie integridade, FKs, envelopes JSON e readiness para Supabase (Postgres JSONB) "
        "e Firebase Firestore. Responda APENAS JSON válido."
    )
