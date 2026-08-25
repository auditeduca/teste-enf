"""Observed maturity panorama from MD/REG/assurance registries. No inferred PASS."""

from __future__ import annotations

import json
from pathlib import Path

from .paths import ROOT, TOOLS_DIR
from .validate import iter_tool_files


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_maturity() -> dict:
    from .bootstrap import evaluate_layer_registry, layer_records

    layers = layer_records()
    by_maturity: dict[str, int] = {}
    for layer in layers:
        key = str(layer.get("maturity") or "UNKNOWN")
        by_maturity[key] = by_maturity.get(key, 0) + 1
    tools = list(iter_tool_files(TOOLS_DIR))
    hold_tools = 0
    for path in tools:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if str(payload.get("status")).lower() == "hold":
            hold_tools += 1
    locales = _load(ROOT / "cko_md" / "locale_registry.json")
    agents = _load(ROOT / "cko_assurance" / "agent_registry.json")
    caat = _load(ROOT / "cko_assurance" / "caat_registry.json")
    ipe = _load(ROOT / "cko_assurance" / "ipe_registry.json")
    tokens = _load(ROOT / "cko_core" / "design_token_registry.json")
    drive = _load(ROOT / "cko_inbox" / "drive" / "INVENTORY.json")
    mockups = _load(ROOT / "admin" / "mockup_reference_map.v1.json")
    frameworks = _load(ROOT / "cko_core" / "framework_registry.json")
    header_token = next(
        (item for item in (tokens.get("tokens") or []) if item.get("business_key") == "TOK-SHELL-HEADER-BG"),
        {},
    )
    font_token = next(
        (item for item in (tokens.get("tokens") or []) if item.get("business_key") == "TOK-FONT-SANS"),
        {},
    )
    fonts_present = (ROOT / "assets" / "fonts" / "inter" / "inter-regular.woff2").exists()
    return {
        "business_key": "IPE-MATURITY-PANORAMA-001",
        "uuid": None,
        "status": "REGISTERED",
        "maturity": "M1_SCHEMA_DEFINED",
        "epistemic_status": "OBSERVED",
        "release": "HOLD",
        "chain": "CKO-MD → CKO-REG → projection → renderer → frontend",
        "rule": "DOCUMENTADO ≠ IMPLEMENTADO ≠ VALIDADO ≠ ASSURED ≠ PUBLICADO. SEM EVIDÊNCIA → HOLD.",
        "layers": {
            "population": len(layers),
            "by_maturity": by_maturity,
            "note": "EXISTS no registry. Nenhuma camada ASSURED.",
        },
        "domain_candidates": {
            "tools": len(tools),
            "hold": hold_tools,
            "braden_in_data_tools": (TOOLS_DIR / "braden.json").exists(),
        },
        "agents": {
            "registry_status": agents.get("status"),
            "implemented": agents.get("implemented"),
            "publication_implemented": agents.get("publication_implemented"),
            "population": agents.get("population"),
            "classes": len(agents.get("classes") or []),
        },
        "caat": {
            "registry_implemented": caat.get("implemented"),
            "registered_caats": len(caat.get("caats") or []),
            "layer_count_44": evaluate_layer_registry(),
        },
        "ipe": {
            "registry_implemented": ipe.get("implemented"),
            "carr": ipe.get("carr") or [],
            "ipes": len(ipe.get("ipes") or []),
            "rule": ipe.get("rule"),
        },
        "locales": {
            "population": locales.get("population"),
            "codes": locales.get("zip_codes_observed") or [],
            "stems_only": locales.get("stems_only") or [],
            "wired_to_frontend": False,
            "display_language_runtime": locales.get("display_language_runtime"),
        },
        "design_system": {
            "official_ds_status": tokens.get("official_ds_status"),
            "header_compare": header_token.get("compare"),
            "fonts": font_token.get("compare") or ("RESTORED" if fonts_present else "GAP"),
            "header_min_height": "96px desktop / 60px mobile",
            "language_selector": "46px HOLD",
        },
        "frameworks": [
            {
                "business_key": item.get("business_key"),
                "name": item.get("name"),
                "clause_text": item.get("clause_text"),
                "epistemic_status": item.get("epistemic_status"),
            }
            for item in (frameworks.get("frameworks") or [])
        ],
        "drive": {
            "inventory_status": drive.get("status"),
            "observed_artifacts": len(drive.get("artifacts") or []),
            "not_ingested": drive.get("not_ingested") or [],
        },
        "mockups": {
            "status": mockups.get("status"),
            "use": mockups.get("use"),
            "population": len(mockups.get("references") or []),
        },
        "next_gate": [
            "Revisão humana dos 1516 HTML SOURCE_DERIVED antes de qualquer promoção MD.",
            "Locales: BCP47 + revisão humana; não ligar 19 códigos só porque o zip existe.",
            "Não promover HTML Drive/pages_full (braden.html etc.) a golden MD.",
            "IPE CARR: RELIABLE=FAIL para publicação; sem reliance neste lote.",
            "Release clínica permanece HOLD. Agentes de extração não autorizam release.",
        ],
    }
