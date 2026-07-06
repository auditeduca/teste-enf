"""Gera i18n mundial: 30 idiomas, home localizada, preferências por país, códigos entity."""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from site_locales import I18N_PAGE_TYPES, SITE_LOCALES, SITE_LOCALE_META

ROOT = Path(__file__).resolve().parent.parent.parent
EXP = ROOT / "datasets" / "master-data" / "global-expansion"
BY_LOCALE = ROOT / "datasets" / "by-locale"
CANONICAL_HOME = ROOT / "datasets" / "content" / "site" / "home_page.json"
PROFILE_CONFIG = ROOT / "website" / "assets" / "data" / "user-profile-config.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _write(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_i18n_code_registry() -> dict:
    items = []
    for loc in SITE_LOCALES:
        lang = SITE_LOCALE_META[loc]["language_code"].upper()
        for page_code, url, entity in I18N_PAGE_TYPES:
            items.append({
                "entity_code": f"I18N_{lang}_{page_code}_001",
                "site_locale": loc,
                "language_code": SITE_LOCALE_META[loc]["language_code"],
                "page_type": page_code,
                "canonical_url": url,
                "content_entity": entity,
                "status": "pending",
                "i18n_status": "scaffold",
                "evidence_grade_required": "A",
                "agent_pipeline": ["search", "generate", "review", "validate"],
            })
    return {
        "schema_version": "2026.2.7-global-i18n",
        "generated_at": _now(),
        "total_items": len(items),
        "site_locales": len(SITE_LOCALES),
        "page_types": len(I18N_PAGE_TYPES),
        "items": items,
    }


def _scaffold_home(locale: str, template: dict) -> dict:
    doc = deepcopy(template)
    doc["locale"] = locale
    doc["generated_at"] = _now()
    doc["i18n_status"] = "scaffold"
    doc["content_source"] = "I18N_SCAFFOLD"
    doc["entity_code"] = f"I18N_{SITE_LOCALE_META[locale]['language_code'].upper()}_HOME_001"
    return doc


def ensure_locale_homes() -> dict[str, str]:
    canonical = _read(CANONICAL_HOME)
    en_home = _read(BY_LOCALE / "en" / "home_page.json") or canonical
    created: dict[str, str] = {}
    for loc in SITE_LOCALES:
        path = BY_LOCALE / loc / "home_page.json"
        if path.is_file():
            doc = _read(path)
            if doc.get("i18n_status") in ("translated", "reviewed"):
                created[loc] = doc.get("i18n_status", "translated")
                continue
        template = en_home if loc != "pt-BR" else canonical
        _write(path, _scaffold_home(loc, template))
        created[loc] = "scaffold"
    return created


def build_country_audience_preferences() -> dict:
    countries = _read(ROOT / "datasets/global/countries.json").get("records", [])
    locales = _read(ROOT / "datasets/global/locales.json").get("records", [])
    locale_by_cc: dict[str, list[str]] = {}
    for loc in locales:
        cc = loc.get("country_code")
        if cc:
            locale_by_cc.setdefault(cc, []).append(loc["locale_code"])

    emphasis_by_income = {
        "High income": "clinical_tools",
        "Upper middle income": "clinical_tools",
        "Lower middle income": "education",
        "Low income": "education",
    }

    records = []
    for c in countries:
        cc = c["country_code"]
        income = c.get("income_level") or "Upper middle income"
        records.append({
            "entity_code": f"{cc}_AUDIENCE_001",
            "country_code": cc,
            "name": c.get("name"),
            "who_region": c.get("who_region"),
            "default_locale": locale_by_cc.get(cc, ["en-" + cc])[0] if locale_by_cc.get(cc) else f"en-{cc}",
            "locales_available": locale_by_cc.get(cc, []),
            "regulatory_zone": c.get("regulatory_zone"),
            "measurement_system": c.get("measurement_system"),
            "homepage_emphasis": emphasis_by_income.get(income, "education"),
            "career_hubs": {
                "jobs": f"/empregos/?country={cc}",
                "courses": f"/cursos/?country={cc}",
                "careers": f"/carreiras/?country={cc}",
            },
            "profile_default": "profissional" if income == "High income" else "estudante",
            "evidence_grade_required": "A",
        })

    return {
        "schema_version": "2026.2.7-global-audience",
        "generated_at": _now(),
        "total_countries": len(records),
        "records": records,
    }


def build_locale_profile_overrides(home_status: dict[str, str]) -> dict:
    base = _read(PROFILE_CONFIG)
    profiles_base = base.get("profiles", {})
    locales_out: dict[str, dict] = {}

    for loc in SITE_LOCALES:
        home = _read(BY_LOCALE / loc / "home_page.json")
        loc_profiles = deepcopy(profiles_base)
        hero_sub = home.get("hero", {}).get("subtitle")
        search = home.get("search", {})
        if hero_sub:
            for key in loc_profiles:
                loc_profiles[key]["hero_subtitle"] = hero_sub
        if search.get("placeholder"):
            for key in loc_profiles:
                loc_profiles[key]["search_placeholder"] = search["placeholder"]
        if search.get("label"):
            for key in loc_profiles:
                loc_profiles[key]["search_label"] = search["label"]
        locales_out[loc] = {
            "profiles": loc_profiles,
            "i18n_status": home_status.get(loc, "scaffold"),
        }

    return {
        "schema_version": "2026.2.7",
        "generated_at": _now(),
        "default_locale": "pt-BR",
        "locales": locales_out,
    }


def sync_by_locale_manifest(home_status: dict[str, str]) -> dict:
    manifest = {
        "generated_at": _now(),
        "schema_version": "2026.2.7-global",
        "strategy": "physical_v5_all_languages",
        "site_locales": SITE_LOCALES,
        "locales": {},
    }
    for loc in SITE_LOCALES:
        meta = SITE_LOCALE_META[loc]
        manifest["locales"][loc] = {
            "home_page": f"by-locale/{loc}/home_page.json",
            "workflows": f"by-locale/{loc}/workflows.json",
            "direction": meta["dir"],
            "url_prefix": meta["url_prefix"],
            "i18n_status": home_status.get(loc, "scaffold"),
        }
        wf = BY_LOCALE / loc / "workflows.json"
        if not wf.is_file():
            _write(wf, {
                "schema_version": "2026.2.7",
                "locale": loc,
                "entity": "Workflow",
                "records": [],
            })
    _write(BY_LOCALE / "manifest.json", manifest)
    return manifest


def sync_user_profile_config(locale_profiles: dict) -> None:
    base = _read(PROFILE_CONFIG)
    base["schema_version"] = "2026.2.7"
    base["supported_locales"] = SITE_LOCALES
    base["locale_profiles"] = locale_profiles.get("locales", {})
    for target in (
        PROFILE_CONFIG,
        ROOT / "website" / "pt" / "assets" / "data" / "user-profile-config.json",
    ):
        _write(target, base)


def main() -> dict:
    home_status = ensure_locale_homes()
    i18n_reg = build_i18n_code_registry()
    audience = build_country_audience_preferences()
    locale_profiles = build_locale_profile_overrides(home_status)
    manifest = sync_by_locale_manifest(home_status)

    _write(EXP / "i18n_code_registry.json", i18n_reg)
    _write(EXP / "country_audience_preferences.json", audience)
    _write(EXP / "locale_profile_matrix.json", locale_profiles)
    sync_user_profile_config(locale_profiles)

    slim = {
        r["country_code"]: {
            "homepage_emphasis": r["homepage_emphasis"],
            "profile_default": r["profile_default"],
            "career_hubs": r["career_hubs"],
            "default_locale": r["default_locale"],
        }
        for r in audience["records"]
    }
    for target in (
        ROOT / "website" / "assets" / "data" / "country-audience.json",
        ROOT / "website" / "pt" / "assets" / "data" / "country-audience.json",
    ):
        _write(target, {"schema_version": "2026.2.7", "generated_at": _now(), "records": slim})

    translated = sum(1 for s in home_status.values() if s in ("translated", "reviewed"))
    summary = {
        "generated_at": _now(),
        "site_locales": len(SITE_LOCALES),
        "i18n_code_items": i18n_reg["total_items"],
        "country_audience_records": audience["total_countries"],
        "home_translated": translated,
        "home_scaffold": len(home_status) - translated,
    }
    _write(EXP / "i18n_coverage_report.json", summary)
    print(f"i18n_code_registry: {i18n_reg['total_items']} items ({len(SITE_LOCALES)} langs × {len(I18N_PAGE_TYPES)} pages)")
    print(f"country_audience: {audience['total_countries']} countries")
    print(f"home pages: {translated} translated, {summary['home_scaffold']} scaffold")
    return summary


if __name__ == "__main__":
    main()
