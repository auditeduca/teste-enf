"""CKO profile of ISO 8000 master-data quality principles. Not ISO certification.

Licensed ISO clause text is never stored. Operational logic binds CKO fields to
the Brazilian PGDADOS programme (SGD/MGI) using catalog metadata only.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT, TOOLS_DIR
from .vault import MANIFEST_PATH, POINTERS_PATH
from .clinical_dict import CATALOG_PATH, DRIVE_MD_BLOCKERS, PILOT_CODES, clinical_dict_fields
from .who_i18n import WHO_OFFICIAL_SELECTOR, who_i18n_fields

OFFICIAL_CATALOG_URL = "https://www.iso.org/standard/80766.html"
PGDADOS_REF_URL = (
    "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/"
    "governancadedados/pgdados"
)
PGDADOS_REF = "MD-PGDADOS-001"
GLOSSARY_URL = (
    "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/"
    "governancadedados/glossario-de-termos-de-dados"
)
BINDING_PATH = ROOT / "cko_md" / "iso8000_pgdados_binding.json"
FIELD_DICT_PATH = ROOT / "cko_md" / "field_dictionary.json"

# Hub page (PGDADOS_REF_URL) names three implementation instruments. Part 3 PDF
# remains EVIDENCE_PENDING in MD-PGDADOS-001.
PGDADOS_INSTRUMENTS = (
    {
        "business_key": "PGD-INSTR-POLITICA",
        "name": "Política Interna de Governança de Dados",
        "guia_part": 1,
        "guia_ref": "RES-PGDADOS-GUIA-P1",
        "source_url": PGDADOS_REF_URL,
    },
    {
        "business_key": "PGD-INSTR-ESTRATEGIA",
        "name": "Estratégia de Dados",
        "guia_part": 2,
        "guia_ref": "RES-PGDADOS-GUIA-P2",
        "source_url": PGDADOS_REF_URL,
    },
    {
        "business_key": "PGD-INSTR-PLANO",
        "name": "Plano de Implementação do Programa de Governança de Dados",
        "guia_part": 3,
        "guia_ref": "RES-PGDADOS-GUIA-P3",
        "source_url": PGDADOS_REF_URL,
        "pdf_status": "EVIDENCE_PENDING",
    },
)

# Names OBSERVED on the PGDADOS glossary page (Cartilha Volume I citation).
# Definitions are NOT copied as product rules.
DATA_QUALITY_DIMENSIONS = (
    "integridade",
    "padronização",
    "precisão",
    "acurácia",
    "atualização",
    "acessibilidade",
    "confiabilidade",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _fld(
    business_key: str,
    name: str,
    purpose: str,
    *,
    layer: str,
    iso_test_id: str,
    pgdados_term: str,
    pgdados_instrument: str,
    extra: dict | None = None,
) -> dict:
    row = {
        "business_key": business_key,
        "name": name,
        "purpose": purpose,
        "layer": layer,
        "iso_test_id": iso_test_id,
        "iso_catalog_url": OFFICIAL_CATALOG_URL,
        "iso_clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        "pgdados_ref": PGDADOS_REF,
        "pgdados_term": pgdados_term,
        "pgdados_instrument": pgdados_instrument,
        "pgdados_source_url": GLOSSARY_URL if pgdados_term else PGDADOS_REF_URL,
        "pgdados_clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
        "certified": False,
        "iso_implemented": False,
    }
    if extra:
        row.update(extra)
    return row


def base_governance_fields() -> list[dict]:
    return [
        _fld(
            "FLD-PROVENANCE-SHA256",
            "provenance.sha256",
            "hash da cópia original",
            layer="L10",
            iso_test_id="ISO8000-CKO-PROVENANCE",
            pgdados_term="Metadados",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-PROVENANCE-URL",
            "provenance.url",
            "URL da fonte observada",
            layer="L10",
            iso_test_id="ISO8000-CKO-PROVENANCE",
            pgdados_term="Metadados",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-PROVENANCE-CAPTURED-AT",
            "provenance.captured_at",
            "instante da primeira captura",
            layer="L10",
            iso_test_id="ISO8000-CKO-PROVENANCE",
            pgdados_term="Metadados",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-VAULT-IMMUTABLE",
            "vault.immutable",
            "WORM: cópia inalterável",
            layer="L10",
            iso_test_id="ISO8000-CKO-WORM",
            pgdados_term="Integridade",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-LINEAGE-PROJECTION",
            "lineage.projection",
            "caminho da projeção frontend",
            layer="L270",
            iso_test_id="ISO8000-CKO-LINEAGE",
            pgdados_term="Metadados",
            pgdados_instrument="PGD-INSTR-ESTRATEGIA",
        ),
        _fld(
            "FLD-WORK-CLASS",
            "work.work_class",
            "ORIGINAL_CKO_CANDIDATE | THIRD_PARTY_SCALE | HOLD_OBJECT",
            layer="L140",
            iso_test_id="ISO8000-CKO-UNIQUENESS",
            pgdados_term="Dados Mestres",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-RIGHTS-STATUS",
            "rights.status",
            "DOCUMENTADO ≠ ASSURED",
            layer="L20",
            iso_test_id="ISO8000-CKO-NO-CERT-CLAIM",
            pgdados_term="Governança de dados",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-MASK-ID",
            "mask.mask_id",
            "máscara de norma aplicada na execução simples",
            layer="L20",
            iso_test_id="ISO8000-CKO-NO-CERT-CLAIM",
            pgdados_term="Governança de dados",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-A11Y-WCAG-EMAG",
            "a11y.wcag_emag",
            "WCAG nomeada; equivalente BR eMAG/LBI. Texto de cláusula W3C NÃO ingerido.",
            layer="L220",
            iso_test_id="ISO8000-CKO-PGDADOS-QUALITY-DIMS",
            pgdados_term="acessibilidade",
            pgdados_instrument="PGD-INSTR-ESTRATEGIA",
            extra={
                "w3c_standard_ingested": False,
                "br_equivalent": "eMAG 3.1 / LBI",
                "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
            },
        ),
        _fld(
            "FLD-SEO-OG-IMAGE",
            "seo.og_image",
            "Open Graph 1200×630 first-party. Cartões Drive COMPARE, não copiados.",
            layer="L290",
            iso_test_id="ISO8000-CKO-LINEAGE",
            pgdados_term="Metadados",
            pgdados_instrument="PGD-INSTR-ESTRATEGIA",
        ),
        _fld(
            "FLD-JSONLD-TYPE",
            "seo.jsonld_type",
            "JSON-LD WebSite/Organization. NUNCA MedicalOrganization.",
            layer="L300",
            iso_test_id="ISO8000-CKO-UNIQUENESS",
            pgdados_term="Dados de Referência",
            pgdados_instrument="PGD-INSTR-ESTRATEGIA",
        ),
    ]


def pgdados_bound_fields() -> list[dict]:
    fields = [
        _fld(
            "FLD-ISO8000-IDENTITY-BK",
            "identity.business_key",
            "Identidade operacional CKO-BK-1. UUIDv7 permanece HOLD.",
            layer="L10",
            iso_test_id="ISO8000-CKO-UNIQUENESS",
            pgdados_term="Dados Mestres",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-ISO8000-NO-SILENT-OVERWRITE",
            "identity.silent_overwrite",
            "FORBIDDEN: changeset → nova versão. Sem UPDATE silencioso.",
            layer="L10",
            iso_test_id="ISO8000-CKO-NO-SILENT-OVERWRITE",
            pgdados_term="Integridade",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-ISO8000-MASTER-RECORD",
            "md.master_record",
            "Registro mestre CKO (candidato em data/tools). Não é golden record ASSURED.",
            layer="L10",
            iso_test_id="ISO8000-CKO-UNIQUENESS",
            pgdados_term="Dados Mestres",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-ISO8000-REFERENCE-DATA",
            "md.reference_data",
            "Dados de referência (locale, entity type, unidade). Sem dump UCUM.",
            layer="L10",
            iso_test_id="ISO8000-CKO-FIELD-DICT",
            pgdados_term="Dados de Referência",
            pgdados_instrument="PGD-INSTR-ESTRATEGIA",
        ),
        _fld(
            "FLD-ISO8000-ATTRIBUTE",
            "md.attribute",
            "Atributo de dicionário (FLD-*). Binding inicia em MD.",
            layer="L10",
            iso_test_id="ISO8000-CKO-FIELD-DICT",
            pgdados_term="Atributos de referência",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-ISO8000-REFERENCE-RECORD",
            "md.reference_record",
            "Registro de referência: uma identidade, várias projeções.",
            layer="L10",
            iso_test_id="ISO8000-CKO-UNIQUENESS",
            pgdados_term="Registros de referência",
            pgdados_instrument="PGD-INSTR-POLITICA",
        ),
        _fld(
            "FLD-PGDADOS-POLITICA",
            "pgdados.politica_interna",
            "Instrumento PGDADOS: política interna. PDF metadado; texto não é regra CKO.",
            layer="L10",
            iso_test_id="ISO8000-CKO-PGDADOS-INSTRUMENTS",
            pgdados_term="Programa de Governança de Dados",
            pgdados_instrument="PGD-INSTR-POLITICA",
            extra={"pgdados_source_url": PGDADOS_REF_URL},
        ),
        _fld(
            "FLD-PGDADOS-ESTRATEGIA",
            "pgdados.estrategia_dados",
            "Instrumento PGDADOS: estratégia de dados.",
            layer="L10",
            iso_test_id="ISO8000-CKO-PGDADOS-INSTRUMENTS",
            pgdados_term="Programa de Governança de Dados",
            pgdados_instrument="PGD-INSTR-ESTRATEGIA",
            extra={"pgdados_source_url": PGDADOS_REF_URL},
        ),
        _fld(
            "FLD-PGDADOS-PLANO",
            "pgdados.plano_implementacao",
            "Instrumento PGDADOS: plano de implementação. PDF parte 3 EVIDENCE_PENDING.",
            layer="L10",
            iso_test_id="ISO8000-CKO-PGDADOS-INSTRUMENTS",
            pgdados_term="Programa de Governança de Dados",
            pgdados_instrument="PGD-INSTR-PLANO",
            extra={"pgdados_source_url": PGDADOS_REF_URL, "pdf_status": "EVIDENCE_PENDING"},
        ),
    ]
    dim_tests = {
        "integridade": "ISO8000-CKO-WORM",
        "padronização": "ISO8000-CKO-FIELD-DICT",
        "precisão": "ISO8000-CKO-FIELD-DICT",
        "acurácia": "ISO8000-CKO-PROVENANCE",
        "atualização": "ISO8000-CKO-LINEAGE",
        "acessibilidade": "ISO8000-CKO-PGDADOS-QUALITY-DIMS",
        "confiabilidade": "ISO8000-CKO-NO-CERT-CLAIM",
    }
    for dim in DATA_QUALITY_DIMENSIONS:
        slug = dim.replace("ã", "a").replace("ç", "c").replace("á", "a")
        fields.append(
            _fld(
                f"FLD-PGDADOS-QD-{slug.upper()}",
                f"pgdados.quality.{dim}",
                f"Dimensão de qualidade PGDADOS nomeada no glossário: {dim}. Definição não copiada.",
                layer="L10",
                iso_test_id=dim_tests[dim],
                pgdados_term=dim,
                pgdados_instrument="PGD-INSTR-ESTRATEGIA",
            )
        )
    return fields


def compose_field_dictionary() -> dict:
    fields = base_governance_fields() + pgdados_bound_fields() + who_i18n_fields() + clinical_dict_fields()
    keys = [item["business_key"] for item in fields]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate field business_key")
    return {
        "business_key": "MD-FIELD-DICT-001",
        "uuid": None,
        "status": "POPULATED",
        "maturity": "M2_CONFIGURED",
        "population": len(fields),
        "pgdados_ref": PGDADOS_REF,
        "iso_catalog_url": OFFICIAL_CATALOG_URL,
        "iso_implemented": False,
        "certified": False,
        "who_ref": "MD-WHO-I18N-001",
        "fields": fields,
        "note": (
            "Dicionário operacional CKO com binding PGDADOS, envelopes i18n WHO/OMS "
            "e catálogo COMPARE do dicionário clínico Drive. "
            "Não é cláusula ISO 8000. Não é dump ICD/ICNP/GHO. Não é certificação."
        ),
    }


def compose_binding(fields: list[dict]) -> dict:
    links = []
    for field in fields:
        links.append({
            "business_key": f"BIND-{field['business_key']}",
            "uuid": None,
            "field_ref": field["business_key"],
            "iso_test_id": field["iso_test_id"],
            "iso_catalog_url": field["iso_catalog_url"],
            "iso_clause_text": "CLAUSE_TEXT_UNAVAILABLE",
            "pgdados_ref": PGDADOS_REF,
            "pgdados_term": field.get("pgdados_term"),
            "pgdados_instrument": field.get("pgdados_instrument"),
            "pgdados_source_url": field.get("pgdados_source_url"),
            "pgdados_clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
            "replaces_iso_clause": False,
            "certified": False,
            "iso_implemented": False,
            "status": "BOUND",
        })
    return {
        "business_key": "MD-ISO8000-PGDADOS-BIND-001",
        "uuid": None,
        "status": "IMPLEMENTED",
        "assured": False,
        "publication": "HOLD",
        "certified": False,
        "iso_implemented": False,
        "iso_catalog_url": OFFICIAL_CATALOG_URL,
        "pgdados_ref": PGDADOS_REF,
        "pgdados_hub_url": PGDADOS_REF_URL,
        "glossary_url": GLOSSARY_URL,
        "instruments": list(PGDADOS_INSTRUMENTS),
        "data_quality_dimensions": [
            {
                "name": name,
                "source_url": GLOSSARY_URL,
                "source": "Cartilha Governança de Dados Volume I (nome no glossário)",
                "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
            }
            for name in DATA_QUALITY_DIMENSIONS
        ],
        "rule": (
            "Cada campo MD do perfil ISO 8000 CKO aponta a um termo/instrumento PGDADOS. "
            "PGDADOS não substitui texto de cláusula ISO licenciada."
        ),
        "population": len(links),
        "links": links,
        "evaluated_at": _now(),
    }


def evaluate_profile() -> dict:
    from .bootstrap import dump as dump_reg

    field_dict = compose_field_dictionary()
    dump_reg(FIELD_DICT_PATH, field_dict)
    binding = compose_binding(field_dict["fields"])
    _dump(BINDING_PATH, binding)

    pointers = _load(POINTERS_PATH)
    manifest = _load(MANIFEST_PATH)
    lineage = _load(ROOT / "cko_md" / "lineage_registry.json")
    identity = _load(ROOT / "cko_core" / "identity_policy.json")
    pgd = _load(ROOT / "cko_md" / "pgdados_program.json")
    tools = list(TOOLS_DIR.glob("*.json"))
    slugs = [path.stem for path in tools]
    unique_slugs = len(set(slugs)) == len(slugs)

    bound_ok = binding["population"] == field_dict["population"] and binding["population"] > 11
    every_link_has_pgdados = all(
        item.get("pgdados_ref") == PGDADOS_REF
        and item.get("iso_clause_text") == "CLAUSE_TEXT_UNAVAILABLE"
        and item.get("replaces_iso_clause") is False
        for item in binding["links"]
    )
    guia = {item.get("part"): item for item in (pgd.get("guia_parts") or [])}
    instruments_ok = (
        (guia.get(1) or {}).get("url")
        and (guia.get(2) or {}).get("url")
        and (guia.get(3) or {}).get("status") == "EVIDENCE_PENDING"
        and len(PGDADOS_INSTRUMENTS) == 3
    )
    dims_ok = [item["name"] for item in binding["data_quality_dimensions"]] == list(DATA_QUALITY_DIMENSIONS)
    who_ids = {item["business_key"] for item in who_i18n_fields()}
    dict_ids = {item["business_key"] for item in field_dict["fields"]}
    who_ok = who_ids.issubset(dict_ids) and all(
        item.get("iso_test_id") == "ISO8000-CKO-WHO-I18N"
        and item.get("pgdados_term") == "Interoperabilidade"
        and item.get("iso_clause_text") == "CLAUSE_TEXT_UNAVAILABLE"
        for item in field_dict["fields"]
        if item["business_key"] in who_ids
    ) and "pt-BR" not in {item["bcp47"] for item in WHO_OFFICIAL_SELECTOR}
    clin_ids = {item["business_key"] for item in clinical_dict_fields()}
    clin_ok = clin_ids.issubset(dict_ids) and all(
        item.get("iso_test_id") == "ISO8000-CKO-CLIN-DICT"
        and item.get("iso_clause_text") == "CLAUSE_TEXT_UNAVAILABLE"
        for item in field_dict["fields"]
        if item["business_key"] in clin_ids
    ) and not (TOOLS_DIR / "braden.json").exists()
    catalog = _load(CATALOG_PATH)
    if catalog:
        clin_ok = clin_ok and catalog.get("promoted_to_data_tools") is False
        clin_ok = clin_ok and catalog.get("identity_conflict", {}).get("adopt_uuid_v4") is False
        blocker_ids = {item[0] for item in DRIVE_MD_BLOCKERS}
        clin_ok = clin_ok and blocker_ids.issubset(dict_ids)
        clin_ok = clin_ok and all(
            (TOOLS_DIR / f"{slug}.json").exists() for slug in PILOT_CODES
        )

    tests = [
        {
            "id": "ISO8000-CKO-UNIQUENESS",
            "principle": "unique identification of master records",
            "pgdados_term": "Dados Mestres",
            "status": "PASS" if unique_slugs and identity.get("silent_id_invention") == "FORBIDDEN" else "FAIL",
            "observed": {"pilot_slugs": sorted(slugs), "uuid_generator": identity.get("uuid_generator_status")},
        },
        {
            "id": "ISO8000-CKO-PROVENANCE",
            "principle": "provenance of source bytes (url, captured_at, sha256)",
            "pgdados_term": "Metadados",
            "status": "PASS" if (pointers.get("pointers") or manifest.get("objects")) else "HOLD",
            "observed": {
                "vault_objects": manifest.get("population") or 0,
                "pointers": pointers.get("population") or 0,
            },
        },
        {
            "id": "ISO8000-CKO-WORM",
            "principle": "unaltered source copy retained",
            "pgdados_term": "Integridade",
            "status": "PASS" if manifest.get("objects") else "HOLD",
            "observed": {"worm": True, "population": manifest.get("population") or 0},
        },
        {
            "id": "ISO8000-CKO-LINEAGE",
            "principle": "source → master → projection completeness",
            "pgdados_term": "Metadados",
            "status": "PASS" if (lineage.get("complete_count") or 0) >= 4 else "HOLD",
            "observed": {
                "links": lineage.get("population") or 0,
                "complete_count": lineage.get("complete_count") or 0,
            },
        },
        {
            "id": "ISO8000-CKO-FIELD-DICT",
            "principle": "data dictionary for master attributes",
            "pgdados_term": "Atributos de referência",
            "status": "PASS" if (field_dict.get("population") or 0) > 11 else "HOLD",
            "observed": {"fields": field_dict.get("population") or 0},
        },
        {
            "id": "ISO8000-CKO-NO-SILENT-OVERWRITE",
            "principle": "no silent master-data overwrite",
            "pgdados_term": "Integridade",
            "status": "PASS" if identity.get("silent_id_invention") == "FORBIDDEN" else "FAIL",
            "observed": {"identity_scheme": identity.get("identity_scheme")},
        },
        {
            "id": "ISO8000-CKO-NO-CERT-CLAIM",
            "principle": "do not claim ISO certification without licensed evidence",
            "pgdados_term": "confiabilidade",
            "status": "PASS",
            "observed": {"certified": False, "clause_text": "CLAUSE_TEXT_UNAVAILABLE", "iso_implemented": False},
        },
        {
            "id": "ISO8000-CKO-PGDADOS-EXPLICIT",
            "principle": "Brazilian government operational reference is PGDADOS (SGD/MGI)",
            "pgdados_term": "Programa de Governança de Dados",
            "status": "PASS" if PGDADOS_REF_URL.endswith("/pgdados") else "FAIL",
            "observed": {
                "pgdados_hub_url": PGDADOS_REF_URL,
                "pgdados_ref": PGDADOS_REF,
                "replaces_iso_clause_text": False,
            },
        },
        {
            "id": "ISO8000-CKO-PGDADOS-INSTRUMENTS",
            "principle": "bind CKO profile to the three PGDADOS implementation instruments",
            "pgdados_term": "Programa de Governança de Dados",
            "status": "PASS" if instruments_ok else "HOLD",
            "observed": {
                "instruments": [item["business_key"] for item in PGDADOS_INSTRUMENTS],
                "guia_p3": (guia.get(3) or {}).get("status"),
            },
        },
        {
            "id": "ISO8000-CKO-PGDADOS-QUALITY-DIMS",
            "principle": "name PGDADOS data-quality dimensions from the official glossary",
            "pgdados_term": "Qualidade dos Dados",
            "status": "PASS" if dims_ok else "FAIL",
            "observed": {
                "count": len(DATA_QUALITY_DIMENSIONS),
                "names": list(DATA_QUALITY_DIMENSIONS),
                "glossary_url": GLOSSARY_URL,
            },
        },
        {
            "id": "ISO8000-CKO-PGDADOS-BINDING",
            "principle": "every ISO 8000 CKO field has a PGDADOS term/instrument binding",
            "pgdados_term": "Atributos de referência",
            "status": "PASS" if bound_ok and every_link_has_pgdados else "FAIL",
            "observed": {
                "fields": field_dict["population"],
                "links": binding["population"],
                "binding_ref": "MD-ISO8000-PGDADOS-BIND-001",
            },
        },
        {
            "id": "ISO8000-CKO-WHO-I18N",
            "principle": "WHO/OMS official selector modulates international i18n envelopes",
            "pgdados_term": "Interoperabilidade",
            "status": "PASS" if who_ok else "FAIL",
            "observed": {
                "who_fields": sorted(who_ids),
                "who_official": [item["bcp47"] for item in WHO_OFFICIAL_SELECTOR],
                "translation_gate": "HOLD",
                "icd_icnp_dump": "FORBIDDEN",
                "pt_br_in_who_selector": False,
            },
        },
        {
            "id": "ISO8000-CKO-CLIN-DICT",
            "principle": "Drive clinical dictionary modulates field/code envelopes without promoting scales",
            "pgdados_term": "Atributos de referência",
            "status": "PASS" if clin_ok else "FAIL",
            "observed": {
                "clin_fields": sorted(clin_ids),
                "braden_in_data_tools": (TOOLS_DIR / "braden.json").exists(),
                "adopt_uuid_v4": False,
                "abnt_clause_text": "CLAUSE_TEXT_UNAVAILABLE",
                "catalog_ref": "MD-CLIN-DICT-001",
            },
        },
    ]
    statuses = {item["status"] for item in tests}
    overall = "HOLD"
    if "FAIL" in statuses:
        overall = "FAIL"
    elif tests and all(item["status"] == "PASS" for item in tests):
        overall = "PASS_PROFILE_ONLY"
    profile = {
        "business_key": "MD-ISO8000-PROFILE-001",
        "uuid": None,
        "framework_ref": "FWK-ISO-8000-001",
        "mask_id": "MASK-TECH-STD",
        "name": "ISO 8000 — Data quality / master data (CKO profile)",
        "official_catalog_url": OFFICIAL_CATALOG_URL,
        "pgdados_hub_url": PGDADOS_REF_URL,
        "pgdados_ref": PGDADOS_REF,
        "glossary_url": GLOSSARY_URL,
        "binding_ref": "MD-ISO8000-PGDADOS-BIND-001",
        "government_reference": (
            "Referência operacional BR explícita: PGDADOS (SGD/MGI), "
            f"{PGDADOS_REF_URL}. Glossário: {GLOSSARY_URL}. "
            "Não substitui texto de cláusula ISO licenciada. Não é certificação ISO 8000."
        ),
        "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        "licensed_body": False,
        "certified": False,
        "iso_implemented": False,
        "cko_profile_applied": True,
        "status": overall,
        "epistemic_status": "PROPOSED",
        "note": (
            "Perfil CKO de unicidade, proveniência, WORM, lineage e dicionário, "
            "vinculado aos instrumentos e dimensões PGDADOS. "
            "Envelopes i18n WHO/OMS (L310) não ligam o seletor de idioma. "
            "NÃO é implantação certificada da ISO 8000."
        ),
        "tests": tests,
        "evaluated_at": _now(),
    }
    _dump(ROOT / "cko_md" / "iso8000_profile.json", profile)
    frameworks = _load(ROOT / "cko_core" / "framework_registry.json")
    items = list(frameworks.get("frameworks") or [])
    iso_fw = {
        "business_key": "FWK-ISO-8000-001",
        "name": "ISO 8000 Data quality / Master data",
        "role": "master data quality principles (uniqueness, provenance, completeness) as CKO profile mapping target",
        "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        "official_catalog_url": OFFICIAL_CATALOG_URL,
        "pgdados_hub_url": PGDADOS_REF_URL,
        "pgdados_ref": PGDADOS_REF,
        "glossary_url": GLOSSARY_URL,
        "binding_ref": "MD-ISO8000-PGDADOS-BIND-001",
        "certified": False,
        "iso_implemented": False,
        "cko_profile_ref": "MD-ISO8000-PROFILE-001",
        "mask_id": "MASK-TECH-STD",
        "status": "EVIDENCE_PENDING",
        "epistemic_status": "PROPOSED",
        "note": (
            "Norma técnica licenciada. Sem texto de cláusula. Perfil CKO ≠ certificação ISO. "
            "Referência operacional BR explícita: PGDADOS (SGD/MGI) /pgdados."
        ),
    }
    items = [item for item in items if item.get("business_key") != "FWK-ISO-8000-001"]
    items.append(iso_fw)
    frameworks["business_key"] = frameworks.get("business_key") or "REG-FRAMEWORK-001"
    frameworks["note"] = (
        "Frameworks de controle, não autoridade clínica. Texto de cláusula licenciada "
        "NÃO está neste repositório. ISO 8000 CKO vincula-se a PGDADOS; PGDADOS não substitui a ISO."
    )
    frameworks["frameworks"] = items
    _dump(ROOT / "cko_core" / "framework_registry.json", frameworks)
    return {
        "agent_id": "AG-ISO8000-PROFILE",
        "class": "MD",
        "role": "CHECKER",
        "status": overall,
        "certified": False,
        "iso_implemented": False,
        "cko_profile_applied": True,
        "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        "binding_ref": "MD-ISO8000-PGDADOS-BIND-001",
        "fields": field_dict["population"],
        "llm_used": False,
        "promotes_to_md": False,
        "tests": [{"id": item["id"], "status": item["status"]} for item in tests],
    }
