#!/usr/bin/env python3
"""CLI — aprovar Doc 14 / master_code_sequence_proposal.

  python scripts/code_sequence/approve_proposal.py --status
  python scripts/code_sequence/approve_proposal.py --approve --approver "Nome" --all-checks
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "code_sequence"))

from approval import CHECKLIST, approve, get_status, reject  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--status", action="store_true")
    p.add_argument("--approve", action="store_true")
    p.add_argument("--reject", action="store_true")
    p.add_argument("--approver", default="")
    p.add_argument("--notes", default="")
    p.add_argument("--reason", default="")
    p.add_argument("--all-checks", action="store_true", help="Marca todos os itens do checklist")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.approve:
        checklist = {c["id"]: True for c in CHECKLIST} if args.all_checks else {}
        if not args.all_checks:
            print("Use --all-checks ou aprove pela plataforma /code-sequence", file=sys.stderr)
            return 1
        result = approve(approver=args.approver, checklist=checklist, notes=args.notes)
    elif args.reject:
        result = reject(approver=args.approver, reason=args.reason)
    else:
        result = get_status()

    if args.json:
        out = json.dumps(result, ensure_ascii=False, indent=2)
        try:
            print(out)
        except UnicodeEncodeError:
            print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(f"Status: {result['status']} | migrate: {result['can_migrate']}")
        if result.get("approval"):
            print(f"Aprovado por: {result['approval'].get('approver')} em {result['approval'].get('approved_at')}")

    return 0 if result.get("is_approved") or args.status or args.reject else 1


if __name__ == "__main__":
    sys.exit(main())
