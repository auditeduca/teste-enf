"""Gera proposta Master Data v2026.2.2 — padrão {CONCEITO}_{ARTEFATO}_{NNN}.

Lê:
  - website/pt/sitemap.xml (ferramentas publicadas)
  - datasets/clinical/clinical_tools_catalog.json (metadados NKOS)
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "website" / "pt" / "sitemap.xml"
CATALOG = ROOT / "datasets" / "clinical" / "clinical_tools_catalog.json"
OUT = ROOT / "datasets" / "metadata" / "master_code_sequence_proposal.json"

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Slug → código conceito (inglês, maiúsculas, underscore)
SLUG_TO_CONCEPT = {
    "apgar": "APGAR",
    "braden": "BRADEN",
    "glasgow": "GLASGOW",
    "gcs": "GLASGOW",
    "morse": "MORSE",
    "barthel": "BARTHEL",
    "katz": "KATZ",
    "news": "NEWS2",
    "news2": "NEWS2",
    "mews": "MEWS",
    "sofa": "SOFA",
    "apache2": "APACHE2",
    "apache": "APACHE2",
    "nihss": "NIHSS",
    "gotejamento": "DRIP_RATE",
    "imc": "BMI",
    "bmi": "BMI",
    "insulina": "INSULIN",
    "insulin": "INSULIN",
    "ballard": "BALLARD",
    "aldrete": "ALDRETE",
    "cam": "CAM_ICU",
    "richmond": "RASS",
    "rass": "RASS",
    "waterlow": "WATERLOW",
    "norton": "NORTON",
    "curb-65": "CURB65",
    "curb65": "CURB65",
    "qsofa": "QSOFA",
}

# Tipos de artefato (3 letras) — sufixo no entity_code
ARTIFACT_TYPES = {
    "SCL": "Escala clínica (instrumento validado)",
    "CAL": "Calculadora (fórmula, dose, conversão)",
    "FLA": "Flashcard / deck de estudo",
    "QIZ": "Quiz / questionário",
    "SIM": "Simulado clínico",
    "PRT": "Protocolo / checklist",
    "ART": "Artigo / conteúdo biblioteca",
    "AST": "Ativo visual (ícone, imagem)",
    "TMP": "Template UI",
}

# Domínio clínico opcional (metadado; prefixo no código só se aprovado futuramente)
DOMAIN_CODES = {
    "general": "GEN",
    "nursing": "NUR",
    "medical": "MED",
    "pharmacy": "PHR",
    "nutrition": "NUT",
    "safety": "SAF",
    "clinical": "CLIN",
}

FORCE_SCL = frozenset({"APGAR", "BRADEN", "GLASGOW", "MORSE", "RASS", "CAM_ICU", "BARTHEL", "KATZ", "NORTON", "WATERLOW", "NIHSS", "NEWS2", "MEWS", "SOFA", "APACHE2", "BALLARD", "ALDRETE", "CURB65", "QSOFA"})

FORCE_PRT = frozenset({"9RIGHTS"})

LIFECYCLE_TEMPLATE = {
    "stage": "draft",
    "approved_by": None,
    "approved_date": None,
    "deprecated_reason": None,
}

CLINICAL_VERSION_TEMPLATE = {
    "instrument_version": "1.0",
    "validated_year": None,
    "last_review": 2026,
}

EVIDENCE_TEMPLATE = {
    "grade": "A",
    "source_type": None,
    "organization": None,
    "citation": None,
    "year": None,
}

I18N_TEMPLATE = {
    "pt-BR": {"name": None, "description": None},
    "en-US": {"name": None, "description": None},
}


def slug_to_concept(slug: str) -> str:
    if slug in SLUG_TO_CONCEPT:
        return SLUG_TO_CONCEPT[slug]
    return re.sub(r"[^A-Za-z0-9]+", "_", slug).strip("_").upper()


def build_code(concept: str, artifact: str, seq: int) -> str:
    return f"{concept}_{artifact}_{seq:03d}"


def next_seq(codes: set[str], concept: str, artifact: str) -> int:
    prefix = f"{concept}_{artifact}_"
    nums = []
    for c in codes:
        if c.startswith(prefix):
            try:
                nums.append(int(c.rsplit("_", 1)[-1]))
            except ValueError:
                pass
    return max(nums, default=0) + 1


def classify_catalog_record(rec: dict, concept: str) -> str:
    if concept in FORCE_SCL:
        return "SCL"
    if concept in FORCE_PRT:
        return "PRT"
    cat = rec.get("category", "")
    tt = rec.get("tool_type", "")
    name = (rec.get("name") or "").lower()
    if tt == "protocol" or cat == "nursing_protocols":
        return "PRT"
    if cat == "assessment_scales" or tt == "score":
        return "SCL"
    if cat == "risk_stratification" and "calculator" not in name:
        return "SCL"
    if cat in ("dose_calculators", "hemodynamic_respiratory", "renal_nutrition_obstetric"):
        return "CAL"
    return "CAL"


def domain_code(rec: dict | None) -> str:
    if not rec:
        return "GEN"
    return DOMAIN_CODES.get(rec.get("domain", "general"), "GEN")


def build_entity_entry(
    *,
    code: str,
    concept: str,
    artifact: str,
    seq: int,
    slug: str | None = None,
    canonical_url: str | None = None,
    rec: dict | None = None,
    parent_entity_code: str | None = None,
    planned: bool = False,
    note: str | None = None,
) -> dict:
    entry = {
        "entity_code": code,
        "concept_code": concept,
        "domain": domain_code(rec),
        "artifact_type": artifact,
        "artifact_label": ARTIFACT_TYPES[artifact],
        "seq": seq,
        "evidence_grade_required": "A",
        "provenance_status": "pending_official_source",
        "lifecycle": dict(LIFECYCLE_TEMPLATE),
        "clinical_version": dict(CLINICAL_VERSION_TEMPLATE),
        "evidence": dict(EVIDENCE_TEMPLATE),
        "i18n": json.loads(json.dumps(I18N_TEMPLATE)),
    }
    if slug:
        entry["sitemap_slug"] = slug
    if canonical_url:
        entry["canonical_url"] = canonical_url
    if rec:
        entry["legacy_tool_code"] = rec.get("tool_code")
        entry["legacy_uuid"] = rec.get("uuid")
        entry["name"] = rec.get("name")
        entry["i18n"]["en-US"]["name"] = rec.get("name")
    elif slug:
        entry["name"] = slug.replace("-", " ").title()
    if parent_entity_code:
        entry["parent_entity_code"] = parent_entity_code
    if planned:
        entry["planned"] = True
    if note:
        entry["note"] = note
    return entry


def parse_sitemap_tools() -> list[dict]:
    root = ET.parse(SITEMAP).getroot()
    tools = []
    for url_el in root.findall("sm:url", NS):
        loc = url_el.find("sm:loc", NS)
        if loc is None or not loc.text:
            continue
        path = loc.text.replace("https://calculadorasdeenfermagem.com.br/", "").strip("/")
        if not path.startswith("ferramentas/") or path.count("/") != 1:
            continue
        slug = path.split("/", 1)[1]
        tools.append({
            "slug": slug,
            "concept": slug_to_concept(slug),
            "canonical_url": loc.text,
            "source": "sitemap",
        })
    return sorted(tools, key=lambda t: t["slug"])


def load_catalog_by_slug() -> dict[str, dict]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_slug = {}
    for rec in data.get("records", []):
        code = rec.get("tool_code", "")
        slug = code.replace("TOOL.", "").lower().replace("_", "-")
        slug_alt = code.replace("TOOL.", "").lower()
        by_slug[slug_alt] = rec
        by_slug[slug] = rec
        # match sitemap slug (apgar, braden, gcs...)
        simple = slug_alt.replace("-", "")
        by_slug[simple] = rec
    return by_slug


def main() -> None:
    sitemap_tools = parse_sitemap_tools()
    catalog = load_catalog_by_slug()

    allocated: set[str] = set()
    concepts: dict[str, dict] = {}
    catalog_entries: list[dict] = []
    review: list[dict] = []

    for tool in sitemap_tools:
        slug = tool["slug"]
        concept = tool["concept"]
        rec = catalog.get(slug) or catalog.get(slug.replace("-", ""))
        artifact = classify_catalog_record(rec, concept) if rec else ("SCL" if concept in FORCE_SCL else "CAL")

        seq = next_seq(allocated, concept, artifact)
        code = build_code(concept, artifact, seq)
        allocated.add(code)

        if concept not in concepts:
            concepts[concept] = {
                "concept_code": concept,
                "domain": domain_code(rec),
                "slug": slug,
                "canonical_url": tool["canonical_url"],
                "artifacts": [],
            }

        entry = build_entity_entry(
            code=code,
            concept=concept,
            artifact=artifact,
            seq=seq,
            slug=slug,
            canonical_url=tool["canonical_url"],
            rec=rec,
        )
        concepts[concept]["artifacts"].append(entry)
        catalog_entries.append(entry)

        # Artefatos derivados planejados (flashcard por conceito clínico principal)
        if artifact == "SCL" and rec:
            for _, art in (("flashcard", "FLA"),):
                dseq = next_seq(allocated, concept, art)
                dcode = build_code(concept, art, dseq)
                allocated.add(dcode)
                derived_entry = build_entity_entry(
                    code=dcode,
                    concept=concept,
                    artifact=art,
                    seq=dseq,
                    rec=rec,
                    parent_entity_code=code,
                    planned=True,
                    note=f"Deck flashcard vinculado à escala {code}",
                )
                concepts[concept]["artifacts"].append(derived_entry)
                catalog_entries.append(derived_entry)

    sample_edges = [
        {
            "from": "BRADEN_SCL_001",
            "to": "NANDA_00046",
            "relation_type": "supports_diagnosis",
            "weight": 1,
            "evidence_grade": "A",
            "status": "draft",
            "notes": "Exemplo — extrair de nursing_diagnoses.json na migração",
        },
        {
            "from": "APGAR_FLA_001",
            "to": "APGAR_SCL_001",
            "relation_type": "derived_from",
            "weight": 1,
            "status": "draft",
        },
    ]
    by_concept_artifact = {}
    for e in catalog_entries:
        if e.get("planned"):
            continue
        by_concept_artifact.setdefault(e["concept_code"], {})[e["artifact_type"]] = e["entity_code"]

    scl_count = sum(1 for e in catalog_entries if e["artifact_type"] == "SCL" and not e.get("planned"))
    cal_count = sum(1 for e in catalog_entries if e["artifact_type"] == "CAL" and not e.get("planned"))
    prt_count = sum(1 for e in catalog_entries if e["artifact_type"] == "PRT" and not e.get("planned"))

    proposal = {
        "status": "PENDING_REVIEW",
        "schema_version": "2026.2.2-draft",
        "generated_by": "scripts/draft_master_code_sequences.py",
        "review_instructions": (
            "Padrão v2026.2.2: {CONCEITO}_{ARTEFATO}_{NNN}. "
            "Tudo orbita o CONCEITO (APGAR, BRADEN…). "
            "Relações via edge layer (relation_dictionary.json) — sem entidade REL. "
            "PRT=protocolo/checklist; CAL exige fórmula+unidade. "
            "Aprovar antes de migrar datasets."
        ),
        "rules": {
            "code_pattern": "{CONCEPT}_{ARTIFACT}_{SEQ:03d}",
            "code_pattern_future_optional": "{DOMAIN}_{CONCEPT}_{ARTIFACT}_{SEQ:03d}",
            "concept": "Nome inglês maiúsculo da ferramenta (APGAR, BRADEN, DRIP_RATE)",
            "domain": "Metadado opcional (GEN, NUR, MED, PHR, NUT, SAF, CLIN) — prefixo no código só se aprovado",
            "artifact_suffix": "3 letras: SCL, CAL, FLA, QIZ, SIM, PRT, ART, AST, TMP",
            "scl_vs_cal_vs_prt": "SCL=escala | CAL=fórmula numérica | PRT=protocolo/checklist",
            "cal_to_scl": "CAL→SCL apenas via edge layer (implements, assesses) — nunca filho duplicado",
            "no_rel_entity": "Proibido entity_code REL_* — arestas em edges.json",
            "uuid": "UUID v4 imutável paralelo ao entity_code",
            "catalog_source": "website/pt/sitemap.xml → ferramentas/* + clinical_tools_catalog.json",
            "content_lineage": "Todo conteúdo referencia canonical_url do sitemap legacy/production",
            "evidence_min": "GRADE_A — fonte oficial primária obrigatória antes de published",
            "lifecycle_stages": ["draft", "review", "validated", "published", "deprecated"],
        },
        "artifact_types": ARTIFACT_TYPES,
        "relation_dictionary": "datasets/metadata/relation_dictionary.json",
        "edge_schema": "datasets/metadata/schemas/entity_edge.schema.json",
        "counts": {
            "concepts": len(concepts),
            "sitemap_tools": len(sitemap_tools),
            "scl_primary": scl_count,
            "cal_primary": cal_count,
            "prt_primary": prt_count,
            "total_codes": len(catalog_entries),
            "review": len(review),
        },
        "examples": {
            "apgar_scale": "APGAR_SCL_001",
            "apgar_flashcard": "APGAR_FLA_001",
            "braden_scale": "BRADEN_SCL_001",
            "drip_calculator": "DRIP_RATE_CAL_001",
            "nine_rights_protocol": "9RIGHTS_PRT_001",
        },
        "concepts": list(concepts.values()),
        "catalog": catalog_entries,
        "edge_layer": {
            "policy": "Relações são arestas (from, relation_type, to) — ver relation_dictionary.json",
            "sample_edges": sample_edges,
        },
        "sequences": {
            "SCL": [e for e in catalog_entries if e["artifact_type"] == "SCL"],
            "CAL": [e for e in catalog_entries if e["artifact_type"] == "CAL"],
            "PRT": [e for e in catalog_entries if e["artifact_type"] == "PRT"],
            "FLA": [e for e in catalog_entries if e["artifact_type"] == "FLA"],
            "REVIEW": review,
        },
    }

    OUT.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(
        f"concepts={proposal['counts']['concepts']} "
        f"SCL={scl_count} CAL={cal_count} PRT={prt_count} "
        f"FLA={len(proposal['sequences']['FLA'])} "
        f"total={proposal['counts']['total_codes']}"
    )


if __name__ == "__main__":
    main()
