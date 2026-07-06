"""Validador APGAR — piloto Master Data (somente ferramenta Apgar).

Uso:
  python scripts/apgar/validate_apgar.py
  python scripts/apgar/validate_apgar.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from apgar.field_registry import canonical, field_docs, modules  # noqa: E402
from dataset_io import read_envelope  # noqa: E402

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
REPORT_PATH = ROOT / "datasets" / "master-data" / "apgar" / "validation_report.json"


class Report:
    def __init__(self) -> None:
        self.errors: list[dict] = []
        self.warnings: list[dict] = []
        self.passed: list[dict] = []
        self.checks = 0

    def ok(self, field_id: str, message: str, **extra) -> None:
        self.checks += 1
        self.passed.append({"field_id": field_id, "status": "pass", "message": message, **extra})

    def err(self, field_id: str, message: str, **extra) -> None:
        self.checks += 1
        self.errors.append({"field_id": field_id, "status": "fail", "message": message, **extra})

    def warn(self, field_id: str, message: str, **extra) -> None:
        self.checks += 1
        self.warnings.append({"field_id": field_id, "status": "warn", "message": message, **extra})


def load_records(rel: str) -> list[dict]:
    try:
        return read_envelope(rel)["records"]
    except FileNotFoundError:
        return []


def find_by_pk(records: list[dict], pk: str, value: str) -> dict | None:
    for r in records:
        if r.get(pk) == value:
            return r
    return None


def check_identity(rep: Report, canon: dict) -> None:
    ident = canon["identity"]
    cat = find_by_pk(load_records("clinical/clinical_tools_catalog.json"), "tool_code", ident["legacy_tool_code"])
    if not cat:
        rep.err("APGAR.identity.concept_code", "TOOL.APGAR ausente em clinical_tools_catalog.json")
    else:
        rep.ok("APGAR.identity.concept_code", f"TOOL.APGAR presente: {cat.get('name')}")

    if cat and cat.get("uuid") != ident["legacy_uuid"]:
        rep.err(
            "APGAR.identity.legacy_uuid",
            f"UUID diverge: catalog={cat.get('uuid')} canonical={ident['legacy_uuid']}",
        )
    else:
        rep.ok("APGAR.identity.legacy_uuid", "UUID legado consistente")

    proposal_path = ROOT / "datasets" / "metadata" / "master_code_sequence_proposal.json"
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    apgar_concept = next((c for c in proposal.get("concepts", []) if c.get("concept_code") == "APGAR"), None)
    if not apgar_concept:
        rep.err("APGAR.identity.canonical_url", "Conceito APGAR ausente no master proposal")
        return

    scl = next((a for a in apgar_concept.get("artifacts", []) if a.get("entity_code") == "APGAR_SCL_001"), None)
    if scl and scl.get("canonical_url") == ident["canonical_url"]:
        rep.ok("APGAR.identity.canonical_url", "URL canônica alinhada")
    else:
        rep.err("APGAR.identity.canonical_url", "URL canônica diverge do canonical.json")


def check_clinical_instrument(rep: Report, canon: dict) -> None:
    scl = canon["artifacts"]["APGAR_SCL_001"]
    defn = find_by_pk(load_records("clinical/calculator_definitions.json"), "definition_code", canon["identity"]["legacy_definition_code"])
    if not defn:
        rep.err("APGAR.scl.score_max", "CALC.TOOL.APGAR ausente")
        return

    if defn.get("score_max") == scl["score_max"]:
        rep.ok("APGAR.scl.score_max", f"score_max={scl['score_max']}")
    else:
        rep.err(
            "APGAR.scl.score_max",
            f"score_max={defn.get('score_max')} — esperado {scl['score_max']} (Apgar 1953)",
            expected=scl["score_max"],
            actual=defn.get("score_max"),
        )

    if defn.get("score_min") == scl["score_min"]:
        rep.ok("APGAR.scl.score_max", f"score_min={scl['score_min']}")
    else:
        rep.err("APGAR.scl.score_max", f"score_min={defn.get('score_min')} — esperado 0")

    bands = defn.get("interpretation_bands") or []
    expected = scl["interpretation_bands"]
    if len(bands) == len(expected):
        match = all(
            b.get("min") == e["min"] and b.get("max") == e["max"]
            for b, e in zip(sorted(bands, key=lambda x: x["min"]), expected)
        )
        if match:
            rep.ok("APGAR.scl.interpretation_bands", "Faixas 0-3 / 4-6 / 7-10 corretas")
        else:
            rep.err(
                "APGAR.scl.interpretation_bands",
                "Faixas incorretas — dataset usa placeholders genéricos",
                actual=bands,
                expected=expected,
            )
    else:
        rep.err("APGAR.scl.interpretation_bands", f"{len(bands)} faixas — esperado 3", actual=bands)

    if defn.get("calculation_type") == scl["calculation_type"]:
        rep.ok("APGAR.scl.components", f"calculation_type={scl['calculation_type']}")
    else:
        rep.warn("APGAR.scl.components", f"calculation_type={defn.get('calculation_type')}")


def check_ui_fields(rep: Report, canon: dict) -> None:
    expected_codes = [c["code"] for c in canon["artifacts"]["APGAR_SCL_001"]["components"]]
    fc = find_by_pk(load_records("metadata/field_configurations.json"), "field_config_code", "FIELD.TOOL.APGAR.STANDARD")
    if not fc:
        rep.err("APGAR.scl.components", "FIELD.TOOL.APGAR.STANDARD ausente")
        return

    props = (fc.get("fields_schema") or {}).get("properties") or {}
    prop_keys = set(props.keys())
    if prop_keys >= set(expected_codes):
        rep.ok("APGAR.scl.components", f"UI tem componentes Apgar: {sorted(prop_keys & set(expected_codes))}")
    else:
        rep.err(
            "APGAR.scl.components",
            f"UI usa campos placeholder: {sorted(prop_keys)} — esperado {expected_codes}",
            actual=sorted(prop_keys),
            expected=expected_codes,
        )


def check_catalog(rep: Report, canon: dict) -> None:
    cat = find_by_pk(load_records("clinical/clinical_tools_catalog.json"), "tool_code", "TOOL.APGAR")
    if not cat:
        return
    if cat.get("definition_code") == canon["identity"]["legacy_definition_code"]:
        rep.ok("APGAR.identity.concept_code", "definition_code CALC.TOOL.APGAR ligado")
    else:
        rep.err("APGAR.identity.concept_code", f"definition_code={cat.get('definition_code')}")

    graph_nanda = canon["graph"]["primary_nanda"].replace("_", ".")
    related = cat.get("related_diagnosis_codes") or []
    if graph_nanda in related:
        rep.ok("APGAR.graph.primary_nanda", f"{graph_nanda} no catálogo")
    else:
        rep.warn(
            "APGAR.graph.primary_nanda",
            f"Catálogo lista {related} — grafo piloto usa {graph_nanda}",
        )


def check_graph(rep: Report, canon: dict) -> None:
    edges_path = ROOT / "datasets" / "ontology" / "apgar_edges.json"
    if not edges_path.exists():
        rep.err("APGAR.graph.edges", "apgar_edges.json ausente")
        return

    edges_doc = json.loads(edges_path.read_text(encoding="utf-8"))
    rel_dict = json.loads((ROOT / "datasets" / "metadata" / "relation_dictionary.json").read_text(encoding="utf-8"))
    allowed = set(rel_dict.get("relation_types", {}).keys())

    nanda_codes = {r["diagnosis_code"].replace(".", "_") for r in load_records("clinical/nursing_diagnoses.json")}
    nic_codes = {r["intervention_code"].replace(".", "_") for r in load_records("clinical/nursing_interventions.json")}
    noc_codes = {r["outcome_code"].replace(".", "_") for r in load_records("clinical/nursing_outcomes.json")}
    entity_codes = {"APGAR_SCL_001", "APGAR_FLA_001", "APGAR_RULE_001"}

    for edge in edges_doc.get("edges", []):
        rt = edge.get("relation_type")
        if rt not in allowed:
            rep.err("APGAR.graph.edges", f"relation_type inválido: {rt}")
            continue
        rep.ok("APGAR.graph.edges", f"{edge['from']} --{rt}--> {edge['to']}")

        for node, pool, label in [
            (edge["from"], entity_codes | nanda_codes | nic_codes | noc_codes, "from"),
            (edge["to"], entity_codes | nanda_codes | nic_codes | noc_codes, "to"),
        ]:
            normalized = node.replace("NANDA.", "NANDA_").replace("NIC.", "NIC_").replace("NOC.", "NOC_")
            if normalized not in pool and not node.startswith("APGAR_"):
                rep.warn("APGAR.graph.edges", f"FK {label} possivelmente ausente: {node}")

    primary = canon["graph"]["primary_nanda"]
    if any(e.get("to") == primary for e in edges_doc.get("edges", [])):
        rep.ok("APGAR.graph.primary_nanda", f"Arestas apontam para {primary}")
    else:
        rep.err("APGAR.graph.primary_nanda", f"Sem aresta para {primary}")


def check_evidence(rep: Report) -> None:
    proposal = json.loads((ROOT / "datasets" / "metadata" / "master_code_sequence_proposal.json").read_text(encoding="utf-8"))
    apgar = next((c for c in proposal.get("concepts", []) if c.get("concept_code") == "APGAR"), None)
    scl = next((a for a in (apgar or {}).get("artifacts", []) if a.get("entity_code") == "APGAR_SCL_001"), None)
    if not scl:
        rep.err("APGAR.evidence.grade", "APGAR_SCL_001 ausente no proposal")
        return

    ev = scl.get("evidence") or {}
    if ev.get("grade") == "A" and ev.get("citation"):
        rep.ok("APGAR.evidence.grade", "Evidência Grau A documentada")
    else:
        rep.warn(
            "APGAR.evidence.grade",
            "Grau A exigido mas citation/year ainda null — pending_official_source",
            actual=ev,
        )
    if ev.get("doi"):
        rep.ok("APGAR.evidence.grade", f"DOI presente: {ev.get('doi')}")


def check_i18n(rep: Report) -> None:
    i18n_path = ROOT / "datasets" / "master-data" / "apgar" / "i18n.json"
    if not i18n_path.exists():
        rep.err("APGAR.i18n.name_pt", "datasets/master-data/apgar/i18n.json ausente — rodar apply_canonical.py")
        return

    i18n_doc = json.loads(i18n_path.read_text(encoding="utf-8"))
    locales = i18n_doc.get("locales") or []
    expected_count = 30
    if len(locales) >= expected_count:
        rep.ok("APGAR.i18n.name_pt", f"{len(locales)} locales em i18n.json")
    else:
        rep.err("APGAR.i18n.name_pt", f"Apenas {len(locales)} locales — esperado {expected_count}")

    pt = next((lc for lc in locales if lc.get("locale_code") == "pt-BR"), None)
    if pt and pt.get("name") == "Escore de Apgar":
        rep.ok("APGAR.i18n.name_pt", "pt-BR.name correto")
    else:
        rep.err("APGAR.i18n.name_pt", f"pt-BR.name={pt.get('name') if pt else None}")

    for lc in locales:
        missing = [k for k in ("name", "description", "components") if not lc.get(k)]
        if missing:
            rep.err("APGAR.i18n.name_pt", f"{lc.get('locale_code')}: campos ausentes {missing}")

    proposal = json.loads((ROOT / "datasets" / "metadata" / "master_code_sequence_proposal.json").read_text(encoding="utf-8"))
    apgar = next((c for c in proposal.get("concepts", []) if c.get("concept_code") == "APGAR"), None)
    scl = next((a for a in (apgar or {}).get("artifacts", []) if a.get("entity_code") == "APGAR_SCL_001"), None)
    if scl:
        pt_prop = (scl.get("i18n") or {}).get("pt-BR") or {}
        if pt_prop.get("name") == "Escore de Apgar":
            rep.ok("APGAR.i18n.name_pt", "master proposal pt-BR sincronizado")
        else:
            rep.err("APGAR.i18n.name_pt", "master proposal i18n.pt-BR desatualizado")


def run_validation() -> Report:
    rep = Report()
    canon = canonical()
    check_identity(rep, canon)
    check_clinical_instrument(rep, canon)
    check_ui_fields(rep, canon)
    check_catalog(rep, canon)
    check_graph(rep, canon)
    check_evidence(rep)
    check_i18n(rep)
    return rep


def main() -> int:
    parser = argparse.ArgumentParser(description="Validador APGAR (piloto Master Data)")
    parser.add_argument("--json", action="store_true", help="Grava validation_report.json")
    args = parser.parse_args()

    rep = run_validation()
    mod = modules()

    summary = {
        "schema_version": "2026.2.2-apgar-pilot",
        "concept_code": "APGAR",
        "generated_at": NOW,
        "overall_completion_pct": mod.get("overall_completion_pct"),
        "checks_total": rep.checks,
        "passed": len(rep.passed),
        "warnings": len(rep.warnings),
        "errors": len(rep.errors),
        "pass_rate": round(len(rep.passed) / rep.checks * 100, 1) if rep.checks else 0,
        "modules": mod.get("modules"),
        "results": {
            "passed": rep.passed,
            "warnings": rep.warnings,
            "errors": rep.errors,
        },
        "field_catalog": field_docs().get("fields"),
    }

    print(f"=== Validador APGAR ===")
    print(f"Checks: {rep.checks} | Pass: {len(rep.passed)} | Warn: {len(rep.warnings)} | Fail: {len(rep.errors)}")
    print(f"Completion piloto: {mod.get('overall_completion_pct')}%")
    print()

    for e in rep.errors:
        print(f"FAIL [{e['field_id']}] {e['message']}")
    for w in rep.warnings:
        print(f"WARN [{w['field_id']}] {w['message']}")

    if args.json:
        REPORT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nRelatório: {REPORT_PATH.relative_to(ROOT)}")

    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
