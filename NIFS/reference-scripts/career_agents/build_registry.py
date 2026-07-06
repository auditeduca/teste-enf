"""Registry de carreiras — Brasil + 195 países (empregos, cursos, trilhas, concursos)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "datasets" / "master-data" / "careers"

CAREER_TYPES = [
    ("JOB", "JobListing", "/empregos/", "datasets/community/job_listings.json"),
    ("CUR", "CourseListing", "/cursos/", "datasets/community/course_listings.json"),
    ("PATH", "CareerPath", "/carreiras/", "datasets/community/career_paths.json"),
    ("CON", "ConcursosHub", "/concursos/", None),
]

# Órgãos reguladores por país (amostra — agente expande com Grau A)
LICENSING_HINTS: dict[str, str] = {
    "BR": "COFEN/COREN",
    "US": "NCLEX/state board",
    "PT": "Ordem dos Enfermeiros",
    "GB": "NMC",
    "AU": "NMBA/AHPRA",
    "CA": "provincial college",
    "DE": "Landesprüfungsamt",
    "FR": "Ordre infirmier",
    "ES": "Consejo General de Enfermería",
    "JP": "MHLW nursing license",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_country_registry() -> dict:
    countries = json.loads((ROOT / "datasets/global/countries.json").read_text(encoding="utf-8"))
    items = []
    for c in countries.get("records", []):
        cc = c["country_code"]
        for art, entity, url, dataset in CAREER_TYPES:
            items.append({
                "entity_code": f"CAREER_{cc}_{art}_001",
                "country_code": cc,
                "country_name": c.get("name"),
                "artifact_type": art,
                "content_entity": entity,
                "canonical_url": url,
                "target_dataset": dataset,
                "licensing_hint": LICENSING_HINTS.get(cc, "national nursing council"),
                "who_region": c.get("who_region"),
                "status": "seeded" if cc == "BR" and dataset else "pending",
                "evidence_grade_required": "A",
                "agent_pipeline": ["search", "generate", "review", "validate"],
                "i18n_locales": 30,
            })
    return {
        "schema_version": "2026.2.7-careers",
        "generated_at": _now(),
        "total_items": len(items),
        "countries": len(countries.get("records", [])),
        "artifact_types": len(CAREER_TYPES),
        "items": items,
    }


def build_canonical() -> dict:
    return {
        "schema_version": "2026.2.7-careers",
        "program_code": "CAREERS_GLOBAL",
        "status": "PENDING_REVIEW",
        "description_pt": "Carreiras em enfermagem: empregos, cursos, trilhas e concursos — Brasil + 195 países, evidência Grau A.",
        "code_pattern": "CAREER_{CC}_{ART}_{NNN}",
        "evidence_policy": {
            "minimum_grade": "A",
            "required_fields": ["citation", "doi_or_url", "organization", "year"],
            "agent_search_rule": "WHO workforce, OECD health labour, national nursing councils, peer-reviewed workforce studies",
            "block_if_missing": True,
        },
        "coverage_targets": {
            "countries": 195,
            "artifact_types_per_country": 4,
            "languages": 30,
        },
        "dataset_bindings": {
            "country_registry": "datasets/master-data/careers/country_registry.json",
            "job_listings_br": "datasets/community/job_listings.json",
            "course_listings_br": "datasets/community/course_listings.json",
            "career_paths_br": "datasets/community/career_paths.json",
        },
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    canonical = build_canonical()
    registry = build_country_registry()
    (OUT / "canonical.json").write_text(json.dumps(canonical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "country_registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cov = {
        "generated_at": _now(),
        "countries": registry["countries"],
        "total_items": registry["total_items"],
        "br_seeded": sum(1 for i in registry["items"] if i["status"] == "seeded"),
        "pending": sum(1 for i in registry["items"] if i["status"] == "pending"),
    }
    (OUT / "coverage_report.json").write_text(json.dumps(cov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"careers registry: {registry['total_items']} items ({registry['countries']} países × 4 tipos)")
    return cov


if __name__ == "__main__":
    main()
