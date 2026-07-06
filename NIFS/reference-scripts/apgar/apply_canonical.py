"""Aplica canonical.json APGAR aos datasets + gera i18n 30 idiomas.

Uso:
  python scripts/apgar/apply_canonical.py
  python scripts/apgar/apply_canonical.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from apgar.i18n_catalog import LOCALE_MAP, all_locales  # noqa: E402
from dataset_io import read_envelope, write_envelope  # noqa: E402

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
APGAR_DIR = ROOT / "datasets" / "master-data" / "apgar"
CANON = json.loads((APGAR_DIR / "canonical.json").read_text(encoding="utf-8"))
SCL = CANON["artifacts"]["APGAR_SCL_001"]
COMPONENTS = SCL["components"]
COMPONENT_CODES = [c["code"] for c in COMPONENTS]


def apgar_fields_schema(density: str = "normal") -> dict:
    props = {}
    for c in COMPONENTS:
        props[c["code"]] = {
            "type": "integer",
            "minimum": 0,
            "maximum": 2,
            "title": c["label_pt"],
        }
    props["assessment_minute"] = {
        "type": "integer",
        "enum": SCL["timing_minutes"],
        "title": "Minuto de avaliação",
        "default": 1,
    }
    props["total_score"] = {
        "type": "number",
        "minimum": 0,
        "maximum": 10,
        "title": "Escore total",
        "readOnly": True,
    }
    required = COMPONENT_CODES + ["assessment_minute"]
    display = COMPONENT_CODES + ["assessment_minute", "total_score"]
    if density == "minimal":
        display = ["assessment_minute"] + COMPONENT_CODES[:3] + ["total_score"]
    return {
        "type": "object",
        "properties": props,
        "required": required,
        "_display_order": display,
    }


def patch_calculator_definitions(dry: bool) -> None:
    data = read_envelope("clinical/calculator_definitions.json")
    for rec in data["records"]:
        if rec.get("definition_code") != "CALC.TOOL.APGAR":
            continue
        rec["score_min"] = SCL["score_min"]
        rec["score_max"] = SCL["score_max"]
        rec["formula"] = SCL["formula"]
        rec["calculation_type"] = SCL["calculation_type"]
        rec["template_code"] = "TPL.SCALE_FORM"
        rec["parameters"] = [
            {"code": c["code"], "label": c["label_pt"], "type": "integer", "min": 0, "max": 2}
            for c in COMPONENTS
        ] + [{"code": "assessment_minute", "label": "Minuto", "type": "integer", "enum": SCL["timing_minutes"]}]
        rec["interpretation_bands"] = [
            {
                "min": b["min"],
                "max": b["max"],
                "label_pt": b["label_pt"],
                "label_en": b["label_en"],
                "severity": b["severity"],
                "action_pt": b["action_pt"],
            }
            for b in SCL["interpretation_bands"]
        ]
        rec["related_diagnosis_codes"] = ["NANDA.00162", "NANDA.00046"]
        rec["evidence_code"] = "EVID.GRADE.A"
        rec["evidence_level"] = "A"
        rec["timing_minutes"] = SCL["timing_minutes"]
        rec["clinical_purpose"] = SCL["clinical_purpose"]
        rec["updated_at"] = NOW
    if not dry:
        write_envelope("clinical/calculator_definitions.json", data)


def patch_field_configurations(dry: bool) -> None:
    data = read_envelope("metadata/field_configurations.json")
    densities = {
        "FIELD.TOOL.APGAR.STANDARD": "normal",
        "FIELD.TOOL.APGAR.URGENCY": "minimal",
        "FIELD.TOOL.APGAR.EVALUATION": "normal",
        "FIELD.TOOL.APGAR.ENTERPRISE": "normal",
        "FIELD.TOOL.APGAR.SIMULATION": "normal",
    }
    for rec in data["records"]:
        code = rec.get("field_config_code")
        if code not in densities:
            continue
        schema = apgar_fields_schema(densities[code])
        display = schema.pop("_display_order")
        rec["template_code"] = "TPL.SCALE_FORM"
        rec["fields_schema"] = schema
        rec["display_order"] = display
        rec["updated_at"] = NOW
    if not dry:
        write_envelope("metadata/field_configurations.json", data)


def patch_catalog(dry: bool) -> None:
    data = read_envelope("clinical/clinical_tools_catalog.json")
    for rec in data["records"]:
        if rec.get("tool_code") != "TOOL.APGAR":
            continue
        rec["related_diagnosis_codes"] = ["NANDA.00162", "NANDA.00046"]
        rec["template_code"] = "TPL.SCALE_FORM"
        rec["updated_at"] = NOW
    if not dry:
        write_envelope("clinical/clinical_tools_catalog.json", data)


def patch_master_proposal(dry: bool) -> None:
    path = ROOT / "datasets" / "metadata" / "master_code_sequence_proposal.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    locales = all_locales()
    i18n_block = {
        lc["locale_code"]: {"name": lc["name"], "description": lc["description"]}
        for lc in locales
    }
    evidence = {
        "grade": "A",
        "source_type": "primary_literature",
        "organization": "Columbia University",
        "citation": CANON["official_sources"][0]["citation"],
        "year": 1953,
        "doi": CANON["official_sources"][0]["doi"],
    }
    for concept in data.get("concepts", []):
        if concept.get("concept_code") != "APGAR":
            continue
        for art in concept.get("artifacts", []):
            if art.get("entity_code") in ("APGAR_SCL_001", "APGAR_FLA_001"):
                art["i18n"] = i18n_block
                art["evidence"] = evidence
                art["provenance_status"] = "official_source_linked"
                art["clinical_version"]["validated_year"] = 1953
                if art.get("entity_code") == "APGAR_SCL_001":
                    art["lifecycle"]["stage"] = "review"
    if not dry:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_i18n_file(dry: bool) -> None:
    payload = {
        "schema_version": "2026.2.2-apgar-pilot",
        "concept_code": "APGAR",
        "entity_code": "APGAR_SCL_001",
        "generated_at": NOW,
        "source_locale": "pt-BR",
        "target_language_count": len(LOCALE_MAP),
        "locales": all_locales(),
    }
    if not dry:
        out = APGAR_DIR / "i18n.json"
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_edges(dry: bool) -> None:
    path = ROOT / "datasets" / "ontology" / "apgar_edges.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["status"] = "review"
    for edge in data.get("edges", []):
        if edge.get("from", "").startswith("APGAR") or edge.get("to", "").startswith("APGAR"):
            edge["status"] = "review"
    if not dry:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_modules_completion(dry: bool) -> None:
    path = APGAR_DIR / "modules.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for m in data["modules"]:
        m["completion_pct"] = 100
        m["blocker"] = None
    data["overall_completion_pct"] = 100
    data["status"] = "REVIEW_READY"
    if not dry:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    dry = args.dry_run

    patch_calculator_definitions(dry)
    patch_field_configurations(dry)
    patch_catalog(dry)
    patch_master_proposal(dry)
    write_i18n_file(dry)
    patch_edges(dry)
    patch_modules_completion(dry)

    print("APGAR apply_canonical:", "dry-run" if dry else "applied")
    print(f"  i18n locales: {len(LOCALE_MAP)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
