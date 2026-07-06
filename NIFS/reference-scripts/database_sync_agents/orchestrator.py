"""Pipeline: validar → DeepSeek → transformar → Supabase/Firebase."""
from __future__ import annotations

from uuid import uuid4

from config import resolve_entities
from paths import append_log
from schema_builder import write_schema_file
from uploader_firebase import upload_entities as upload_firebase
from uploader_supabase import upload_entities as upload_supabase
from validate_program import run_validation
from validator_agent import validate_with_deepseek


def run_pipeline(
    *,
    entity_keys: list[str] | None = None,
    target: str = "supabase",
    use_llm: bool = True,
    dry_run: bool | None = None,
    validate_only: bool = False,
    payload: dict | None = None,
    tier: str | None = None,
) -> dict:
    payload = payload or {}
    run_id = f"SYNC.{uuid4().hex[:10].upper()}"

    if tier:
        from config import ENTITY_TIERS
        keys = [e["entity_key"] for e in ENTITY_TIERS.get(tier, [])]
        entities = resolve_entities(keys)
    else:
        entities = resolve_entities(entity_keys)

    deterministic = run_validation([e["entity_key"] for e in entities])
    validation = validate_with_deepseek(
        entity_keys=[e["entity_key"] for e in entities],
        use_llm=use_llm,
        payload=payload,
    )

    schema_path = write_schema_file()

    result = {
        "ok": validation.get("upload_ready", deterministic.ok),
        "run_id": run_id,
        "validation": {
            "deterministic_ok": deterministic.ok,
            "upload_ready": validation.get("upload_ready"),
            "overall_score": validation.get("overall_score"),
            "errors": validation.get("errors", deterministic.errors)[:20],
            "warnings": validation.get("warnings", deterministic.warnings)[:20],
            "blockers": validation.get("blockers", []),
            "recommendations": validation.get("recommendations", []),
            "mode": validation.get("mode"),
        },
        "schema_sql": schema_path,
        "entities": [e["entity_key"] for e in entities],
    }

    if validate_only or (not validation.get("upload_ready", deterministic.ok) and not payload.get("force")):
        result["upload_skipped"] = True
        append_log(run_id, result)
        return result

    uploads = {}
    if target in ("supabase", "both"):
        uploads["supabase"] = upload_supabase(entities, dry_run=dry_run)
    if target in ("firebase", "both"):
        uploads["firebase"] = upload_firebase(
            entities,
            dry_run=dry_run,
            use_function=payload.get("use_firebase_function", True),
        )

    result["uploads"] = uploads
    result["ok"] = all(u.get("ok") for u in uploads.values()) if uploads else result["ok"]
    append_log(run_id, result)
    return result
