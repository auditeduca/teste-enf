#!/usr/bin/env python3
"""
finalize_base.py — LangGraph + DeepSeek: Read → Plan → Review → Validate → Execute.

Finaliza a base NKOS com backup OBRIGATÓRIO e gate de precisão ≥95% (default).

Uso:
  python scripts/finalize_base.py --validate-only     # gate sem upload
  python scripts/finalize_base.py --execute           # pipeline completo (dry-run)
  python scripts/finalize_base.py --execute --live    # upload real
  python scripts/finalize_base.py --backup-only
  python scripts/finalize_base.py --legacy --execute  # pipeline antigo
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "database_sync_agents"))

from agent_common.env_loader import load_project_env  # noqa: E402


def main() -> int:
    load_project_env()

    p = argparse.ArgumentParser(description="NKOS — Finalizar base (LangGraph + DeepSeek)")
    p.add_argument("--plan", action="store_true", help="Só planejar (DeepSeek)")
    p.add_argument("--execute", action="store_true", help="Pipeline completo")
    p.add_argument("--backup-only", action="store_true")
    p.add_argument("--full-backup", action="store_true")
    p.add_argument("--restore", metavar="BKP_ID")
    p.add_argument("--target", choices=["supabase", "firebase", "both"], default="supabase")
    p.add_argument("--tiers", nargs="*", default=["tier1_core", "tier2_clinical", "tier3_content"])
    p.add_argument("--llm", action="store_true", default=True)
    p.add_argument("--no-llm", action="store_true")
    p.add_argument("--live", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--legacy", action="store_true", help="Pipeline sem LangGraph")
    p.add_argument("--validate-only", action="store_true", help="Para no validate (sem execute)")
    p.add_argument("--min-score", type=float, default=95.0)
    args = p.parse_args()

    from backup import create_security_backup, list_backups, restore_backup  # noqa: E402
    from reader import build_context_snapshot  # noqa: E402

    if args.restore:
        result = restore_backup(args.restore, dry_run=not args.live)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1

    if args.backup_only:
        result = create_security_backup(full=args.full_backup, tiers=args.tiers, label="manual_backup")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    use_llm = args.llm and not args.no_llm
    api_key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()

    if not args.legacy:
        from finalize_graph import run_finalize_graph  # noqa: E402

        if args.plan and not args.execute and not args.validate_only:
            result = run_finalize_graph(
                tiers=args.tiers,
                target=args.target,
                api_key=api_key,
                use_llm=use_llm,
                live=False,
                force=args.force,
                min_score=args.min_score,
                execute_enabled=False,
                validate_only=True,
            )
            out = {k: v for k, v in result.items() if k not in ("context",)}
            print(json.dumps(out, indent=2, ensure_ascii=False))
            return 0 if result.get("ok") else 1

        if args.execute or args.validate_only:
            result = run_finalize_graph(
                tiers=args.tiers,
                target=args.target,
                api_key=api_key,
                use_llm=use_llm,
                live=args.live,
                force=args.force,
                min_score=args.min_score,
                execute_enabled=not args.validate_only,
                validate_only=args.validate_only,
            )
            out = {k: v for k, v in result.items() if k not in ("context",)}
            print(json.dumps(out, indent=2, ensure_ascii=False))
            return 0 if result.get("ok") else 1

    # Legacy pipeline
    from executor_agent import execute_plan  # noqa: E402
    from planner_agent import plan_finalize  # noqa: E402

    payload = {"live": args.live, "force": args.force, "use_llm": use_llm}

    if args.plan and not args.execute:
        plan = plan_finalize(tiers=args.tiers, target=args.target, use_llm=use_llm, payload=payload)
        print(json.dumps({k: v for k, v in plan.items() if k != "context"}, indent=2, ensure_ascii=False))
        return 0

    if args.execute:
        backup = create_security_backup(full=args.full_backup, tiers=args.tiers, label="pre_finalize_execute")
        plan = plan_finalize(tiers=args.tiers, target=args.target, use_llm=use_llm, payload=payload)
        if plan.get("blockers_before_execute") and not args.force:
            print(json.dumps({"ok": False, "blockers": plan["blockers_before_execute"], "backup_id": backup.get("backup_id")}, indent=2))
            return 2
        report = execute_plan(plan, payload=payload, stop_on_error=not args.force)
        report["backup_id"] = backup.get("backup_id")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report.get("ok") else 1

    ctx = build_context_snapshot(tiers=args.tiers)
    print(json.dumps({
        "program": "finalize_base",
        "engine": "langgraph" if not args.legacy else "legacy",
        "validation_ok": ctx.get("validation_ok"),
        "min_score_default": args.min_score,
        "backups": [b.get("backup_id") for b in list_backups(5)],
        "commands": {
            "validate_gate": "python scripts/finalize_base.py --validate-only",
            "execute_dry": "python scripts/finalize_base.py --execute",
            "execute_live": "python scripts/finalize_base.py --execute --live",
        },
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
