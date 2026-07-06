"""Orquestrador resource expansion — geradores, biblioteca, slides, games, dicionário medicamentos."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "resource_expansion"))
sys.path.insert(0, str(ROOT / "scripts"))
from agent_common.sanitize import sanitize_agent_result  # noqa: E402

RES = ROOT / "datasets" / "master-data" / "resource-expansion"
RUNS = RES / "agent_runs"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_medication_dictionary(
    *,
    limit: int,
    api_key: str | None,
    use_llm: bool,
) -> dict:
    md_path = str(ROOT / "scripts" / "medication_dictionary_agents")
    apgar_path = str(ROOT / "scripts" / "apgar_agents")
    for p in (md_path, apgar_path):
        if p not in sys.path:
            sys.path.insert(0, p)
    from graph import run_batch as run_med_dict  # noqa: WPS433

    return run_med_dict(
        limit=limit if limit and limit > 0 else None,
        api_key=api_key,
        use_llm=use_llm,
        apply=True,
    )


def run_resources(
    *,
    rebuild: bool = True,
    sync_assets: bool = True,
    build_slides: bool = True,
    asset_limit: int | None = None,
    api_key: str | None = None,
    use_llm: bool = False,
    run_medication_dictionary: bool = True,
    medication_dict_limit: int | None = None,
    use_pending_inventory: bool = True,
) -> dict:
    pending_assets = 851
    pending_med = 10
    if use_pending_inventory:
        try:
            from agent_common.pending_inventory import collect  # noqa: WPS433

            inv = collect()
            re = inv.get("programs", {}).get("resource_expansion", {})
            md = inv.get("programs", {}).get("medication_dictionary", {})
            pending_assets = max(re.get("library_assets_pending", 0), 30)
            pending_med = max(md.get("pending", 0), 0)
        except Exception:
            pass

    if asset_limit is None:
        asset_limit = min(pending_assets, 851) if pending_assets else 30
    if medication_dict_limit is None:
        medication_dict_limit = pending_med if pending_med else 0

    if rebuild:
        from build_registry import main as build_main  # noqa: E402

        build_main()

    indicators_result = {}
    try:
        from build_nursing_indicators import generate as build_indicators  # noqa: E402

        indicators_result = build_indicators()
    except Exception as exc:
        indicators_result = {"ok": False, "error": str(exc)}

    games_result = {}
    try:
        from build_games import generate as build_games  # noqa: E402

        games_result = build_games()
    except Exception as exc:
        games_result = {"ok": False, "error": str(exc)}

    med_dict_result = {}
    if run_medication_dictionary and medication_dict_limit > 0:
        med_dict_result = _run_medication_dictionary(
            limit=medication_dict_limit,
            api_key=api_key,
            use_llm=use_llm,
        )

    asset_sync = {}
    if sync_assets:
        from sync_library_assets import sync  # noqa: E402

        asset_sync = sync(limit=asset_limit)

    slides_built = 0
    if build_slides:
        from build_tool_slides import main as slides_main  # noqa: E402

        slides_built = slides_main().get("built", 0)

    from validate_resources import run_validation  # noqa: E402

    rep = run_validation()

    from update_progress import persist_progress  # noqa: E402

    progress = persist_progress(asset_sync=asset_sync or None, slides_built=slides_built or None)

    report = sanitize_agent_result({
        "generated_at": _now(),
        "validation_ok": len(rep.errors) == 0,
        "validation_errors": rep.errors,
        "asset_sync": asset_sync,
        "slides_built": slides_built,
        "indicators": indicators_result,
        "games": games_result,
        "medication_dictionary": med_dict_result,
        "use_llm": use_llm,
        "llm_provider": "deepseek" if use_llm else None,
        "modules": progress.get("modules", []),
        "overall_completion_pct": progress.get("overall_completion_pct", 0),
        "module_progress": progress.get("module_progress", {}),
        "ok": len(rep.errors) == 0,
    })

    RUNS.mkdir(parents=True, exist_ok=True)
    path = RUNS / f"run_{_now().replace(':', '').replace('-', '')[:15]}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["run_path"] = str(path.relative_to(ROOT))
    return report
