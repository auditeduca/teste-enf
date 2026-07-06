#!/usr/bin/env python3
"""Gera + aprova conteúdos pendentes até esvaziar a fila.

  python scripts/content/process_pending.py
  python scripts/content/process_pending.py --limit 20 --max-batches 10
  python scripts/content/process_pending.py --llm
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "content"))

from field_registry import pending_items  # noqa: E402
from workflow_runner import approve_workflow, run_bulk  # noqa: E402
from workflow_store import list_workflows  # noqa: E402


def _pending_count() -> int:
    return sum(
        1
        for i in pending_items().get("items", [])
        if i.get("status") in ("pending", "draft")
    )


def approve_all_awaiting() -> dict:
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
            errors.append({"entity_code": code, "error": str(exc)})
    return {"approved": approved, "skipped": skipped, "errors": errors}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=20, help="Itens por lote de geração")
    p.add_argument("--max-batches", type=int, default=50)
    p.add_argument("--artifact-type", default="")
    p.add_argument("--llm", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    batches: list[dict] = []
    start = _pending_count()

    for batch_num in range(1, args.max_batches + 1):
        pending = _pending_count()
        if pending == 0:
            break

        gen = run_bulk(
            artifact_type=args.artifact_type or None,
            limit=min(args.limit, pending),
            use_llm=args.llm,
        )
        appr = approve_all_awaiting()
        batches.append({
            "batch": batch_num,
            "pending_before": pending,
            "generated": gen.get("processed", 0),
            "gen_errors": gen.get("errors", []),
            "approved": len(appr["approved"]),
            "skipped": len(appr["skipped"]),
            "approve_errors": appr["errors"],
        })

        if gen.get("processed", 0) == 0 and not appr["approved"] and not appr["skipped"]:
            break

    end = _pending_count()
    applied = sum(1 for i in pending_items().get("items", []) if i.get("status") == "applied")
    result = {
        "pending_start": start,
        "pending_end": end,
        "applied_total": applied,
        "batches_run": len(batches),
        "batches": batches,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Fila: {start} -> {end} | gravados: {applied} | lotes: {len(batches)}")
        for b in batches:
            print(
                f"  lote {b['batch']}: gerados {b['generated']}, "
                f"aprovados {b['approved']}, skip {b['skipped']}, erros gen {len(b['gen_errors'])}"
            )

    return 0 if end == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
