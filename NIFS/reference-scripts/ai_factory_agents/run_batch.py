"""CLI — Nursing AI Factory."""
from __future__ import annotations

import argparse
import json

from status import collect_status
from workflow_runner import run_workflow


def main() -> None:
    p = argparse.ArgumentParser(description="Nursing AI Factory — internal autonomous development")
    p.add_argument("--status", action="store_true")
    p.add_argument("--run", help='Brief e.g. "Nova calculadora MEWS"')
    p.add_argument("--workflow", default="new_clinical_tool")
    p.add_argument("--full", action="store_true", help="Run all workflow steps, not phase1 only")
    p.add_argument("--no-persist", action="store_true")
    args = p.parse_args()

    if args.status:
        print(json.dumps(collect_status(), ensure_ascii=False, indent=2))
        return
    if args.run:
        print(json.dumps(run_workflow(
            args.run,
            workflow_id=args.workflow,
            phase1_only=not args.full,
            persist=not args.no_persist,
        ), ensure_ascii=False, indent=2))
        return
    print(json.dumps(collect_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
