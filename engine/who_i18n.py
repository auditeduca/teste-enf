"""WHO/OMS sources modulate international i18n envelopes. Not a translation engine.

Observed who.int language selector: en, ar, zh, fr, ru, es.
GHO OData Indicator.Language observed EN on $top=1.
ICD-11 and ICNP pages observed; terms are not copied. translation_gate remains HOLD.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT

WHO_HOME = "https://www.who.int/"
WHO_ICNP = (
    "https://www.who.int/standards/classifications/other-classifications/"
    "international-classification-for-nursing-practice"
)
ICD11_HOME = "https://icd.who.int/en"
GHO_INDICATOR = "https://ghoapi.azureedge.net/api/Indicator?$top=1"
GHO_DIMENSION = "https://ghoapi.azureedge.net/api/Dimension"
NLM_ICD10CM = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=sepsis&maxList=1"
IRIS = "https://iris.who.int/"

# Codes OBSERVED in the who.int language <select> (2026-08-25).
WHO_OFFICIAL_SELECTOR = (
    {"bcp47": "en", "label_observed": "English"},
    {"bcp47": "ar", "label_observed": "العربية"},
    {"bcp47": "zh", "label_observed": "中文"},
    {"bcp47": "fr", "label_observed": "Français"},
    {"bcp47": "ru", "label_observed": "Русский"},
    {"bcp47": "es", "label_observed": "Español"},
)

DRIVE_ZIP_CODES = (
    "ar", "de", "en", "es", "fr", "hi", "id", "it", "ja", "ko",
    "nl", "pl", "pt", "ru", "sv", "tr", "uk", "vi", "zh",
)

GLOSSARY_URL = (
    "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/"
    "governancadedados/glossario-de-termos-de-dados"
)
PGDADOS_REF = "MD-PGDADOS-001"
OFFICIAL_CATALOG_URL = "https://www.iso.org/standard/80766.html"


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


def who_official_codes() -> set[str]:
    return {item["bcp47"] for item in WHO_OFFICIAL_SELECTOR}


def who_i18n_fields() -> list[dict]:
    """MD fields for i18n modulation. Still carry PGDADOS interoperability binding."""
    common = {
        "iso_catalog_url": OFFICIAL_CATALOG_URL,
        "iso_clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        "pgdados_ref": PGDADOS_REF,
        "pgdados_term": "Interoperabilidade",
        "pgdados_instrument": "PGD-INSTR-ESTRATEGIA",
        "pgdados_source_url": GLOSSARY_URL,
        "pgdados_clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
        "who_ref": "MD-WHO-I18N-001",
        "certified": False,
        "iso_implemented": False,
        "layer": "L310",
        "iso_test_id": "ISO8000-CKO-WHO-I18N",
    }
    rows = [
        ("FLD-I18N-BCP47", "i18n.bcp47", "Código BCP47 da identidade MD. pt ≠ pt-BR."),
        ("FLD-I18N-WHO-OFFICIAL", "i18n.who_official", "Locale candidato se código ∈ seletor who.int (6 oficiais observados)."),
        ("FLD-I18N-TRANSLATION-OBJECT", "i18n.translation_object", "Envelope de tradução por ferramenta+locale. Sem objeto MD → HOLD."),
        ("FLD-I18N-GHO-INDICATOR", "i18n.gho_indicator", "GHO OData: indicador/dimensão. Language observado EN no probe $top=1. Sem dump."),
        ("FLD-I18N-ICD-CODE", "i18n.icd_code", "Identidade de código ICD. Sem texto ICD-11 (licença WHO). NLM ICD-10-CM = busca US."),
        ("FLD-I18N-ICNP-CANDIDATE", "i18n.icnp_candidate", "CIPE/ICNP no WHO-FIC. Texto não copiado. OPT-C EVIDENCE_PENDING."),
        ("FLD-I18N-WHO-REGION", "i18n.who_region", "Dimensão GHO REGION (WHO regions). Geografia, não string de UI."),
    ]
    return [
        {
            "business_key": key,
            "name": name,
            "purpose": purpose,
            **common,
        }
        for key, name, purpose in rows
    ]


def compose_who_i18n() -> dict:
    adapters = _load(ROOT / "cko_md" / "api_adapter_registry.json").get("adapters") or []
    by_key = {item.get("business_key"): item for item in adapters}
    gho = by_key.get("API-WHO-GHO-INDICATOR") or {}
    icd10cm = by_key.get("API-NLM-CLINICALTABLES-ICD10CM") or {}
    official = who_official_codes()
    languages = []
    for code in DRIVE_ZIP_CODES:
        role = "WHO_OFFICIAL_CANDIDATE" if code in official else "DRIVE_ONLY"
        if code == "pt":
            role = "DRIVE_PT_NOT_WHO_SELECTOR"
        languages.append({
            "business_key": f"WHO-LANG-{code.upper()}",
            "uuid": None,
            "bcp47": code,
            "in_drive_zip": True,
            "in_who_int_selector": code in official,
            "modulation_role": role,
            "wired_to_frontend": False,
            "runtime": False,
            "note": (
                "pt no zip ≠ pt-BR de runtime. who.int não listou pt no seletor observado."
                if code == "pt"
                else None
            ),
        })
    return {
        "business_key": "MD-WHO-I18N-001",
        "uuid": None,
        "status": "REGISTERED",
        "implemented": True,
        "publication": "HOLD",
        "assured": False,
        "translation_gate": "HOLD",
        "wired_to_frontend": False,
        "layer": "L310",
        "agency_key": "AGY-WHO",
        "role": (
            "Modular conteúdo internacional: identidade de idioma WHO ∩ Drive zip. "
            "Não traduz calculadora. Não copia ICD/ICNP/GHO como texto canônico."
        ),
        "sources": [
            {
                "business_key": "SRC-WHO-INT-SELECTOR",
                "url": WHO_HOME,
                "observed": "language-selector options en ar zh fr ru es",
                "http_status": 200,
                "epistemic_status": "OBSERVED",
            },
            {
                "business_key": "SRC-WHO-GHO",
                "url": GHO_INDICATOR,
                "dimension_url": GHO_DIMENSION,
                "adapter_ref": "API-WHO-GHO-INDICATOR",
                "http_status": gho.get("http_status"),
                "epistemic_status": gho.get("epistemic_status") or "OBSERVED",
                "note": "Indicator.Language=EN no probe $top=1. Dimensão REGION/COUNTRY para recorte geográfico.",
            },
            {
                "business_key": "SRC-WHO-ICD11",
                "url": ICD11_HOME,
                "http_status": 200,
                "epistemic_status": "OBSERVED",
                "license": "ICD-11 License page named; texto não copiado.",
                "dump": "FORBIDDEN",
            },
            {
                "business_key": "SRC-WHO-ICNP",
                "url": WHO_ICNP,
                "http_status": 200,
                "epistemic_status": "OBSERVED",
                "nnn_option": "OPT-C-CIPE",
                "dump": "FORBIDDEN",
            },
            {
                "business_key": "SRC-NLM-ICD10CM",
                "url": NLM_ICD10CM,
                "adapter_ref": "API-NLM-CLINICALTABLES-ICD10CM",
                "http_status": icd10cm.get("http_status"),
                "epistemic_status": icd10cm.get("epistemic_status") or "OBSERVED",
                "note": "Classificação US relacionada. Não é ICD-11 OMS.",
            },
            {
                "business_key": "SRC-WHO-IRIS",
                "url": IRIS,
                "http_status": 200,
                "epistemic_status": "OBSERVED",
                "note": "HTML de descoberta. Não republica escala.",
            },
            {
                "business_key": "SRC-PAHO",
                "url": "https://www.paho.org/en",
                "http_status": 200,
                "epistemic_status": "OBSERVED",
                "note": "html lang en/es/fr observados. Português NÃO observado. Não inferir PAHO-pt.",
            },
        ],
        "who_official_languages": [
            {**item, "in_drive_zip": item["bcp47"] in DRIVE_ZIP_CODES, "source_url": WHO_HOME}
            for item in WHO_OFFICIAL_SELECTOR
        ],
        "drive_intersection": sorted(official & set(DRIVE_ZIP_CODES)),
        "drive_only": sorted(set(DRIVE_ZIP_CODES) - official),
        "languages": languages,
        "runtime_locale": "pt-BR",
        "runtime_not_in_who_selector": True,
        "rules": [
            "Um conceito → uma identidade MD → projeções por BCP47.",
            "Candidato i18n WHO = código no seletor who.int ∩ locales.zip.",
            "Não inferir pt → pt-BR.",
            "GHO/ICD/ICNP = SOURCE_DERIVED. Sem dump de termos.",
            "Frontend translation_gate HOLD até objeto MD de tradução + revisão humana.",
            "CIPE/ICNP não substitui NANDA sem decisão OPT-C.",
            "PAHO não observa pt; não inventar locale PAHO-pt.",
        ],
        "icd_icnp_gho_dump": "FORBIDDEN",
        "evaluated_at": _now(),
    }


def evaluate_who_i18n() -> dict:
    payload = compose_who_i18n()
    _dump(ROOT / "cko_md" / "who_i18n_modulation.json", payload)
    i18n = _load(ROOT / "cko_reg" / "i18n_profile.json")
    i18n.update({
        "business_key": i18n.get("business_key") or "REG-I18N-001",
        "uuid": None,
        "who_ref": "MD-WHO-I18N-001",
        "md_ref": "MD-LOCALE-REG-001",
        "translation_gate": "HOLD",
        "human_review_required": True,
        "wired_to_frontend": False,
        "display_language_runtime": "pt-BR",
        "who_official_intersection": payload["drive_intersection"],
        "rule": (
            "Locale é identidade MD. OMS/WHO modula candidatos internacionais (6 idiomas do seletor who.int). "
            "REG governa BCP47, rights e revisão humana. Frontend não cria locale."
        ),
    })
    notes = list(i18n.get("notes") or [])
    who_note = (
        "OMS who.int seletor observado: en ar zh fr ru es. Interseção com locales.zip = candidatos i18n. "
        "pt-BR runtime não está no seletor WHO. Tradução HOLD."
    )
    if who_note not in notes:
        notes.append(who_note)
    i18n["notes"] = notes
    _dump(ROOT / "cko_reg" / "i18n_profile.json", i18n)
    lang = _load(ROOT / "cko_md" / "language_locale_registry.json")
    lang["who_ref"] = "MD-WHO-I18N-001"
    lang["who_official_intersection"] = payload["drive_intersection"]
    lang["drive_only_not_who_official"] = payload["drive_only"]
    lang["related_drive_catalog"] = "MD-LOCALE-REG-001"
    lang["translation_gate"] = "HOLD"
    lang["wired_to_frontend"] = False
    _dump(ROOT / "cko_md" / "language_locale_registry.json", lang)
    drive_locales = _load(ROOT / "cko_md" / "locale_registry.json")
    if drive_locales:
        drive_locales["who_ref"] = "MD-WHO-I18N-001"
        drive_locales["who_official_intersection"] = payload["drive_intersection"]
        drive_locales["drive_only_not_who_official"] = payload["drive_only"]
        drive_locales["translation_gate"] = "HOLD"
        _dump(ROOT / "cko_md" / "locale_registry.json", drive_locales)
    return {
        "agent_id": "AG-WHO-I18N",
        "class": "MD",
        "role": "CHECKER",
        "status": "HOLD",
        "translation_gate": "HOLD",
        "wired_to_frontend": False,
        "who_official_count": len(payload["who_official_languages"]),
        "drive_intersection": payload["drive_intersection"],
        "llm_used": False,
        "promotes_to_md": False,
        "publication": "HOLD",
    }
