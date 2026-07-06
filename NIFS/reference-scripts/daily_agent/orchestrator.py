"""Agente diário — finaliza pendências em ciclos de 24h."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
REPORT = ROOT / "datasets" / "metadata" / "daily_agent_report.json"
STATE = ROOT / "datasets" / "metadata" / "daily_agent_state.json"
HISTORY = ROOT / "datasets" / "metadata" / "daily_agent_history.jsonl"
LOCK = ROOT / "datasets" / "metadata" / "daily_agent.lock"

NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _py(*parts: str) -> list[str]:
    return [sys.executable, str(SCRIPTS / parts[0])] + list(parts[1:])


def _step(name: str, cmd: list[str], *, timeout: int | None = None) -> dict[str, Any]:
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        ok = proc.returncode == 0
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
    except subprocess.TimeoutExpired as exc:
        ok = False
        out = (exc.stdout or "")[-1200:] if exc.stdout else ""
        err = f"timeout after {timeout}s"
        proc = None
    return {
        "step": name,
        "ok": ok,
        "exit_code": proc.returncode if proc else -1,
        "elapsed_s": round(time.monotonic() - t0, 1),
        "stdout_tail": "\n".join(out.splitlines()[-4:]),
        "stderr_tail": "\n".join(err.splitlines()[-4:]),
    }


def _acquire_lock() -> bool:
    if LOCK.is_file():
        try:
            old = json.loads(LOCK.read_text(encoding="utf-8"))
            started = datetime.strptime(old["started_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - started < timedelta(hours=6):
                return False
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps({"pid": "agent", "started_at": NOW()}, indent=2) + "\n", encoding="utf-8")
    return True


def _release_lock() -> None:
    LOCK.unlink(missing_ok=True)


def _load_state() -> dict:
    if STATE.is_file():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {}


def _save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_history(summary: dict) -> None:
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(summary, ensure_ascii=False) + "\n")


def run_daily_cycle(
    *,
    use_llm: bool = False,
    med_limit: int = 25,
    asset_limit: int = 50,
    full_audit: bool = False,
    rebuild_site: bool = False,
    no_ssl_verify: bool = True,
) -> dict[str, Any]:
    if not _acquire_lock():
        return {"ok": False, "error": "daily_agent already running (lock)", "locked": True}

    steps: list[dict[str, Any]] = []
    ssl = ["--no-ssl-verify"] if no_ssl_verify else []
    llm = ["--llm"] if use_llm else []

    def go(name: str, cmd: list[str], timeout: int | None = None) -> bool:
        r = _step(name, cmd, timeout=timeout)
        steps.append(r)
        return r["ok"]

    try:
        sys.path.insert(0, str(SCRIPTS))
        from agent_common.pending_inventory import collect  # noqa: WPS433
        from run_platform_complete import repair_datasets  # noqa: WPS433

        repair = repair_datasets()
        steps.append({"step": "repair_datasets", "ok": True, "detail": repair})

        inv_before = collect()
        actions = inv_before.get("actions", [])
        progs = inv_before.get("programs", {})

        med_pending = progs.get("medication_dictionary", {}).get("pending", 0)
        lib_pending = progs.get("resource_expansion", {}).get("library_assets_pending", 0)
        wf_retry = progs.get("workflows", {}).get("retry_count", 0)
        cn_pending = progs.get("compulsory_notifications", {}).get("queue_pending", 0)
        anv_pending = progs.get("anvisa_open_data", {}).get("pending_refresh", 0)
        ge_pct = progs.get("global_expansion", {}).get("completion_pct", 100)
        i18n_homes = (progs.get("global_expansion", {}).get("segments") or {}).get("i18n_homes", 100)

        if med_pending > 0:
            cmd = _py("medication_dictionary_agents/run_batch.py", "--limit", str(med_limit), *llm)
            go("medication_dictionary", cmd, timeout=7200)

        if wf_retry > 0:
            go(
                "workflow_retry",
                _py("content/workflow_runner.py", "--retry-failed", "--limit", str(min(wf_retry, 10)), *(["--no-llm"] if not use_llm else [])),
                timeout=600,
            )

        if lib_pending > 0:
            go(
                "library_assets",
                _py(
                    "resource_expansion_agents/run_resources.py",
                    "--all", "--limit", str(min(asset_limit, lib_pending)),
                    "--med-dict-limit", "0", *(["--no-llm"] if not use_llm else []),
                ),
                timeout=3600,
            )

        if anv_pending > 0:
            go("anvisa_open_data", _py("anvisa_open_data_agents/run_batch.py", "--monthly", "--limit", "5", *ssl), timeout=3600)

        if cn_pending > 0:
            go("compulsory_notifications", _py("compulsory_notification_agents/run_batch.py", "--scrape", "--catalog"), timeout=600)

        if ge_pct < 100 or i18n_homes < 100:
            go("user_profiles", _py("global_expansion/build_user_profiles.py"), timeout=120)
            if i18n_homes < 100:
                go("i18n_world", _py("global_expansion/build_i18n_world.py"), timeout=180)
                if use_llm:
                    go(
                        "global_expansion_i18n",
                        _py("global_expansion_agents/run_global.py", "--all", "--rebuild", *llm),
                        timeout=1800,
                    )

        go("content_factory_sync", _py("content_factory_sync.py", "--country", "BR"), timeout=120)
        go("resource_progress", _py("resource_expansion/update_progress.py"), timeout=120)
        go("games_m25", _py("resource_expansion/build_games.py"), timeout=120)

        if full_audit:
            go("full_audit", _py("run_full_audit.py"), timeout=7200)
        else:
            go("audit_ecosystem", _py("audit_ecosystem_coverage.py"), timeout=600)

        go("minify_assets", _py("optimize_assets.py", "--all", "--apply-build", "--in-place"), timeout=600)

        if rebuild_site or i18n_homes < 100:
            go("website_i18n", _py("generate_website_pt.py", "--optimize-assets", "--no-zip"), timeout=7200)

        go("content_validate", _py("content/validate_content.py"), timeout=300)

        inv_after = collect()
        remaining = len(inv_after.get("actions", []))

        state = _load_state()
        run_count = state.get("run_count", 0) + 1
        complete = remaining == 0
        next_run = (datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")

        ok_count = sum(1 for s in steps if s.get("ok"))
        fail_count = sum(1 for s in steps if s.get("ok") is False)

        report = {
            "schema_version": "2026.2.12-daily-agent",
            "generated_at": NOW(),
            "ok": fail_count == 0,
            "platform_complete": complete,
            "run_count": run_count,
            "next_run_at": next_run,
            "actions_before": len(actions),
            "actions_after": remaining,
            "steps_ok": ok_count,
            "steps_fail": fail_count,
            "inventory_before": {
                "critical_pending": inv_before.get("summary", {}).get("critical_pending"),
                "actions": [a.get("agent") for a in actions],
            },
            "inventory_after": {
                "critical_pending": inv_after.get("summary", {}).get("critical_pending"),
                "actions": [a.get("agent") for a in inv_after.get("actions", [])],
            },
            "steps": steps,
        }

        _save_state({
            "last_run_at": NOW(),
            "next_run_at": next_run,
            "run_count": run_count,
            "platform_complete": complete,
            "last_actions_remaining": remaining,
        })
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _append_history({
            "at": NOW(),
            "complete": complete,
            "remaining": remaining,
            "steps_fail": fail_count,
        })
        report["report_path"] = str(REPORT.relative_to(ROOT))
        return report
    finally:
        _release_lock()
