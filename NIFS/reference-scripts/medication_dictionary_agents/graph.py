"""Pipeline Search → Generate → Review → Validate — dicionário de medicamentos."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "medication_dictionary_agents"))

from agent_common.sanitize import sanitize_agent_result  # noqa: E402
from apgar_agents.llm import chat_json, resolve_model  # noqa: E402
from apply_entry import apply_entry  # noqa: E402
from catalog import build_queue, get_pending_item, is_linked  # noqa: E402
from config import PROMPTS_DIR  # noqa: E402
from validators import validate_entry  # noqa: E402


def _deterministic_search(item: dict) -> dict:
    return {
        "drug_ref_code": item["drug_ref_code"],
        "concept_code": item["concept_code"],
        "term_pt": item.get("term_pt"),
        "atc_code": item.get("atc_code"),
        "pharmacological_class": item.get("pharmacological_class"),
        "high_alert_medication": item.get("high_alert_medication"),
        "linked_monograph_code": item.get("linked_monograph_code"),
        "mode": "deterministic",
    }


def _deterministic_generate(item: dict, search: dict) -> dict:
    term = item.get("term_pt") or item.get("concept_code")
    cls = item.get("pharmacological_class") or "medicamento"
    atc = item.get("atc_code") or "—"
    ha = item.get("high_alert_medication")
    ha_txt = " Medicamento de alta vigilância — dupla checagem e monitorização contínua." if ha else ""
    definition = (
        f"{term}: {cls.replace('_', ' ')} (ATC {atc}). "
        f"Entrada vinculada ao conceito pai {item['drug_ref_code']}.{ha_txt} "
        f"Revisar monografia institucional antes da administração."
    )
    return {
        "entity_code": item["entity_code"],
        "concept_code": item["concept_code"],
        "parent_entity_code": item["drug_ref_code"],
        "parent_entity_type": "DrugReference",
        "drug_ref_code": item["drug_ref_code"],
        "linked_monograph_code": item.get("linked_monograph_code"),
        "term_pt": term,
        "term_en": item.get("term_en"),
        "slug": (term or "").lower().replace(" ", "-")[:80],
        "atc_code": item.get("atc_code"),
        "pharmacological_class": item.get("pharmacological_class"),
        "high_alert_medication": ha,
        "routes": item.get("routes") or [],
        "definition_pt": definition,
        "nursing_monitoring_pt": "Sinais vitais, reações adversas, compatibilidade de via e documentação (9 Rights).",
        "evidence_grade": "A",
        "evidence_source": {
            "citation": "DrugReference NKOS + prática clínica enfermagem",
            "organization": "NKOS_CUSTOM",
            "year": 2026,
        },
        "mode": "deterministic",
    }


def _llm_generate(item: dict, search: dict, *, api_key: str, model: str) -> dict:
    system = (PROMPTS_DIR / "generate.md").read_text(encoding="utf-8")
    user = json.dumps({"queue_item": item, "search": search}, ensure_ascii=False, indent=2)
    out = chat_json(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        api_key=api_key,
        model=model,
    )
    if isinstance(out, dict):
        out.setdefault("entity_code", item["entity_code"])
        out.setdefault("concept_code", item["concept_code"])
        out.setdefault("parent_entity_code", item["drug_ref_code"])
        out.setdefault("parent_entity_type", "DrugReference")
        out.setdefault("drug_ref_code", item["drug_ref_code"])
        out["mode"] = "deepseek"
    return out


def _review(proposal: dict, *, api_key: str | None, model: str, use_llm: bool) -> dict:
    if use_llm and api_key:
        try:
            system = (PROMPTS_DIR / "review.md").read_text(encoding="utf-8")
            user = json.dumps({"proposal": proposal}, ensure_ascii=False, indent=2)
            return chat_json(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                api_key=api_key,
                model=model,
            )
        except Exception as exc:
            return {"decision": "approve", "notes_pt": f"Review fallback: {exc}", "mode": "fallback"}
    val = validate_entry(proposal)
    return {
        "decision": "approve" if val.ok else "revise",
        "notes_pt": "; ".join(val.errors) or "Validação determinística OK",
        "blockers": val.errors,
        "mode": "deterministic",
    }


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

    if is_linked(item["drug_ref_code"]):
        return sanitize_agent_result({
            "pending_id": pending_id,
            "entity_code": item["entity_code"],
            "drug_ref_code": item["drug_ref_code"],
            "status": "already_linked",
            "parent_entity_code": item["drug_ref_code"],
        })

    model = resolve_model(model)
    search = _deterministic_search(item)
    if use_llm and api_key:
        try:
            system = (PROMPTS_DIR / "search.md").read_text(encoding="utf-8")
            user = json.dumps({"queue_item": item}, ensure_ascii=False, indent=2)
            search = chat_json(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                api_key=api_key,
                model=model,
            )
            search["mode"] = "deepseek"
        except Exception:
            pass

    if use_llm and api_key:
        proposal = _llm_generate(item, search, api_key=api_key, model=model)
    else:
        proposal = _deterministic_generate(item, search)

    review = _review(proposal, api_key=api_key, model=model, use_llm=use_llm)
    validation = validate_entry(proposal)
    validation_dict = {
        "validation_passed": validation.ok and review.get("decision") != "reject",
        "errors": validation.errors,
        "warnings": validation.warnings,
    }

    result = sanitize_agent_result({
        "pending_id": pending_id,
        "entity_code": item["entity_code"],
        "drug_ref_code": item["drug_ref_code"],
        "steps": {
            "search": search,
            "proposal": proposal,
            "review": review,
            "validation": validation_dict,
        },
        "status": "applied" if validation_dict["validation_passed"] and apply else "awaiting_approval",
    })

    if validation_dict["validation_passed"] and apply:
        result["apply"] = apply_entry(proposal)
        item["status"] = "applied"
    return result


def run_batch(
    *,
    limit: int | None = 10,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = False,
    apply: bool = True,
) -> dict:
    queue = build_queue(limit=None)
    items = queue.get("items", [])
    if limit is not None and limit > 0:
        items = items[:limit]
    results = []
    errors = []
    for item in items:
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
    skipped = sum(1 for r in results if r.get("status") == "already_linked")
    return {
        "ok": len(errors) == 0,
        "queued": len(items),
        "processed": len(results),
        "applied": applied,
        "skipped": skipped,
        "errors": errors,
        "results": results,
    }
