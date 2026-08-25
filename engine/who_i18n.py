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

# Codes OBSERVED in the who.int language <select> (2026-08-25). UN/WHO HQ six.
WHO_OFFICIAL_SELECTOR = (
    {"bcp47": "en", "label_observed": "English"},
    {"bcp47": "ar", "label_observed": "العربية"},
    {"bcp47": "zh", "label_observed": "中文"},
    {"bcp47": "fr", "label_observed": "Français"},
    {"bcp47": "ru", "label_observed": "Русский"},
    {"bcp47": "es", "label_observed": "Español"},
)

# Runtime local UI. WHO HQ official src remains `en` (Portuguese is not in the six).
RUNTIME_WHO_SRC = "en"
RUNTIME_LOCAL_BCP47 = "pt-BR"

WHO_PT_HOME = "https://www.who.int/pt"
WHO_PT_ABOUT = "https://www.who.int/pt/about"
WHO_LUSOPHONE = (
    "https://www.who.int/pt/teams/global-hiv-hepatitis-and-stis-programmes/"
    "strategies/lusophone-countries-collaboration-to-eliminate-hiv--hepatitis--stis-and-tb"
)
PAHO_PT = "https://www.paho.org/pt"
CLDR_DEFAULT_CONTENT = "https://cldr.unicode.org/translation/translation-guide-general/default-content"
BCP47_RFC = "https://www.rfc-editor.org/rfc/rfc5646"
RFC4647 = "https://www.rfc-editor.org/rfc/rfc4647"
XLIFF20 = "https://docs.oasis-open.org/xliff/xliff-core/v2.0/os/xliff-core-v2.0-os.html"

DESIGN_ZIP_7 = {
    "file_id": "1QS84_ws1yhCLCbHdPWyQDdbZoqI2Mo6Z",
    "title": "Design e arquivos das imagens (7).zip",
    "bytes": 121704396,
    "classification": "SKIP_BINARY_DUMP",
    "unzipped": False,
    "promoted_to_chrome": False,
    "note": (
        "Zip de design/imagens ≥20MB. Não unzip. Não é dicionário de locales. "
        "Mesmo tamanho em bytes que Design e arquivos das imagens (6).zip. "
        "Bandeiras do seletor permanecem EVIDENCE_PENDING."
    ),
}

# BCP47 = ISO 639-1 `pt` + ISO 3166-1 region. Not a dump of NIFS locales.json.
# who_lusophone_page: names counted on WHO_LUSOPHONE HTML this cycle.
LUSOPHONE_LOCALES = (
    {
        "bcp47": "pt-BR",
        "iso3166": "BR",
        "who_region": "AMRO",
        "label": "Brasil",
        "epistemic_status": "OBSERVED",
        "runtime": True,
        "wired_to_frontend": False,
        "who_lusophone_page": True,
        "source": "Runtime CKO html lang=pt-BR. WHO lusophone page names Brasil. PAHO Content-Language pt-br.",
    },
    {
        "bcp47": "pt-PT",
        "iso3166": "PT",
        "who_region": "EURO",
        "label": "Portugal",
        "epistemic_status": "OBSERVED",
        "runtime": False,
        "wired_to_frontend": False,
        "who_lusophone_page": True,
        "source": "WHO lusophone page names Portugal. Não inferir pt-PT → pt-BR.",
    },
    {
        "bcp47": "pt-AO",
        "iso3166": "AO",
        "who_region": "AFRO",
        "label": "Angola",
        "epistemic_status": "OBSERVED",
        "runtime": False,
        "wired_to_frontend": False,
        "who_lusophone_page": True,
        "source": "WHO lusophone page names Angola.",
    },
    {
        "bcp47": "pt-CV",
        "iso3166": "CV",
        "who_region": "AFRO",
        "label": "Cabo Verde",
        "epistemic_status": "OBSERVED",
        "runtime": False,
        "wired_to_frontend": False,
        "who_lusophone_page": True,
        "source": "WHO lusophone page names Cabo Verde.",
    },
    {
        "bcp47": "pt-MZ",
        "iso3166": "MZ",
        "who_region": "AFRO",
        "label": "Moçambique",
        "epistemic_status": "PROPOSED",
        "runtime": False,
        "wired_to_frontend": False,
        "who_lusophone_page": False,
        "source": "BCP47 pt+MZ. Não nomeado na página WHO lusophone deste ciclo.",
    },
    {
        "bcp47": "pt-GW",
        "iso3166": "GW",
        "who_region": "AFRO",
        "label": "Guiné-Bissau",
        "epistemic_status": "PROPOSED",
        "runtime": False,
        "wired_to_frontend": False,
        "who_lusophone_page": False,
        "source": "BCP47 pt+GW. Não nomeado na página WHO lusophone deste ciclo.",
    },
    {
        "bcp47": "pt-ST",
        "iso3166": "ST",
        "who_region": "AFRO",
        "label": "São Tomé e Príncipe",
        "epistemic_status": "PROPOSED",
        "runtime": False,
        "wired_to_frontend": False,
        "who_lusophone_page": False,
        "source": "BCP47 pt+ST. Não nomeado na página WHO lusophone deste ciclo.",
    },
    {
        "bcp47": "pt-TL",
        "iso3166": "TL",
        "who_region": "WPRO",
        "label": "Timor-Leste",
        "epistemic_status": "PROPOSED",
        "runtime": False,
        "wired_to_frontend": False,
        "who_lusophone_page": False,
        "source": "BCP47 pt+TL. Não nomeado na página WHO lusophone deste ciclo.",
    },
    {
        "bcp47": "pt-GQ",
        "iso3166": "GQ",
        "who_region": "AFRO",
        "label": "Guiné Equatorial",
        "epistemic_status": "PROPOSED",
        "runtime": False,
        "wired_to_frontend": False,
        "who_lusophone_page": False,
        "source": "BCP47 pt+GQ. Português é língua oficial; não nomeado na página WHO lusophone deste ciclo.",
    },
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


def who_local_key(who_src: str, local_bcp47: str) -> str:
    """XLIFF-style src+trg identity. WHO official src is not a BCP47 region tag."""
    return f"who.{who_src}+local.{local_bcp47}"


def runtime_who_local_key() -> str:
    return who_local_key(RUNTIME_WHO_SRC, RUNTIME_LOCAL_BCP47)


def lusophone_variant_rows() -> list[dict]:
    rows = []
    for item in LUSOPHONE_LOCALES:
        rows.append({
            **item,
            "uuid": None,
            "who_local_key": who_local_key(RUNTIME_WHO_SRC, item["bcp47"]),
            "who_pt_path_key": who_local_key("pt", item["bcp47"]),
            "paho_local_key": f"paho.pt-BR+local.{item['bcp47']}",
            "cldr_default_content_is_pt_br": True,
            "adopt_cldr_pt_fallback": False,
            "rfc4647_sibling_fallback": False,
        })
    return rows


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
        (
            "FLD-I18N-WHO-LOCAL-KEY",
            "i18n.who_local_key",
            "Chave composta who.{src}+local.{bcp47} (XLIFF srcLang/trgLang). Runtime who.en+local.pt-BR.",
        ),
        (
            "FLD-I18N-LOCAL-VARIANT",
            "i18n.local_variant",
            "Variante BCP47 lusófona (pt-BR ≠ pt-PT ≠ pt-AO). Sem fallback irmão RFC 4647. Sem ligar seletor.",
        ),
        (
            "FLD-I18N-PAHO-PT",
            "i18n.paho_pt",
            "OPAS/OMS português observado em paho.org/pt (Content-Language pt-br). Não é seletor who.int.",
        ),
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
                "note": "Hub EN. Português vive em SRC-PAHO-PT, não neste URL.",
            },
            {
                "business_key": "SRC-PAHO-PT",
                "url": PAHO_PT,
                "http_status": 200,
                "content_language": "pt-br",
                "epistemic_status": "OBSERVED",
                "note": "OPAS/OMS português. Content-Language pt-br. Não colapsar pt-PT/pt-AO neste valor.",
            },
            {
                "business_key": "SRC-WHO-PT-HOME",
                "url": WHO_PT_HOME,
                "http_status": 404,
                "epistemic_status": "OBSERVED",
                "note": "Raiz /pt 404. Português WHO não é locale site-wide. Não promover who.int/pt a seletor oficial.",
            },
            {
                "business_key": "SRC-WHO-PT-ABOUT",
                "url": WHO_PT_ABOUT,
                "http_status": 200,
                "html_lang": "pt",
                "epistemic_status": "OBSERVED",
                "note": "Caminho de conteúdo /pt/about. html lang=pt ≠ pt-BR. Fora do seletor das 6 oficiais.",
            },
            {
                "business_key": "SRC-WHO-LUSOPHONE",
                "url": WHO_LUSOPHONE,
                "http_status": 200,
                "html_lang": "pt",
                "epistemic_status": "OBSERVED",
                "names_counted": ["Angola", "Brasil", "Cabo Verde", "Portugal"],
                "note": "Página de colaboração lusófona. Não dump de termos clínicos.",
            },
            {
                "business_key": "SRC-DRIVE-DESIGN-ZIP-7",
                "url": f"https://drive.google.com/file/d/{DESIGN_ZIP_7['file_id']}/view",
                "file_id": DESIGN_ZIP_7["file_id"],
                "title": DESIGN_ZIP_7["title"],
                "bytes": DESIGN_ZIP_7["bytes"],
                "classification": DESIGN_ZIP_7["classification"],
                "unzipped": False,
                "epistemic_status": "OBSERVED",
                "note": DESIGN_ZIP_7["note"],
            },
        ],
        "who_official_languages": [
            {**item, "in_drive_zip": item["bcp47"] in DRIVE_ZIP_CODES, "source_url": WHO_HOME}
            for item in WHO_OFFICIAL_SELECTOR
        ],
        "drive_intersection": sorted(official & set(DRIVE_ZIP_CODES)),
        "drive_only": sorted(set(DRIVE_ZIP_CODES) - official),
        "languages": languages,
        "runtime_locale": RUNTIME_LOCAL_BCP47,
        "runtime_who_src": RUNTIME_WHO_SRC,
        "runtime_who_local_key": runtime_who_local_key(),
        "runtime_not_in_who_selector": True,
        "lusophone_variants": lusophone_variant_rows(),
        "lusophone_runtime": [item["bcp47"] for item in LUSOPHONE_LOCALES if item["runtime"]],
        "lusophone_hold": [item["bcp47"] for item in LUSOPHONE_LOCALES if not item["runtime"]],
        "practices": [
            {
                "id": "BCP47",
                "url": BCP47_RFC,
                "rule": "Identidade local = language-region (pt-BR, pt-PT, pt-AO). pt sozinho não nomeia país.",
            },
            {
                "id": "RFC4647-LOOKUP",
                "url": RFC4647,
                "rule": "Matching Lookup: mais longo primeiro. Sem fallback irmão (pt-AO ↛ pt-BR).",
            },
            {
                "id": "CLDR-DEFAULT-CONTENT",
                "url": CLDR_DEFAULT_CONTENT,
                "rule": "CLDR default content de pt é pt-BR (fato Unicode). CKO NÃO adota isso como fallback de produto.",
                "adopted": False,
            },
            {
                "id": "XLIFF-SRC-TRG",
                "url": XLIFF20,
                "rule": "Chave de envelope = who.{srcLang}+local.{trgLang}. Eixos separados: idioma WHO vs locale local.",
            },
            {
                "id": "WHO-UN-SIX",
                "url": WHO_HOME,
                "rule": "Seletor who.int = 6 oficiais ONU. Português é caminho de conteúdo (/pt/about), não oficial HQ.",
            },
            {
                "id": "PAHO-PT-BR",
                "url": PAHO_PT,
                "rule": "OPAS observa Content-Language pt-br. Não substitui variantes africanas/europeias.",
            },
        ],
        "design_zip": DESIGN_ZIP_7,
        "rules": [
            "Um conceito → uma identidade MD → projeções por BCP47.",
            "Chave runtime = who.{src_oficial}+local.{bcp47_variante}.",
            "Candidato i18n WHO HQ = código no seletor who.int ∩ locales.zip.",
            "Não inferir pt → pt-BR nem pt-PT → pt-BR nem pt-AO → pt-BR.",
            "CLDR default content pt=pt-BR é fato Unicode, não regra CKO.",
            "GHO/ICD/ICNP = SOURCE_DERIVED. Sem dump de termos.",
            "Frontend translation_gate HOLD até objeto MD de tradução + revisão humana.",
            "CIPE/ICNP não substitui NANDA sem decisão OPT-C.",
            "PAHO pt-br observado; não inventar PAHO-pt-PT.",
            "Zip de design/imagens SKIP_BINARY. Sem copiar bandeiras.",
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
        "display_language_runtime": RUNTIME_LOCAL_BCP47,
        "runtime_who_local_key": runtime_who_local_key(),
        "runtime_who_src": RUNTIME_WHO_SRC,
        "lusophone_hold": payload["lusophone_hold"],
        "who_official_intersection": payload["drive_intersection"],
        "rule": (
            "Locale é identidade MD. Chave de envelope who.{src}+local.{bcp47}. "
            "OMS/WHO HQ modula 6 oficiais; português local tem variantes BCP47. "
            "REG governa BCP47, rights e revisão humana. Frontend não cria locale."
        ),
    })
    notes = list(i18n.get("notes") or [])
    who_note = (
        "OMS who.int seletor observado: en ar zh fr ru es. Interseção com locales.zip = candidatos i18n. "
        "Runtime who.en+local.pt-BR. Variantes lusófonas catalogadas HOLD. PAHO Content-Language pt-br. "
        "who.int/pt raiz 404. Tradução HOLD."
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
    lang["runtime_who_local_key"] = runtime_who_local_key()
    lang["runtime_who_src"] = RUNTIME_WHO_SRC
    lang["adopt_cldr_pt_fallback"] = False
    locales = list(lang.get("locales") or [])
    by_bcp = {item.get("bcp47"): item for item in locales}
    territories = list(lang.get("territories") or [])
    by_iso = {item.get("iso3166"): item for item in territories}
    for row in payload["lusophone_variants"]:
        loc = by_bcp.get(row["bcp47"]) or {
            "business_key": f"LOC-{row['bcp47'].upper().replace('-', '-')}",
            "bcp47": row["bcp47"],
        }
        loc.update({
            "business_key": f"LOC-{row['bcp47'].upper()}",
            "bcp47": row["bcp47"],
            "epistemic_status": row["epistemic_status"],
            "runtime": row["runtime"],
            "wired_to_frontend": False,
            "who_local_key": row["who_local_key"],
            "who_region": row["who_region"],
            "source": row["source"],
        })
        by_bcp[row["bcp47"]] = loc
        terr = by_iso.get(row["iso3166"]) or {
            "business_key": f"TERR-{row['iso3166']}",
            "iso3166": row["iso3166"],
        }
        terr.update({
            "business_key": f"TERR-{row['iso3166']}",
            "iso3166": row["iso3166"],
            "epistemic_status": row["epistemic_status"],
            "note": row["source"],
        })
        by_iso[row["iso3166"]] = terr
    lang["locales"] = list(by_bcp.values())
    lang["territories"] = list(by_iso.values())
    lang["note"] = (
        "Runtime who.en+local.pt-BR. Variantes lusófonas são catálogo HOLD. "
        "locales.zip (19 códigos) não substitui este registry. Overlay WHO por AG-WHO-I18N."
    )
    _dump(ROOT / "cko_md" / "language_locale_registry.json", lang)
    _dump(ROOT / "cko_inbox" / "extracted" / "design_zip7_skip.json", {
        "business_key": "IPE-DESIGN-ZIP7-SKIP-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        **DESIGN_ZIP_7,
        "captured_at": payload["evaluated_at"],
    })
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
        "runtime_who_local_key": runtime_who_local_key(),
        "lusophone_hold": payload["lusophone_hold"],
        "llm_used": False,
        "promotes_to_md": False,
        "publication": "HOLD",
    }
