"""Recalcula completion_pct da expansão global (i18n, perfis, carreiras, países)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXP = ROOT / "datasets" / "master-data" / "global-expansion"
CAREERS = ROOT / "datasets" / "master-data" / "careers"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def persist_global_progress(*, last_run: dict | None = None) -> dict:
    cov_path = EXP / "coverage_report.json"
    i18n_path = EXP / "i18n_coverage_report.json"
    cov = json.loads(cov_path.read_text(encoding="utf-8")) if cov_path.is_file() else {}
    i18n = json.loads(i18n_path.read_text(encoding="utf-8")) if i18n_path.is_file() else {}

    countries_pct = _pct(cov.get("countries", 0), 195)
    langs_pct = _pct(cov.get("languages", 0), 30)
    home_pct = _pct(i18n.get("home_translated", 0), 30)
    i18n_codes_pct = _pct(i18n.get("i18n_code_items", 300), 300)

    careers_pct = 0
    cr_path = CAREERS / "coverage_report.json"
    if cr_path.is_file():
        cr = json.loads(cr_path.read_text(encoding="utf-8"))
        generated = ROOT / "datasets" / "generated" / "careers"
        country_dirs = len([p for p in generated.iterdir() if p.is_dir()]) if generated.is_dir() else 0
        careers_pct = _pct(country_dirs, cr.get("countries", 195))

    if last_run:
        if last_run.get("i18n", {}).get("home_translated") is not None:
            home_pct = max(home_pct, _pct(last_run["i18n"]["home_translated"], 30))
        if last_run.get("careers", {}).get("countries_ok") is not None:
            careers_pct = max(careers_pct, _pct(last_run["careers"]["countries_ok"], 195))

    profiles_pct = 50
    reg_path = EXP / "user_profiles_registry.json"
    if reg_path.is_file():
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        profiles_pct = int(reg.get("summary", {}).get("overall_profiles_pct", 50))
    elif last_run and all(p.get("ok") for p in last_run.get("profiles", [])):
        profiles_pct = 100

    segments = {
        "countries": countries_pct,
        "languages": langs_pct,
        "i18n_homes": home_pct,
        "i18n_codes": i18n_codes_pct,
        "careers": careers_pct,
        "profiles": profiles_pct,
    }
    overall = round(sum(segments.values()) / len(segments), 1)

    out = {
        "generated_at": _now(),
        "overall_completion_pct": overall,
        "segments": segments,
    }
    cov["overall_completion_pct"] = overall
    cov["progress_segments"] = segments
    cov["progress_updated_at"] = _now()
    cov_path.write_text(json.dumps(cov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def _pct(num: float, den: float) -> int:
    if den <= 0:
        return 0
    return min(100, max(0, round(num / den * 100)))
