"""Gera registries globais: páginas por país + fusos por território."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "datasets" / "master-data" / "global-expansion"

# Territórios com múltiplos fusos IANA (suplemento além do timezone primário em countries.json)
MULTI_TIMEZONE_TERRITORIES: dict[str, list[str]] = {
    "US": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles", "America/Anchorage", "Pacific/Honolulu"],
    "CA": ["America/Toronto", "America/Vancouver", "America/Edmonton", "America/Winnipeg", "America/Halifax", "America/St_Johns"],
    "AU": ["Australia/Sydney", "Australia/Melbourne", "Australia/Brisbane", "Australia/Perth", "Australia/Adelaide", "Australia/Darwin"],
    "BR": ["America/Sao_Paulo", "America/Manaus", "America/Fortaleza", "America/Recife", "America/Cuiaba", "America/Noronha"],
    "RU": ["Europe/Moscow", "Europe/Kaliningrad", "Asia/Yekaterinburg", "Asia/Novosibirsk", "Asia/Vladivostok", "Asia/Kamchatka"],
    "MX": ["America/Mexico_City", "America/Cancun", "America/Tijuana", "America/Hermosillo", "America/Mazatlan"],
    "ID": ["Asia/Jakarta", "Asia/Makassar", "Asia/Jayapura"],
    "KZ": ["Asia/Almaty", "Asia/Qyzylorda", "Asia/Aqtobe"],
    "ES": ["Europe/Madrid", "Atlantic/Canary"],
    "PT": ["Europe/Lisbon", "Atlantic/Azores"],
    "GL": ["America/Godthab", "America/Danmarkshavn", "America/Scoresbysund", "America/Thule"],
    "CD": ["Africa/Kinshasa", "Africa/Lubumbashi"],
    "MN": ["Asia/Ulaanbaatar", "Asia/Hovd", "Asia/Choibalsan"],
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_territory_timezones() -> dict:
    countries = json.loads((ROOT / "datasets/global/countries.json").read_text(encoding="utf-8"))
    records = []
    for c in countries.get("records", []):
        cc = c["country_code"]
        primary = c.get("timezone")
        zones = MULTI_TIMEZONE_TERRITORIES.get(cc, [primary] if primary else [])
        zones = list(dict.fromkeys(z for z in zones if z))
        records.append({
            "country_code": cc,
            "name": c.get("name"),
            "who_region": c.get("who_region"),
            "primary_timezone": primary,
            "timezones": zones,
            "timezone_count": len(zones),
            "entity_code": f"TERR_{cc}_TZ_001",
        })
    return {
        "schema_version": "2026.2.6-global-expansion",
        "generated_at": _now(),
        "total_territories": len(records),
        "multi_zone_territories": len(MULTI_TIMEZONE_TERRITORIES),
        "records": records,
    }


def build_country_pages() -> dict:
    countries = json.loads((ROOT / "datasets/global/countries.json").read_text(encoding="utf-8"))
    locales = json.loads((ROOT / "datasets/global/locales.json").read_text(encoding="utf-8"))
    langs = {r["language_code"] for r in json.loads((ROOT / "datasets/global/languages.json").read_text(encoding="utf-8")).get("records", [])}

    locale_by_country: dict[str, list[str]] = {}
    for loc in locales.get("records", []):
        cc = loc.get("country_code")
        if cc:
            locale_by_country.setdefault(cc, []).append(loc["locale_code"])

    pages = []
    for c in countries.get("records", []):
        cc = c["country_code"]
        pages.append({
            "entity_code": f"{cc}_PAGE_001",
            "country_code": cc,
            "name": c.get("name"),
            "canonical_url_pattern": f"/regiao/{cc.lower()}/",
            "who_region": c.get("who_region"),
            "timezone": c.get("timezone"),
            "locales_available": locale_by_country.get(cc, []),
            "locale_count": len(locale_by_country.get(cc, [])),
            "languages_in_country": sorted({lc.split("-")[0] for lc in locale_by_country.get(cc, []) if "-" in lc}),
            "status": "pending",
            "evidence_grade_required": "A",
            "agent_pipeline": ["search", "generate", "review", "validate"],
        })

    return {
        "schema_version": "2026.2.6-global-expansion",
        "generated_at": _now(),
        "total_pages": len(pages),
        "languages_global": sorted(langs),
        "language_count": len(langs),
        "pages": pages,
    }


def build_coverage() -> dict:
    countries = json.loads((ROOT / "datasets/global/countries.json").read_text(encoding="utf-8"))
    languages = json.loads((ROOT / "datasets/global/languages.json").read_text(encoding="utf-8"))
    locales = json.loads((ROOT / "datasets/global/locales.json").read_text(encoding="utf-8"))
    tz = build_territory_timezones()
    return {
        "generated_at": _now(),
        "countries": len(countries.get("records", [])),
        "languages": len(languages.get("records", [])),
        "locales": len(locales.get("records", [])),
        "territories_with_timezones": tz["total_territories"],
        "multi_zone_count": tz["multi_zone_territories"],
        "user_profiles": 4,
        "targets_met": {
            "countries_195": len(countries.get("records", [])) >= 195,
            "languages_30": len(languages.get("records", [])) >= 30,
        },
    }


def sync_locale_options(tz_doc: dict) -> int:
    """Enriquece locale-options.json com timezone por país (site mega-menu + persistência)."""
    tz_by_cc = {r["country_code"]: r for r in tz_doc.get("records", [])}
    for rel in (
        ROOT / "website/assets/data/locale-options.json",
        ROOT / "website/pt/assets/data/locale-options.json",
    ):
        if not rel.exists():
            continue
        doc = json.loads(rel.read_text(encoding="utf-8"))
        for rec in doc.get("records", []):
            tz = tz_by_cc.get(rec.get("country_code"), {})
            rec["timezone"] = tz.get("primary_timezone")
            rec["timezones"] = tz.get("timezones", [])
        doc["schema_version"] = "2026.2.6-global-expansion"
        doc["timezone_enriched_at"] = _now()
        rel.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(tz_by_cc)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tz_doc = build_territory_timezones()
    pages_doc = build_country_pages()
    cov = build_coverage()
    synced = sync_locale_options(tz_doc)

    (OUT_DIR / "territory_timezones.json").write_text(json.dumps(tz_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "country_pages_registry.json").write_text(json.dumps(pages_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "coverage_report.json").write_text(json.dumps(cov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"territory_timezones: {tz_doc['total_territories']} territories, {tz_doc['multi_zone_territories']} multi-zone")
    print(f"country_pages: {pages_doc['total_pages']} pages, {pages_doc['language_count']} languages")
    print(f"locale-options: {synced} territories with timezone")
    print(f"coverage: {cov}")

    from build_i18n_world import main as i18n_main  # noqa: WPS433

    i18n_main()

    import importlib.util

    career_path = ROOT / "scripts" / "career_agents" / "build_registry.py"
    spec = importlib.util.spec_from_file_location("career_build_registry", career_path)
    career_mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(career_mod)
    career_mod.main()

    try:
        from build_user_profiles import generate as build_profiles  # noqa: WPS433

        build_profiles()
    except Exception:
        pass


if __name__ == "__main__":
    main()
