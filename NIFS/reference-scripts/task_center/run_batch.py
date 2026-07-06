#!/usr/bin/env python3
"""CLI — Task Center executar tarefas."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "task_center"))

from agent_common.env_loader import load_project_env  # noqa: E402


def main() -> int:
    load_project_env()
    p = argparse.ArgumentParser(description="NKOS Task Center")
    p.add_argument("--status", action="store_true")
    p.add_argument("--sync", action="store_true")
    p.add_argument("--list", action="store_true")
    p.add_argument("--run", metavar="TASK_ID")
    p.add_argument("--run-all", action="store_true")
    p.add_argument("--run-pending-agents", action="store_true", help="run_pending_agents.py")
    p.add_argument("--agent", help="PROG agent name e.g. medication_dictionary")
    p.add_argument("--llm", action="store_true")
    p.add_argument("--limit", type=int, default=20)
    args = p.parse_args()

    from registry import list_tasks, sync_registry  # noqa: E402
    from runner import run_batch_tasks, run_task  # noqa: E402

    if args.status:
        from status import collect_status  # noqa: E402
        print(json.dumps(collect_status(), indent=2, ensure_ascii=False))
        return 0

    if args.sync:
        print(json.dumps(sync_registry(), indent=2, ensure_ascii=False)[:2000])
        return 0

    if args.list:
        print(json.dumps(list_tasks(status="all", limit=args.limit), indent=2, ensure_ascii=False))
        return 0

    if args.run_pending_agents:
        sys.path.insert(0, str(ROOT / "scripts" / "database_sync_agents"))
        from agent_executor import run_pending_agents  # noqa: E402
        r = run_pending_agents(use_llm=args.llm)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0 if r.get("ok") else 1

    if args.agent:
        r = run_task(f"PROG.{args.agent}", use_llm=args.llm, limit=args.limit)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0 if r.get("ok") else 1

    if args.run:
        r = run_task(args.run, use_llm=args.llm, limit=args.limit)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0 if r.get("ok") else 1

    if args.run_all:
        sync_registry()
        listed = list_tasks(status="pending", limit=args.limit)
        pending = listed.get("tasks", [])
        pending.sort(key=lambda t: (0 if str(t.get("id", "")).startswith("PROG.") else 1, t.get("priority", 99)))
        ids = [t["id"] for t in pending]
        r = run_batch_tasks(ids, use_llm=args.llm)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0 if r.get("ok") else 1

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
