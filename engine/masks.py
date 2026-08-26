"""Apply norm masks with simple deterministic checks. No LLM in the execution path."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .paths import ROOT, TOOLS_DIR
from .vault import first_copy

MASKS_PATH = ROOT / "cko_reg" / "norm_masks.json"


def load_masks() -> dict:
    return json.loads(MASKS_PATH.read_text(encoding="utf-8"))


def _regex_present(text: str, pattern: str, flags: str = "") -> bool:
    flag = re.I if "I" in (flags or "") else 0
    return re.search(pattern, text, flag) is not None


def apply_mask(mask: dict, *, context: dict) -> dict:
    findings = []
    for check in mask.get("execution") or []:
        kind = check.get("kind")
        status = "HOLD"
        detail = None
        if kind == "vault_first_copy":
            logical_id = context.get("logical_id")
            copy = first_copy(logical_id) if logical_id else None
            if copy:
                status = "PASS"
                detail = copy.get("first_sha256")
            elif check.get("required"):
                status = "FAIL"
                detail = "first copy missing"
            else:
                status = "HOLD"
                detail = "optional first copy absent"
        elif kind == "regex_present":
            text = context.get("text") or ""
            ok = _regex_present(text, check["pattern"], check.get("flags") or "")
            status = "PASS" if ok else "FAIL"
        elif kind == "http_ok_or_inbox":
            status = "PASS" if context.get("inbox_present") or context.get("http_status") == 200 else "HOLD"
        elif kind == "no_clause_invention":
            status = "PASS" if context.get("clause_text") in {None, "CLAUSE_TEXT_UNAVAILABLE", "NOT_COPIED_AS_PRODUCT_RULE"} else "FAIL"
        elif kind == "clause_unavailable":
            status = "PASS" if context.get("clause_text") == "CLAUSE_TEXT_UNAVAILABLE" else "FAIL"
        elif kind == "metadata_only":
            status = "PASS" if not context.get("licensed_body") else "FAIL"
        elif kind == "no_pdf_ingest":
            media = (context.get("media_type") or "")
            status = "FAIL" if "pdf" in media.lower() else "PASS"
        elif kind == "cko_profile_not_certification":
            status = "PASS" if context.get("certified") is not True else "FAIL"
        elif kind == "internal_absent":
            text = context.get("internal_text") or ""
            hits = [token for token in check.get("tokens") or [] if token.lower() in text.lower()]
            status = "PASS" if not hits else "FAIL"
            detail = hits or None
        elif kind == "api_base_url_null":
            status = "PASS" if context.get("api_base_url") is None else "FAIL"
        elif kind == "no_rest_invention":
            status = "PASS" if not context.get("invented_rest") else "FAIL"
        elif kind == "pilot_in_data_tools":
            slug = context.get("slug")
            status = "PASS" if slug and (TOOLS_DIR / f"{slug}.json").exists() else "FAIL"
        elif kind == "lineage_complete":
            status = "PASS" if context.get("lineage_complete") else "HOLD"
        elif kind == "rights_not_assured":
            status = "PASS" if context.get("rights_status") != "ASSURED" else "FAIL"
        elif kind == "not_in_data_tools":
            slug = context.get("slug")
            status = "PASS" if slug and not (TOOLS_DIR / f"{slug}.json").exists() else "FAIL"
        elif kind == "quarantined":
            status = "PASS" if context.get("quarantined") is True else "HOLD"
        elif kind == "status_hold":
            status = "PASS" if str(context.get("status") or "").lower() == "hold" else "FAIL"
        elif kind == "no_formula":
            status = "PASS" if not context.get("has_formula") else "FAIL"
        else:
            status = "HOLD"
            detail = f"unknown check {kind}"
        findings.append({"kind": kind, "status": status, "detail": detail})
    statuses = {item["status"] for item in findings}
    overall = "HOLD"
    if findings and all(item["status"] == "PASS" for item in findings):
        overall = "PASS"
    elif "FAIL" in statuses:
        overall = "FAIL"
    return {
        "mask_id": mask.get("mask_id"),
        "norm_type": mask.get("norm_type"),
        "status": overall,
        "findings": findings,
        "execution_engine": "SIMPLE_DETERMINISTIC_ONLY",
        "llm_used": False,
    }


def apply_all(contexts: list[dict]) -> dict:
    catalog = load_masks()
    by_id = {item["mask_id"]: item for item in catalog.get("masks") or []}
    results = []
    for ctx in contexts:
        mask = by_id.get(ctx.get("mask_id"))
        if not mask:
            results.append({"mask_id": ctx.get("mask_id"), "status": "HOLD", "reason": "mask not found", "llm_used": False})
            continue
        results.append(apply_mask(mask, context=ctx))
    return {
        "business_key": "IPE-MASK-RUN-001",
        "uuid": None,
        "authoring_policy": catalog.get("authoring_policy"),
        "execution_policy": catalog.get("execution_policy"),
        "llm_as_checker": catalog.get("llm_as_checker"),
        "llm_used": False,
        "results": results,
        "population": len(results),
        "path": str((ROOT / "cko_inbox" / "extracted" / "mask_run.json").relative_to(ROOT)) if ROOT else None,
    }
