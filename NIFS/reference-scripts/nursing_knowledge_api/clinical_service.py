"""Clinical service — scales, calculators catalog, protocols, glossary."""
from __future__ import annotations

from paths import calculator_definitions, resolve_tool_id, tools_catalog

CATEGORY_PURPOSE = {
    "assessment_scales": "risk assessment",
    "dose_calculators": "dose or anthropometric calculation",
    "patient_safety": "patient safety assessment",
}

GLOSSARY_SEED = [
    { "term": "SAE", "definition_pt": "Sistematização da Assistência de Enfermagem", "category": "nursing_process" },
    { "term": "NANDA", "definition_pt": "North American Nursing Diagnosis Association — diagnósticos", "category": "taxonomy" },
    { "term": "NIC", "definition_pt": "Nursing Interventions Classification", "category": "taxonomy" },
    { "term": "LPP", "definition_pt": "Lesão por Pressão", "category": "clinical" },
    { "term": "COREN", "definition_pt": "Conselho Regional de Enfermagem", "category": "regulatory" },
]


def _scale_payload(tool: dict) -> dict:
    defs = {d["tool_code"]: d for d in calculator_definitions()}
    calc = defs.get(tool.get("tool_code"), {})
    return {
        "id": tool.get("tool_code", "").replace("TOOL.", "").lower(),
        "tool_code": tool.get("tool_code"),
        "name": tool.get("name"),
        "category": tool.get("domain", tool.get("category", "")).replace("_", " "),
        "purpose": CATEGORY_PURPOSE.get(tool.get("category"), "clinical assessment"),
        "evidence": [
            calc.get("evidence_code", "EVID.TYPE.PROTOCOL"),
            calc.get("reference_framework", "NKOS"),
        ],
        "related_tools": tool.get("related_diagnosis_codes", [])[:5],
        "related_protocols": [f"protocol:{tool.get('domain', 'general')}"],
        "tool_type": tool.get("tool_type"),
        "status": tool.get("status"),
    }


def list_scales(*, category: str | None = None) -> dict:
    scales = [t for t in tools_catalog() if t.get("tool_type") == "score" or t.get("category") == "assessment_scales"]
    if category:
        scales = [s for s in scales if category.lower() in (s.get("domain") or "").lower()]
    return {"ok": True, "count": len(scales), "scales": [_scale_payload(s) for s in scales[:50]]}


def get_scale(scale_id: str) -> dict:
    tool = resolve_tool_id(scale_id)
    if not tool:
        return {"ok": False, "error": "scale_not_found"}
    return {"ok": True, **_scale_payload(tool)}


def list_calculators() -> dict:
    calcs = [t for t in tools_catalog() if t.get("tool_type") in ("dose_calculation", "anthropometric", "score")]
    return {"ok": True, "count": len(calcs), "calculators": [
        {"id": c.get("tool_code", "").replace("TOOL.", "").lower(), "name": c.get("name"), "tool_code": c.get("tool_code")}
        for c in calcs[:50]
    ]}


def get_calculator(calc_id: str) -> dict:
    tool = resolve_tool_id(calc_id)
    if not tool:
        return {"ok": False, "error": "calculator_not_found"}
    defs = {d["tool_code"]: d for d in calculator_definitions()}
    calc = defs.get(tool.get("tool_code"))
    return {"ok": True, "tool": tool, "definition": calc}


def list_protocols() -> dict:
    domains = sorted({t.get("domain") for t in tools_catalog() if t.get("domain")})
    return {"ok": True, "protocols": [{"domain": d, "tools_count": sum(1 for t in tools_catalog() if t.get("domain") == d)} for d in domains]}


def glossary() -> dict:
    return {"ok": True, "count": len(GLOSSARY_SEED), "terms": GLOSSARY_SEED}
