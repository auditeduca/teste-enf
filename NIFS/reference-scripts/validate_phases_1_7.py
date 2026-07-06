"""Referential integrity validator for NKOS Phases 1-7.

Generic checks (all phase 1-7 entities from canonical_registry):
  - JSON validity + envelope count == len(records)
  - Primary-key presence and uniqueness
  - Registry record count == actual file count
Targeted foreign-key checks (clinical/content relationships):
  - NNN linkages, drug interactions, calculator defs, locales
  - EntityRelation / EntityApplicability typed references
  - Content + ContentFragment/Version/Translation/ReviewCycle
Writes datasets/metadata/validation_phases_1_7_report.json; exits non-zero on error.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dataset_io import read_envelope

ROOT = Path(__file__).resolve().parent.parent / "datasets"
NOW_ISO = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(rel: str) -> dict:
    return read_envelope(rel)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks = 0

    def err(self, m: str) -> None:
        self.errors.append(m)

    def warn(self, m: str) -> None:
        self.warnings.append(m)

    def ok(self) -> None:
        self.checks += 1


def code_set(rel: str, field: str) -> set[str]:
    try:
        return {r[field] for r in load(rel)["records"] if r.get(field)}
    except (FileNotFoundError, KeyError):
        return set()


def registry_entities() -> list[dict]:
    reg = load("metadata/canonical_registry.json")["entities"]
    return [e for e in reg if (e.get("nkos_phase") is None or e.get("nkos_phase") <= 7)]


def generic_checks(rep: Report) -> dict[str, list[dict]]:
    rbe: dict[str, list[dict]] = {}
    for e in registry_entities():
        entity, rel, pk = e["entity"], e["file"], e.get("primary_key")
        try:
            data = load(rel)
        except FileNotFoundError:
            rep.err(f"{entity}: arquivo ausente ({rel})")
            continue
        except json.JSONDecodeError as ex:
            rep.err(f"{entity}: JSON inválido ({rel}): {ex}")
            continue
        records = data.get("records", [])
        rbe[entity] = records
        if "count" in data and data.get("count") != len(records):
            rep.err(f"{entity}: envelope count={data.get('count')} != len(records)={len(records)}")
        else:
            rep.ok()
        if e.get("records") is not None and e["records"] != len(records):
            rep.err(f"{entity}: registry records={e['records']} != arquivo={len(records)}")
        else:
            rep.ok()
        if pk and pk != "?":
            seen: set[str] = set()
            dups = 0
            for i, r in enumerate(records):
                key = r.get(pk)
                if key is None:
                    rep.err(f"{entity}: registro #{i} sem PK '{pk}'")
                    continue
                if key in seen:
                    dups += 1
                    if dups <= 3:
                        rep.err(f"{entity}: PK duplicada '{key}'")
                seen.add(key)
            rep.ok()
    return rbe


def fk_check(rep: Report, records: list[dict], field: str, valid: set[str], label: str, *, is_list: bool = False, optional: bool = True) -> None:
    missing = 0
    for r in records:
        val = r.get(field)
        if val is None or val == "":
            if not optional:
                rep.err(f"{label}: campo obrigatório '{field}' vazio")
            continue
        vals = val if (is_list and isinstance(val, list)) else [val]
        for v in vals:
            if v and v not in valid:
                missing += 1
                if missing <= 3:
                    rep.err(f"{label}.{field}='{v}' não resolve")
    if missing == 0:
        rep.ok()
    elif missing > 3:
        rep.err(f"{label}.{field}: +{missing - 3} referências quebradas adicionais")


def targeted_checks(rep: Report, rbe: dict[str, list[dict]]) -> None:
    dx = code_set("clinical/nursing_diagnoses.json", "diagnosis_code")
    nic = code_set("clinical/nursing_interventions.json", "intervention_code")
    noc = code_set("clinical/nursing_outcomes.json", "outcome_code")
    concepts = code_set("clinical/clinical_concepts.json", "concept_code")
    tools = code_set("clinical/clinical_tools_catalog.json", "tool_code")
    taxonomy = code_set("clinical/taxonomy.json", "taxonomy_code")
    master = code_set("master/master_entities.json", "entity_code")
    evidence = code_set("clinical/evidence.json", "evidence_code")
    drugs = code_set("clinical/drug_references.json", "drug_code")
    countries = code_set("global/countries.json", "country_code")
    languages = code_set("global/languages.json", "language_code")
    locales = code_set("global/locales.json", "locale_code")

    type_map = {
        "NursingDiagnosis": dx, "NursingIntervention": nic, "NursingOutcome": noc,
        "ClinicalConcept": concepts, "ClinicalTool": tools, "Taxonomy": taxonomy,
        "MasterEntity": master,
    }

    # Phase 1 — Locale FKs
    loc_records = load("global/locales.json")["records"]
    fk_check(rep, loc_records, "language_code", languages, "Locale")
    fk_check(rep, loc_records, "country_code", countries, "Locale")
    fk_check(rep, loc_records, "fallback_locale", locales, "Locale")

    # Phase 2/3 — clinical relationships
    nnn = load("clinical/nnn_linkages.json")["records"]
    fk_check(rep, nnn, "diagnosis_code", dx, "NNNLinkage", optional=False)
    fk_check(rep, nnn, "intervention_code", nic, "NNNLinkage", optional=False)
    fk_check(rep, nnn, "outcome_code", noc, "NNNLinkage", optional=False)
    fk_check(rep, nnn, "evidence_code", evidence, "NNNLinkage")

    di = load("clinical/drug_interactions.json")["records"]
    fk_check(rep, di, "drug_a_code", drugs, "DrugInteraction", optional=False)
    fk_check(rep, di, "drug_b_code", drugs, "DrugInteraction", optional=False)

    fk_check(rep, load("clinical/nursing_diagnoses.json")["records"], "evidence_code", evidence, "NursingDiagnosis")
    fk_check(rep, load("clinical/clinical_guidelines.json")["records"], "evidence_code", evidence, "ClinicalGuideline")

    cd = load("clinical/calculator_definitions.json")["records"]
    fk_check(rep, cd, "tool_code", tools, "CalculatorDefinition", optional=False)
    fk_check(rep, cd, "evidence_code", evidence, "CalculatorDefinition")
    fk_check(rep, cd, "related_diagnosis_codes", dx, "CalculatorDefinition", is_list=True)

    ni = load("clinical/nursing_interventions.json")["records"]
    fk_check(rep, ni, "related_tool_codes", tools, "NursingIntervention", is_list=True)
    nd = load("clinical/nursing_diagnoses.json")["records"]
    fk_check(rep, nd, "related_tool_codes", tools, "NursingDiagnosis", is_list=True)

    # Phase 3 — typed relations / applicability
    er = load("master/entity_relations.json")["records"]
    bad_src = bad_tgt = unknown = 0
    for r in er:
        st_, sc = r.get("source_entity_type"), r.get("source_code")
        tt, tc = r.get("target_entity_type"), r.get("target_code")
        if st_ in type_map:
            if sc and sc not in type_map[st_]:
                bad_src += 1
        else:
            unknown += 1
        if tt in type_map:
            if tc and tc not in type_map[tt]:
                bad_tgt += 1
        else:
            unknown += 1
    if bad_src:
        rep.err(f"EntityRelation: {bad_src} source_code não resolvem no tipo declarado")
    else:
        rep.ok()
    if bad_tgt:
        rep.err(f"EntityRelation: {bad_tgt} target_code não resolvem no tipo declarado")
    else:
        rep.ok()
    if unknown:
        rep.warn(f"EntityRelation: {unknown} extremidades com entity_type fora do mapa de tipos")

    ea = load("master/entity_applicability.json")["records"]
    bad_ea = bad_country = 0
    for r in ea:
        et, ec = r.get("entity_type"), r.get("entity_code")
        if et in type_map and ec and ec not in type_map[et]:
            bad_ea += 1
        cc = r.get("country_code")
        if cc and cc not in countries and cc not in ("ALL", "*", ""):
            bad_country += 1
    if bad_ea:
        rep.err(f"EntityApplicability: {bad_ea} entity_code não resolvem no tipo")
    else:
        rep.ok()
    if bad_country:
        rep.warn(f"EntityApplicability: {bad_country} country_code fora de Country (excl. ALL)")

    # Phase 7 — content graph
    contents = load("content/nkos/contents.json")["records"]
    content_codes = {c["content_code"] for c in contents if c.get("content_code")}
    source_sets = {
        "ClinicalTool": tools,
        "Quiz": code_set("education/quizzes.json", "quiz_code"),
        "ClinicalGuideline": code_set("clinical/clinical_guidelines.json", "guideline_code"),
        "InstitutionalProtocol": code_set("clinical/institutional_protocols.json", "protocol_code"),
        "Article": code_set("content/editorial/articles.json", "article_code"),
        "NursingDiagnosis": dx,
        "NursingIntervention": nic,
        "NursingOutcome": noc,
        "DrugReference": drugs,
        "LearningPath": code_set("education/learning_paths.json", "path_code"),
        "Competency": code_set("education/competencies.json", "competency_code"),
        "SimulatedExam": code_set("education/simulated_exams.json", "exam_code"),
        "Flashcard": code_set("education/flashcards.json", "flashcard_code"),
    }
    bad_src = 0
    for c in contents:
        se, sc = c.get("source_entity"), c.get("source_code")
        if se in source_sets and sc and sc not in source_sets[se]:
            bad_src += 1
    if bad_src:
        rep.err(f"Content: {bad_src} source_code não resolvem na entidade-fonte")
    else:
        rep.ok()

    for entity, rel in [
        ("ContentFragment", "content/nkos/content_fragments.json"),
        ("ContentVersion", "content/nkos/content_versions.json"),
        ("Translation", "content/i18n/translations.json"),
        ("ContentReviewCycle", "content/nkos/content_review_cycles.json"),
    ]:
        fk_check(rep, load(rel)["records"], "content_code", content_codes, entity, optional=False)


def main() -> int:
    rep = Report()
    rbe = generic_checks(rep)
    targeted_checks(rep, rbe)

    report = {
        "validated_at": NOW_ISO,
        "scope": "NKOS Phases 1-7",
        "entities_checked": len(rbe),
        "checks_passed": rep.checks,
        "error_count": len(rep.errors),
        "warning_count": len(rep.warnings),
        "errors": rep.errors,
        "warnings": rep.warnings,
        "passed": not rep.errors,
    }
    out = ROOT / "metadata" / "validation_phases_1_7_report.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("NKOS Phases 1-7 — referential integrity")
    print(f"  Entities checked: {len(rbe)}")
    print(f"  Checks passed:    {rep.checks}")
    print(f"  Errors:           {len(rep.errors)}")
    print(f"  Warnings:         {len(rep.warnings)}")
    for e in rep.errors[:20]:
        print(f"    ERROR: {e}")
    for w in rep.warnings[:10]:
        print(f"    warn: {w}")
    print(f"  Report: {out}")
    print(f"  Result: {'PASS' if report['passed'] else 'FAIL'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
