"""Pipeline Search → Scrape → Structure → Validate — notificação compulsória."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "compulsory_notification_agents"))

from agent_common.sanitize import sanitize_agent_result  # noqa: E402
from apgar_agents.llm import chat_json, resolve_model  # noqa: E402
from apply_entry import apply_entry  # noqa: E402
from catalog import build_queue, get_pending_item, is_structured  # noqa: E402
from config import PROMPTS_DIR  # noqa: E402
from scrape import scrape_all, scrape_source  # noqa: E402
from structure import deterministic_structure, llm_structure, scrape_context_for_item  # noqa: E402
from validators import validate_entry  # noqa: E402


def run_scrape(*, limit: int | None = None) -> dict:
    return scrape_all(limit=limit)


def run_item(
    pending_id: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = False,
    apply: bool = True,
) -> dict:
    item = get_pending_item(pending_id)
    if not item:
        raise KeyError(f"pending_id não encontrado: {pending_id}")

    if is_structured(item["concept_code"]):
        return sanitize_agent_result({
            "pending_id": pending_id,
            "entity_code": item["entity_code"],
            "status": "already_structured",
            "parent_entity_code": item["parent_entity_code"],
        })

    model = resolve_model(model)
    ctx = scrape_context_for_item(item)
    if not ctx and item.get("source_id"):
        from config import SCRAPE_SOURCES  # noqa: WPS433

        sources = json.loads(SCRAPE_SOURCES.read_text(encoding="utf-8")).get("sources", [])
        src = next((s for s in sources if s.get("source_id") == item["source_id"]), None)
        if src:
            ctx = scrape_source(src)
            ctx = {**ctx, "text_snippet": ""}

    search = {
        "condition_name_pt": item.get("condition_name_pt"),
        "parent_entity_code": item.get("parent_entity_code"),
        "jurisdiction_code": item.get("jurisdiction_code"),
        "source_url": item.get("source_url"),
        "mode": "deterministic",
    }

    if use_llm and api_key:
        try:
            system = (PROMPTS_DIR / "search.md").read_text(encoding="utf-8")
            user = json.dumps({"queue_item": item, "scrape": ctx}, ensure_ascii=False, indent=2)
            search = chat_json(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                api_key=api_key,
                model=model,
            )
            search["mode"] = "deepseek"
        except Exception:
            pass

    if use_llm and api_key and ctx:
        proposal = llm_structure(item, ctx, api_key=api_key, model=model)
    else:
        proposal = deterministic_structure(item, ctx)

    review = {"decision": "approve", "mode": "deterministic"}
    if use_llm and api_key:
        try:
            system = (PROMPTS_DIR / "review.md").read_text(encoding="utf-8")
            user = json.dumps({"proposal": proposal}, ensure_ascii=False, indent=2)
            review = chat_json(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                api_key=api_key,
                model=model,
            )
        except Exception as exc:
            review = {"decision": "approve", "notes_pt": str(exc), "mode": "fallback"}

    validation = validate_entry(proposal)
    validation_dict = {
        "validation_passed": validation.ok and review.get("decision") != "reject",
        "errors": validation.errors,
        "warnings": validation.warnings,
    }

    result = sanitize_agent_result({
        "pending_id": pending_id,
        "entity_code": item["entity_code"],
        "parent_entity_code": item["parent_entity_code"],
        "jurisdiction_code": item["jurisdiction_code"],
        "steps": {
            "search": search,
            "scrape_context": bool(ctx),
            "proposal": proposal,
            "review": review,
            "validation": validation_dict,
        },
        "status": "applied" if validation_dict["validation_passed"] and apply else "awaiting_approval",
    })

    if validation_dict["validation_passed"] and apply:
        result["apply"] = apply_entry(proposal)
    return result


def run_batch(
    *,
    limit: int = 10,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = False,
    apply: bool = True,
    scrape_first: bool = False,
    scrape_limit: int | None = None,
) -> dict:
    scrape_result = None
    if scrape_first:
        scrape_result = run_scrape(limit=scrape_limit)
        build_queue(limit=limit * 3)

    queue = build_queue(limit=limit)
    results = []
    errors = []
    for item in queue.get("items", []):
        try:
            results.append(
                run_item(
                    item["pending_id"],
                    api_key=api_key,
                    model=model,
                    use_llm=use_llm,
                    apply=apply,
                )
            )
        except Exception as exc:
            errors.append({"pending_id": item.get("pending_id"), "error": str(exc)})

    applied = sum(1 for r in results if r.get("status") == "applied")
    return sanitize_agent_result({
        "ok": len(errors) == 0,
        "processed": len(results),
        "applied": applied,
        "scrape": scrape_result,
        "errors": errors,
        "results": results,
    })
