"""Recalcula completion_pct por módulo M19–M25 com base no estado real dos datasets."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RES = ROOT / "datasets" / "master-data" / "resource-expansion"
LIB_MANIFEST = ROOT / "datasets" / "content" / "library" / "library_visual_assets.json"
SLIDES_DIR = ROOT / "website" / "assets" / "data" / "slides"
DICT = ROOT / "datasets" / "master" / "nursing_dictionary.json"
MED_DICT = ROOT / "datasets" / "clinical" / "medication_dictionary.json"
DRUG_REFS = ROOT / "datasets" / "clinical" / "drug_references.json"
INDICATORS = ROOT / "datasets" / "operations" / "nursing_indicators.json"
APGAR_VAL = ROOT / "datasets" / "master-data" / "apgar" / "validation_report.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pct(num: float, den: float, cap: int = 100) -> int:
    if den <= 0:
        return 0
    return min(cap, max(0, round(num / den * 100)))


def _medication_dictionary_stats() -> dict:
    import sys

    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from agent_common.json_io import load_json  # noqa: WPS433

    med_doc = load_json(MED_DICT) if MED_DICT.is_file() else {}
    med_records = med_doc.get("records", [])
    med_with_def = sum(1 for r in med_records if r.get("definition_pt") or r.get("definition"))
    drug_total = len(json.loads(DRUG_REFS.read_text(encoding="utf-8")).get("records", [])) if DRUG_REFS.is_file() else 500
    med_pct = _pct(med_with_def, max(drug_total, 1))
    return {
        "linked": len(med_records),
        "with_definition": med_with_def,
        "total_drug_references": drug_total,
        "completion_pct": med_pct,
    }


def compute_module_progress(*, asset_sync: dict | None = None, slides_built: int | None = None) -> dict[str, int]:
    progress: dict[str, int] = {}

    tpl = ROOT / "datasets" / "content" / "site" / "template_pages.json"
    progress["M19_cv_generator"] = 55 if tpl.is_file() else 20

    apgar_pct = 5
    if APGAR_VAL.is_file():
        rep = json.loads(APGAR_VAL.read_text(encoding="utf-8"))
        if rep.get("validation_passed") or rep.get("errors", 1) == 0:
            apgar_pct = 100
        elif rep.get("checks_passed"):
            apgar_pct = min(95, _pct(rep.get("checks_passed", 0), rep.get("checks_total", 26)))
    progress["M20_scales_generator"] = apgar_pct

    ind_doc = json.loads(INDICATORS.read_text(encoding="utf-8")) if INDICATORS.is_file() else {}
    ind_count = len(ind_doc.get("records", []))
    progress["M21_indicators_generator"] = _pct(ind_count, 100)

    dict_doc = json.loads(DICT.read_text(encoding="utf-8")) if DICT.is_file() else {}
    records = dict_doc.get("records", [])
    with_def = sum(1 for r in records if r.get("definition_pt") or r.get("definition"))
    nursing_pct = _pct(with_def, max(len(records), 1))

    med_stats = _medication_dictionary_stats()
    med_pct = med_stats["completion_pct"]
    progress["M22_dictionary"] = round((nursing_pct + med_pct) / 2)

    downloaded = 0
    total_assets = 851
    if LIB_MANIFEST.is_file():
        lib = json.loads(LIB_MANIFEST.read_text(encoding="utf-8"))
        total_assets = lib.get("total_assets", len(lib.get("records", [])))
        downloaded = sum(1 for r in lib.get("records", []) if r.get("status") == "downloaded")
    if asset_sync:
        downloaded = max(downloaded, asset_sync.get("ok", 0))
    progress["M23_library_assets"] = _pct(downloaded, min(total_assets, 100) or 1)

    slide_files = len(list(SLIDES_DIR.glob("*.json"))) if SLIDES_DIR.is_dir() else 0
    if slides_built is not None:
        slide_files = max(slide_files, slides_built)
    progress["M24_tool_slides"] = _pct(slide_files, 100)

    reg_games = RES / "games_registry.json"
    if reg_games.is_file():
        summary = json.loads(reg_games.read_text(encoding="utf-8")).get("summary", {})
        progress["M25_games"] = int(summary.get("games_completion_pct", summary.get("completion_pct", 0)))
    else:
        games_path = RES / "games_roadmap.json"
        if games_path.is_file():
            phases = len(json.loads(games_path.read_text(encoding="utf-8")).get("phases", []))
            progress["M25_games"] = _pct(phases, 3)
        else:
            progress["M25_games"] = 0

    return progress


def persist_progress(*, asset_sync: dict | None = None, slides_built: int | None = None) -> dict:
    reg_path = RES / "modules_registry.json"
    if not reg_path.is_file():
        from build_registry import main as build_main  # noqa: WPS433

        build_main()

    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    progress = compute_module_progress(asset_sync=asset_sync, slides_built=slides_built)

    for mod in reg.get("modules", []):
        mid = mod.get("module_id", "")
        if mid in progress:
            mod["completion_pct"] = progress[mid]
            mod["progress_updated_at"] = _now()

    reg["generated_at"] = _now()
    reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pcts = [m.get("completion_pct", 0) for m in reg.get("modules", [])]
    overall = round(sum(pcts) / len(pcts), 1) if pcts else 0

    cov_path = RES / "coverage_report.json"
    cov = json.loads(cov_path.read_text(encoding="utf-8")) if cov_path.is_file() else {}
    med_stats = _medication_dictionary_stats()
    cov.update({
        "generated_at": _now(),
        "overall_completion_pct": overall,
        "module_progress": progress,
        "medication_dictionary": med_stats,
    })
    cov_path.write_text(json.dumps(cov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {"overall_completion_pct": overall, "modules": reg.get("modules", []), "module_progress": progress}


if __name__ == "__main__":
    result = persist_progress()
    print(f"overall_completion_pct: {result['overall_completion_pct']}")
    for mid, pct in result.get("module_progress", {}).items():
        print(f"  {mid}: {pct}%")
