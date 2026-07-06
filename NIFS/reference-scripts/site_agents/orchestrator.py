"""Orquestrador site-full — delega para apgar/content/site agents."""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "site_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from agent_common.sanitize import sanitize_agent_result  # noqa: E402
from site_full.field_registry import manifest, module_by_id  # noqa: E402

RUNS_DIR = ROOT / "datasets" / "master-data" / "site-full" / "agent_runs"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_content_field(field_id: str, *, api_key: str | None, model: str | None, use_llm: bool) -> dict:
    ca = str(ROOT / "scripts" / "content_agents")
    aa = str(ROOT / "scripts" / "apgar_agents")
    for p in (ca, aa):
        if p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, aa)
    sys.path.insert(0, ca)
    import graph as content_graph  # noqa: E402

    return content_graph.run_field(field_id, api_key=api_key, model=model, use_llm=use_llm)


def _run_apgar_field(field_id: str, *, api_key: str | None, model: str | None, use_llm: bool) -> dict:
    aa = str(ROOT / "scripts" / "apgar_agents")
    if aa not in sys.path:
        sys.path.insert(0, aa)
    import graph as apgar_graph  # noqa: E402

    return apgar_graph.run_field(field_id, api_key=api_key, model=model, use_llm=use_llm)


def _run_content_bulk(artifact_type: str, limit: int, *, api_key: str | None, model: str | None, use_llm: bool) -> dict:
    from content.workflow_runner import run_bulk  # noqa: E402

    return run_bulk(artifact_type=artifact_type, limit=limit, api_key=api_key, model=model, use_llm=use_llm)


def _validate_api() -> dict:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8787/api/health", timeout=3) as r:
            data = json.loads(r.read().decode())
        return {"ok": data.get("ok"), "entity_count": data.get("entity_count"), "mode": "live"}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "mode": "offline"}


def _run_build() -> dict:
    cmd = [sys.executable, str(ROOT / "scripts" / "generate_website_pt.py"), "--pt-only", "--no-zip"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=600)
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-800:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def _check_datasets(module: dict) -> dict:
    missing = []
    for rel in module.get("datasets", []):
        if not (ROOT / "datasets" / rel).exists():
            missing.append(rel)
    return {"ok": len(missing) == 0, "missing": missing, "count": len(module.get("datasets", []))}


def run_module(
    module_id: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
    bulk_limit: int = 5,
    approve: bool = False,
) -> dict:
    mod = module_by_id(module_id)
    if not mod:
        raise KeyError(f"Módulo desconhecido: {module_id}")

    agent = mod.get("agent", "site_agents")
    field_id = mod.get("field_id", "")
    result: dict[str, Any] = {
        "module_id": mod["id"],
        "code": mod["code"],
        "label_pt": mod["label_pt"],
        "agent": agent,
        "started_at": _now(),
        "steps": [],
    }

    ds_check = _check_datasets(mod)
    result["steps"].append({"step": "search", "ok": ds_check["ok"], "detail": ds_check})

    if mod["id"] == "M18_build":
        build_out = _run_build()
        result["steps"].append({"step": "build", "ok": build_out["ok"], "detail": build_out})
        result["ok"] = build_out["ok"]
        result["finished_at"] = _now()
        return sanitize_agent_result(result)

    if mod["id"] == "M12_api_platform":
        api_out = _validate_api()
        result["steps"].append({"step": "validate", "ok": api_out.get("ok"), "detail": api_out})
        result["ok"] = bool(api_out.get("ok"))
        result["finished_at"] = _now()
        return sanitize_agent_result(result)

    if agent == "content_agents" and mod.get("artifact_type"):
        bulk = _run_content_bulk(
            mod["artifact_type"],
            bulk_limit,
            api_key=api_key,
            model=model,
            use_llm=use_llm,
        )
        result["steps"].append({"step": "generate", "ok": bulk.get("ok"), "detail": {"processed": bulk.get("processed"), "errors": bulk.get("errors")[:3]}})
        if approve and bulk.get("results"):
            from content.workflow_runner import approve_workflow  # noqa: E402

            approved = []
            for wf in bulk["results"]:
                if wf.get("status") == "awaiting_approval":
                    try:
                        approved.append(approve_workflow(wf["workflow_id"]))
                    except Exception as exc:
                        approved.append({"error": str(exc)})
            result["steps"].append({"step": "apply", "ok": True, "detail": {"approved": len(approved)}})
        result["ok"] = bulk.get("ok", False)
    elif agent == "apgar_agents" and field_id:
        pipe = _run_apgar_field(field_id, api_key=api_key, model=model, use_llm=use_llm)
        result["steps"].append({"step": "pipeline", "ok": (pipe.get("validation") or {}).get("validation_passed"), "detail": {"trace": pipe.get("trace")}})
        result["ok"] = bool((pipe.get("validation") or {}).get("validation_passed"))
    elif field_id:
        try:
            pipe = _run_content_field(field_id, api_key=api_key, model=model, use_llm=use_llm)
            result["steps"].append({"step": "pipeline", "ok": (pipe.get("validation") or {}).get("validation_passed"), "detail": {"trace": pipe.get("trace")}})
            result["ok"] = bool((pipe.get("validation") or {}).get("validation_passed"))
        except KeyError:
            result["steps"].append({"step": "generate", "ok": ds_check["ok"], "detail": "Campo site — pipeline stub (datasets OK)"})
            result["ok"] = ds_check["ok"]
    else:
        result["ok"] = ds_check["ok"]

    result["finished_at"] = _now()
    return sanitize_agent_result(result)


def run_all(
    *,
    module_ids: list[str] | None = None,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
    bulk_limit: int = 5,
    approve: bool = False,
    build: bool = True,
    archive_dry_run: bool = True,
) -> dict:
    mods = manifest().get("modules", [])
    if module_ids:
        wanted = set(module_ids)
        mods = [m for m in mods if m["id"] in wanted or m["code"] in wanted]

    if archive_dry_run:
        from content.apply_proposal import archive_legacy_datasets  # noqa: E402

        archive_preview = archive_legacy_datasets(dry_run=True)
    else:
        archive_preview = {"skipped": True}

    results = []
    for mod in sorted(mods, key=lambda x: x.get("priority", 99)):
        if mod["id"] == "M18_build" and not build:
            continue
        try:
            results.append(
                run_module(
                    mod["id"],
                    api_key=api_key,
                    model=model,
                    use_llm=use_llm,
                    bulk_limit=bulk_limit,
                    approve=approve,
                )
            )
        except Exception as exc:
            results.append({"module_id": mod["id"], "ok": False, "error": str(exc)})

    ok_count = sum(1 for r in results if r.get("ok"))
    report = {
        "schema_version": "2026.2.5-site-full",
        "generated_at": _now(),
        "ok": ok_count == len(results),
        "modules_total": len(results),
        "modules_passed": ok_count,
        "archive_preview": archive_preview,
        "results": results,
    }

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"run_{_now().replace(':', '').replace('-', '')[:15]}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["run_path"] = str(path.relative_to(ROOT))
    return report
