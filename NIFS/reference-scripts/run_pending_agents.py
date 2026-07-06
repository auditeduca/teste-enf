#!/usr/bin/env python3
"""Executa agentes apenas nas pendências detectadas pelo inventário.

  python scripts/run_pending_agents.py --inventory
  python scripts/run_pending_agents.py --run
  python scripts/run_pending_agents.py --run --llm
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
REPORT = ROOT / "datasets" / "metadata" / "pending_agents_report.json"

NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _py(*parts: str) -> list[str]:
    return [sys.executable, str(SCRIPTS / parts[0])] + list(parts[1:])


def _step(name: str, cmd: list[str], *, timeout: int | None = None) -> dict[str, Any]:
    t0 = time.monotonic()
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
    elapsed = round(time.monotonic() - t0, 1)
    return {
        "step": name,
        "ok": proc.returncode == 0,
        "elapsed_s": elapsed,
        "stdout_tail": "\n".join((proc.stdout or "").strip().splitlines()[-6:]),
        "stderr_tail": "\n".join((proc.stderr or "").strip().splitlines()[-6:]),
    }


def run_pending(*, use_llm: bool = False) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from agent_common.pending_inventory import collect  # noqa: WPS433

    inv = collect()
    llm = ["--llm"] if use_llm else ["--no-llm"]
    steps: list[dict[str, Any]] = []

    progs = inv.get("programs", {})
    med_pending = progs.get("medication_dictionary", {}).get("pending", 0)
    wf_retry = progs.get("workflows", {}).get("retry_count", 0)
    lib_pending = progs.get("resource_expansion", {}).get("library_assets_pending", 0)
    ind_pending = progs.get("resource_expansion", {}).get("indicators_pending", 0)
    ind_count = progs.get("resource_expansion", {}).get("indicators_count", 0)
    ind_target = progs.get("resource_expansion", {}).get("indicators_target", 100)
    cn_pending = progs.get("compulsory_notifications", {}).get("queue_pending", 0)
    bl_pending = progs.get("brazilian_legislation", {}).get("queue_pending", 0)
    anv_pending = progs.get("anvisa_open_data", {}).get("pending_refresh", 0)
    ge_pct = progs.get("global_expansion", {}).get("completion_pct", 100)

    print(f"=== Pendências @ {inv['generated_at']} ===")
    for action in inv.get("actions", []):
        print(f"  [{action['priority']}] {action['agent']}: {action.get('pending', action.get('pending_pct', '?'))}")

    if ind_pending > 0:
        print(f"\n>> M21 indicators ({ind_count}/{ind_target})")
        steps.append(_step("indicators_m21", _py("resource_expansion/build_nursing_indicators.py"), timeout=120))

    if med_pending > 0:
        print(f"\n>> medication_dictionary ({med_pending} DrugReference)")
        steps.append(_step(
            "medication_dictionary",
            _py("medication_dictionary_agents/run_batch.py", "--all-pending", *(["--llm"] if use_llm else [])),
            timeout=7200,
        ))

    if wf_retry > 0:
        print(f"\n>> content workflows retry ({wf_retry})")
        steps.append(_step(
            "workflow_retry",
            _py("content/workflow_runner.py", "--retry-failed", "--limit", str(wf_retry), *(["--no-llm"] if not use_llm else [])),
            timeout=600,
        ))

    if lib_pending > 0 or med_pending > 0:
        print(f"\n>> resource expansion (assets={lib_pending})")
        steps.append(_step(
            "resource_expansion",
            _py(
                "resource_expansion_agents/run_resources.py",
                "--all",
                "--limit",
                str(min(lib_pending or 851, 851)),
                "--med-dict-limit",
                "0",
                *llm,
            ),
            timeout=3600,
        ))

    if cn_pending > 0:
        print(f"\n>> compulsory notifications ({cn_pending})")
        steps.append(_step("compulsory_scrape", _py("compulsory_notification_agents/run_batch.py", "--scrape", "--catalog"), timeout=600))
        steps.append(_step("compulsory_validate", _py("compulsory_notification_agents/run_batch.py", "--validate")))

    if bl_pending > 0:
        print(f"\n>> brazilian legislation ({bl_pending})")
        steps.append(_step("legislation_refresh", _py("brazilian_legislation_agents/run_batch.py", "--refresh", "--all-sources"), timeout=900))

    if anv_pending > 0:
        print(f"\n>> ANVISA open data ({anv_pending} stale/initial)")
        steps.append(_step("anvisa_monthly", _py("anvisa_open_data_agents/run_batch.py", "--monthly", "--limit", "5"), timeout=3600))

    if ge_pct < 100:
        print(f"\n>> global expansion ({ge_pct}%)")
        steps.append(_step("user_profiles", _py("global_expansion/build_user_profiles.py"), timeout=60))
        steps.append(_step("global_expansion", _py("global_expansion_agents/run_global.py", "--all", "--rebuild", *llm), timeout=1800))

    print("\n>> content factory sync")
    steps.append(_step("content_factory_sync", _py("content_factory_sync.py", "--country", "BR")))

    inv_after = collect()
    ok = sum(1 for s in steps if s.get("ok"))
    fail = sum(1 for s in steps if not s.get("ok"))

    report = {
        "generated_at": NOW(),
        "ok": fail == 0,
        "steps_ok": ok,
        "steps_fail": fail,
        "inventory_before": inv,
        "inventory_after": inv_after,
        "steps": steps,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\n=== Pending agents: {'PASS' if report['ok'] else 'FAIL'} ({ok}/{len(steps)}) ===")
    print(f"Relatório: {REPORT.relative_to(ROOT)}")
    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Agentes orientados por inventário de pendências")
    p.add_argument("--inventory", action="store_true")
    p.add_argument("--run", action="store_true")
    p.add_argument("--llm", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    sys.path.insert(0, str(SCRIPTS))
    from agent_common.pending_inventory import collect  # noqa: WPS433

    if args.inventory or not args.run:
        inv = collect()
        if args.json:
            print(json.dumps(inv, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(inv, ensure_ascii=False, indent=2))
        return 0 if not inv.get("actions") else 1

    report = run_pending(use_llm=args.llm)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
