#!/usr/bin/env python3
"""Wrap-up do projeto — auditoria, minificação CSS/JS, rebuild i18n, inventário.

Executar após sincronizações (ANVISA, resource expansion, etc.):

  python scripts/run_project_wrapup.py
  python scripts/run_project_wrapup.py --skip-audit
  python scripts/run_project_wrapup.py --quick   # sem auditoria completa

Escreve: datasets/metadata/project_wrapup_report.json
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
REPORT = ROOT / "datasets" / "metadata" / "project_wrapup_report.json"

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
        out = (exc.stdout or "")[-1500:] if exc.stdout else ""
        err = f"timeout after {timeout}s"
        proc = None
    elapsed = round(time.monotonic() - t0, 1)
    return {
        "step": name,
        "ok": ok,
        "exit_code": proc.returncode if proc else -1,
        "elapsed_s": elapsed,
        "cmd": " ".join(cmd),
        "stdout_tail": "\n".join(out.splitlines()[-6:]),
        "stderr_tail": "\n".join(err.splitlines()[-6:]),
    }


def run_wrapup(
    *,
    skip_audit: bool = False,
    skip_build: bool = False,
    skip_anvisa: bool = False,
    quick: bool = False,
    no_ssl_verify: bool = True,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []

    def go(name: str, cmd: list[str], timeout: int | None = None) -> bool:
        print(f"\n>> {name}")
        r = _step(name, cmd, timeout=timeout)
        steps.append(r)
        mark = "OK" if r["ok"] else "FAIL"
        print(f"   [{mark}] {r['elapsed_s']}s")
        if not r["ok"] and r.get("stderr_tail"):
            print(f"   {r['stderr_tail'][:180]}")
        return r["ok"]

    ssl_flags = ["--no-ssl-verify"] if no_ssl_verify else []

    print("=== WRAP-UP CALENF-NKD ===")

    sys.path.insert(0, str(SCRIPTS))
    try:
        from run_platform_complete import repair_datasets  # noqa: WPS433

        repair = repair_datasets()
        steps.append({"step": "repair_datasets", "ok": True, "detail": repair, "elapsed_s": 0})
        print(">> repair_datasets\n   [OK]")
    except Exception as exc:
        steps.append({"step": "repair_datasets", "ok": False, "error": str(exc)})
        print(f">> repair_datasets\n   [FAIL] {exc}")

    if not skip_anvisa:
        go("anvisa_monthly", _py("anvisa_open_data_agents/run_batch.py", "--monthly", "--limit", "5", *ssl_flags), timeout=3600)
    else:
        steps.append({"step": "anvisa_monthly", "ok": True, "skipped": True})

    go("user_profiles", _py("global_expansion/build_user_profiles.py"), timeout=120)

    go("i18n_world", _py("global_expansion/build_i18n_world.py"), timeout=180)

    go("resource_progress", _py("resource_expansion/update_progress.py"), timeout=120)

    go("games_m25", _py("resource_expansion/build_games.py"), timeout=120)

    if not skip_audit and not quick:
        go("full_audit", _py("run_full_audit.py"), timeout=7200)
    elif quick:
        go("audit_ecosystem", _py("audit_ecosystem_coverage.py"), timeout=600)
        steps.append({"step": "full_audit", "ok": True, "skipped": True, "reason": "quick mode"})

    go(
        "minify_assets",
        _py("optimize_assets.py", "--all", "--apply-build", "--in-place"),
        timeout=600,
    )

    if not skip_build:
        go(
            "website_i18n_build",
            _py("generate_website_pt.py", "--optimize-assets", "--no-zip"),
            timeout=7200,
        )
    else:
        steps.append({"step": "website_i18n_build", "ok": True, "skipped": True})

    go("content_pending_validate", _py("content/validate_content.py"), timeout=300)

    inv_ok = go("pending_inventory", _py("run_pending_agents.py", "--inventory"), timeout=120)
    if steps and steps[-1]["step"] == "pending_inventory" and not inv_ok:
        # Exit 1 = há pendências — esperado, não falha de wrap-up
        steps[-1]["ok"] = True
        steps[-1]["informational"] = True
        steps[-1]["note"] = "pending items remain (exit 1 expected)"

    # Snapshot final
    sys.path.insert(0, str(SCRIPTS))
    snapshot: dict[str, Any] = {}
    try:
        from monitor_progress import collect  # noqa: WPS433

        snapshot["progress"] = collect(refresh_resource=True)
    except Exception as exc:
        snapshot["progress_error"] = str(exc)

    audit_path = ROOT / "datasets" / "metadata" / "full_audit_report.json"
    if audit_path.is_file():
        audit_doc = json.loads(audit_path.read_text(encoding="utf-8"))
        snapshot["audit_passed"] = audit_doc.get("passed")
        snapshot["audit_score_pct"] = audit_doc.get("summary", {}).get("completeness_score_pct")

    asset_report = ROOT / "datasets" / "metadata" / "asset_optimization_report.json"
    if asset_report.is_file():
        snapshot["asset_optimization"] = json.loads(asset_report.read_text(encoding="utf-8"))

    i18n_cov = ROOT / "datasets" / "master-data" / "global-expansion" / "i18n_coverage_report.json"
    if i18n_cov.is_file():
        snapshot["i18n"] = json.loads(i18n_cov.read_text(encoding="utf-8"))

    ok_count = sum(1 for s in steps if s.get("ok") and not s.get("skipped"))
    fail_count = sum(1 for s in steps if s.get("ok") is False)

    report = {
        "schema_version": "2026.2.12-project-wrapup",
        "generated_at": NOW(),
        "ok": fail_count == 0,
        "steps_ok": ok_count,
        "steps_fail": fail_count,
        "steps": steps,
        "snapshot": snapshot,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(REPORT.relative_to(ROOT))
    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Wrap-up: auditoria + minify + i18n + inventário")
    p.add_argument("--skip-audit", action="store_true")
    p.add_argument("--skip-build", action="store_true", help="Não regenerar website")
    p.add_argument("--quick", action="store_true", help="Auditoria rápida (ecosystem only)")
    p.add_argument("--skip-anvisa", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    report = run_wrapup(
        skip_audit=args.skip_audit,
        skip_build=args.skip_build,
        skip_anvisa=args.skip_anvisa,
        quick=args.quick,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"\n=== Wrap-up: {'PASS' if report['ok'] else 'FAIL'} ===")
        print(f"Steps OK: {report['steps_ok']} | FAIL: {report['steps_fail']}")
        snap = report.get("snapshot", {})
        if snap.get("audit_score_pct") is not None:
            print(f"Auditoria score: {snap['audit_score_pct']}%")
        if snap.get("i18n"):
            i = snap["i18n"]
            print(f"i18n: {i.get('home_translated', '?')}/{i.get('site_locales', '?')} homes traduzidas")
        print(f"Relatório: {report['report_path']}")

    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
