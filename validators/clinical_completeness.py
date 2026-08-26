"""Clinical completeness: required SAE taxonomies must be resolved to promote."""

from __future__ import annotations

from engine.validate import iter_tool_files, load_tool


def _sae_status(entries: list, taxonomy: str) -> dict:
    if not entries:
        return {
            "id": f"SAE_REQUIRED_{taxonomy.upper()}",
            "pass": False,
            "blocking": True,
            "status": "HOLD",
            "reason": f"{taxonomy.upper()} ausente.",
        }
    unresolved = [item for item in entries if item.get("status", "CANDIDATE") != "RESOLVED"]
    if unresolved:
        codes = [item.get("code") or item.get("diagnosis") or item.get("intervention") or item.get("outcome") for item in unresolved]
        return {
            "id": f"SAE_REQUIRED_{taxonomy.upper()}",
            "pass": False,
            "blocking": True,
            "status": "HOLD",
            "reason": f"{taxonomy.upper()} candidato interno, sem fonte canônica/licenciada: {', '.join(str(c) for c in codes if c)}.",
        }
    return {
        "id": f"SAE_REQUIRED_{taxonomy.upper()}",
        "pass": True,
        "blocking": True,
        "status": "RESOLVED",
        "reason": f"{taxonomy.upper()} resolvido.",
    }


def evaluate_object(tool: dict) -> dict:
    kind = tool.get("kind")
    if kind not in {"calculator", "scale"}:
        return {
            "objectId": tool.get("slug"),
            "status": "NOT_APPLICABLE",
            "promotionAllowed": tool.get("status") != "hold",
            "checks": [],
            "blockingFindings": [],
        }
    sae = tool.get("sae") or {}
    checks = [
        _sae_status(sae.get("nanda") or [], "nanda"),
        _sae_status(sae.get("nic") or [], "nic"),
        _sae_status(sae.get("noc") or [], "noc"),
    ]
    blocking = [item for item in checks if item["blocking"] and not item["pass"]]
    status = "HOLD" if blocking else "PASS"
    return {
        "objectId": f"tool:{tool.get('slug')}",
        "status": status,
        "promotionAllowed": status == "PASS" and tool.get("status") == "published",
        "rule": "REQUIRED_CONTENT_MUST_BE_RESOLVED; HOLD/PENDING/UNKNOWN blocks promotion.",
        "checks": checks,
        "blockingFindings": [
            {"id": item["id"], "reason": item["reason"]} for item in blocking
        ],
    }


def evaluate_catalog() -> dict:
    results = [evaluate_object(load_tool(path)) for path in iter_tool_files()]
    blocking = []
    for result in results:
        blocking.extend(result.get("blockingFindings") or [])
        if result.get("status") == "HOLD":
            blocking.append({
                "id": "OBJECT_HOLD",
                "reason": f"{result.get('objectId')} permanece HOLD.",
            })
    status = "HOLD" if blocking else "PASS"
    return {
        "validatorId": "cko.clinical-completeness.validator.v1",
        "status": status,
        "promotionAllowed": False if blocking else True,
        "objects": results,
        "blockingFindings": blocking,
    }
