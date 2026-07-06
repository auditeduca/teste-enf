"""Validador cobertura global."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXP = ROOT / "datasets" / "master-data" / "global-expansion"


@dataclass
class Report:
    checks: int = 0
    errors: list[dict] = field(default_factory=list)
    passed: list[dict] = field(default_factory=list)

    def ok(self, fid: str, msg: str) -> None:
        self.checks += 1
        self.passed.append({"field_id": fid, "message": msg})

    def fail(self, fid: str, msg: str) -> None:
        self.checks += 1
        self.errors.append({"field_id": fid, "message": msg})


def run_validation() -> Report:
    rep = Report()
    canonical = json.loads((EXP / "canonical.json").read_text(encoding="utf-8"))

    for name in ("territory_timezones.json", "country_pages_registry.json", "profile_content_matrix.json"):
        if not (EXP / name).exists():
            rep.fail(f"GLOBAL.files.{name}", "ausente — rode build_registry.py")
        else:
            rep.ok(f"GLOBAL.files.{name}", "presente")

    countries = json.loads((ROOT / "datasets/global/countries.json").read_text(encoding="utf-8"))
    n_countries = len(countries.get("records", []))
    if n_countries < 195:
        rep.fail("GLOBAL.countries", f"{n_countries} < 195")
    else:
        rep.ok("GLOBAL.countries", f"{n_countries} países")

    langs = json.loads((ROOT / "datasets/global/languages.json").read_text(encoding="utf-8"))
    n_lang = len(langs.get("records", []))
    if n_lang < 30:
        rep.fail("GLOBAL.languages", f"{n_lang} < 30")
    else:
        rep.ok("GLOBAL.languages", f"{n_lang} idiomas")

    if (EXP / "country_pages_registry.json").exists():
        pages = json.loads((EXP / "country_pages_registry.json").read_text(encoding="utf-8"))
        if pages.get("total_pages") != n_countries:
            rep.fail("GLOBAL.pages.sync", f"pages {pages.get('total_pages')} != countries {n_countries}")
        else:
            rep.ok("GLOBAL.pages.sync", f"{pages['total_pages']} páginas país")

    if (EXP / "territory_timezones.json").exists():
        tz = json.loads((EXP / "territory_timezones.json").read_text(encoding="utf-8"))
        without_tz = [r for r in tz.get("records", []) if not r.get("timezones")]
        if without_tz:
            rep.fail("GLOBAL.timezones", f"{len(without_tz)} territórios sem fuso")
        else:
            rep.ok("GLOBAL.timezones", f"{tz['total_territories']} territórios com fusos")

    matrix = json.loads((EXP / "profile_content_matrix.json").read_text(encoding="utf-8"))
    for key in ("estudante", "profissional", "gestor", "academico"):
        if key not in matrix.get("profiles", {}):
            rep.fail(f"GLOBAL.profile.{key}", "ausente")
        else:
            mods = matrix["profiles"][key].get("modules", [])
            if not all(m.get("evidence_grade") == "A" for m in mods):
                rep.fail(f"GLOBAL.profile.{key}", "evidência != A")
            else:
                rep.ok(f"GLOBAL.profile.{key}", f"{len(mods)} módulos Grau A")

    if canonical.get("evidence_policy", {}).get("minimum_grade") != "A":
        rep.fail("GLOBAL.evidence", "minimum_grade != A")
    else:
        rep.ok("GLOBAL.evidence", "Grau A obrigatório")

    for name, min_count, label in (
        ("i18n_code_registry.json", 300, "i18n codes"),
        ("country_audience_preferences.json", 195, "audience prefs"),
        ("locale_profile_matrix.json", 1, "locale profiles"),
        ("i18n_coverage_report.json", 1, "i18n coverage"),
    ):
        path = EXP / name
        if not path.exists():
            rep.fail(f"GLOBAL.i18n.{name}", "ausente — rode build_registry.py")
        else:
            doc = json.loads(path.read_text(encoding="utf-8"))
            count = doc.get("total_items") or doc.get("total_countries") or doc.get("site_locales") or 1
            if count < min_count:
                rep.fail(f"GLOBAL.i18n.{name}", f"{count} < {min_count}")
            else:
                rep.ok(f"GLOBAL.i18n.{name}", f"{label}: {count}")

    careers_dir = ROOT / "datasets" / "master-data" / "careers"
    if not (careers_dir / "country_registry.json").exists():
        rep.fail("GLOBAL.careers.registry", "ausente")
    else:
        cr = json.loads((careers_dir / "country_registry.json").read_text(encoding="utf-8"))
        expected = n_countries * 4
        if cr.get("total_items", 0) < expected:
            rep.fail("GLOBAL.careers.registry", f"{cr.get('total_items')} < {expected}")
        else:
            rep.ok("GLOBAL.careers.registry", f"{cr['total_items']} itens carreira")

    try:
        import sys
        scripts = ROOT / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from global_expansion.site_locales import SITE_LOCALES as SL  # noqa: WPS433

        if len(SL) < 30:
            rep.fail("GLOBAL.site_locales", f"{len(SL)} < 30")
        else:
            rep.ok("GLOBAL.site_locales", f"{len(SL)} idiomas build")
    except ImportError as exc:
        rep.fail("GLOBAL.site_locales", str(exc))

    return rep


if __name__ == "__main__":
    import sys

    rep = run_validation()
    print(f"Checks: {rep.checks} | Pass: {len(rep.passed)} | Fail: {len(rep.errors)}")
    for e in rep.errors:
        print(f"  FAIL {e['field_id']}: {e['message']}")
    sys.exit(1 if rep.errors else 0)
