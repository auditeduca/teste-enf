#!/usr/bin/env python3
"""Aprova todos os workflows em awaiting_approval.

  python scripts/content/auto_approve.py
  python scripts/content/auto_approve.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "content"))

from workflow_runner import approve_workflow  # noqa: E402
from workflow_store import list_workflows  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    awaiting = list_workflows(status="awaiting_approval", limit=500)
    approved, skipped, errors = [], [], []

    for wf in awaiting:
        wid = wf["workflow_id"]
        code = wf.get("entity_code") or wid
        try:
            out = approve_workflow(wid)
            if out.get("apply", {}).get("skipped"):
                skipped.append(code)
            else:
                approved.append(code)
        except Exception as exc:
            errors.append({"workflow_id": wid, "entity_code": code, "error": str(exc)})

    result = {
        "awaiting_found": len(awaiting),
        "approved": approved,
        "skipped_already_applied": skipped,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Aprovados: {len(approved)} | já gravados: {len(skipped)} | erros: {len(errors)}")
        for code in approved:
            print(f"  + {code}")
        for code in skipped:
            print(f"  ~ {code} (skip)")
        for err in errors:
            print(f"  ! {err['entity_code']}: {err['error']}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
