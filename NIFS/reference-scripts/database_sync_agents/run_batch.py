#!/usr/bin/env python3
"""CLI — Database Sync Agent."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "database_sync_agents"))

from agent_common.env_loader import load_project_env  # noqa: E402
from orchestrator import run_pipeline  # noqa: E402
from status import collect_status  # noqa: E402


def main() -> int:
    load_project_env()
    p = argparse.ArgumentParser(description="NKOS Database Sync — Supabase + Firebase")
    p.add_argument("--status", action="store_true")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--sync", action="store_true")
    p.add_argument("--target", choices=["supabase", "firebase", "both"], default="supabase")
    p.add_argument("--tier", default="tier1_core")
    p.add_argument("--entities", nargs="*", help="Entity keys e.g. Country MasterEntity")
    p.add_argument("--llm", action="store_true", help="DeepSeek semantic validation")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--live", action="store_true", help="Disable dry-run (upload real)")
    args = p.parse_args()

    if args.status:
        print(json.dumps(collect_status(), indent=2, ensure_ascii=False))
        return 0

    dry_run = not args.live
    if args.dry_run:
        dry_run = True

    if args.validate or args.sync:
        result = run_pipeline(
            entity_keys=args.entities,
            tier=args.tier if not args.entities else None,
            target=args.target,
            use_llm=args.llm,
            dry_run=dry_run,
            validate_only=args.validate and not args.sync,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
