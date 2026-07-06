"""Country / locale partition helpers for Knowledge Platform API."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "datasets"

# 30 idiomas — ver scripts/global_expansion/site_locales.py
try:
    from global_expansion.site_locales import PRIMARY_SITE_LOCALE, SITE_LOCALES  # noqa: WPS433
except ImportError:
    SITE_LOCALES = ["pt-BR", "en", "es", "fr", "de", "it", "ja"]
    PRIMARY_SITE_LOCALE = {"pt": "pt-BR", "en": "en", "es": "es", "fr": "fr", "de": "de", "it": "it", "ja": "ja"}

COUNTRY_FRAMEWORKS: dict[str, list[str]] = {
    "BR": ["LGPD", "COFEN", "ANVISA", "FHIR R4/R5"],
    "US": ["HIPAA", "FHIR R4/R5"],
    "PT": ["GDPR", "RGPD", "FHIR R4/R5"],
    "ES": ["GDPR", "RGPD", "FHIR R4/R5"],
    "FR": ["GDPR", "RGPD", "FHIR R4/R5"],
    "DE": ["GDPR", "DSGVO", "FHIR R4/R5"],
    "IT": ["GDPR", "FHIR R4/R5"],
    "JP": ["APPI", "FHIR R4/R5"],
}

COUNTRY_ENTITY_FILES: dict[str, str] = {
    "ComplianceRule": "compliance_rules.json",
    "ContentRequest": "content_requests.json",
}

LOCALE_ENTITY_FILES: dict[str, str] = {
    "Workflow": "workflows.json",
    "Translation": "translations.json",
}

LOCALE_CONTENT_FILES: dict[str, str] = {
    "home_page": "home_page.json",
}

SUPPORTED_COUNTRIES = list(COUNTRY_FRAMEWORKS.keys())


def normalize_locale(locale: str) -> str:
    loc = (locale or "pt-BR").strip().replace("_", "-")
    low = loc.lower()
    if low in ("pt", "pt-br"):
        return "pt-BR"
    for site in SITE_LOCALES:
        if low == site.lower() or low.startswith(site.lower() + "-"):
            return site
    return loc


def country_entity_rel(entity_key: str, country: str) -> str:
    fname = COUNTRY_ENTITY_FILES[entity_key]
    return f"by-country/{country.upper()}/{fname}"


def locale_entity_rel(entity_key: str, locale: str) -> str:
    fname = LOCALE_ENTITY_FILES.get(entity_key)
    if not fname:
        raise KeyError(entity_key)
    return f"by-locale/{normalize_locale(locale)}/{fname}"


def locale_content_rel(content_key: str, locale: str) -> str:
    fname = LOCALE_CONTENT_FILES[content_key]
    return f"by-locale/{normalize_locale(locale)}/{fname}"


def resolve_entity_path(
    entity_key: str,
    meta: dict,
    *,
    country: str | None = None,
    locale: str | None = None,
) -> str:
    cc = (country or "").strip().upper()
    loc = normalize_locale(locale) if locale else ""

    if meta.get("partition") == "country" and cc:
        rel = country_entity_rel(entity_key, cc)
        if (DATASETS / rel).exists():
            return rel

    if meta.get("partition") == "locale" and loc:
        fname = LOCALE_ENTITY_FILES.get(entity_key)
        if fname:
            rel = f"by-locale/{normalize_locale(locale)}/{fname}"
            if (DATASETS / rel).exists():
                return rel

    return meta["path"]
