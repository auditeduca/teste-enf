#!/usr/bin/env python3
"""CLI — agente dicionário de medicamentos.

  python scripts/medication_dictionary_agents/run_batch.py --catalog
  python scripts/medication_dictionary_agents/run_batch.py --limit 10
  python scripts/medication_dictionary_agents/run_batch.py --limit 5 --llm
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "medication_dictionary_agents"))

from apgar_agents.llm import get_api_key  # noqa: E402
from catalog import build_queue  # noqa: E402
from graph import run_batch, run_item  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", action="store_true")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--all-pending", action="store_true", help="Processar toda a fila DrugReference→DICT")
    p.add_argument("--pending-id", default="")
    p.add_argument("--llm", action="store_true")
    p.add_argument("--no-apply", action="store_true")
    p.add_argument("--api-key", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    use_llm = args.llm and bool(get_api_key(args.api_key))
    batch_limit = None if args.all_pending else args.limit

    if args.catalog:
        result = build_queue(limit=args.limit if args.limit else None)
    elif args.pending_id:
        result = run_item(
            args.pending_id,
            api_key=get_api_key(args.api_key),
            use_llm=use_llm,
            apply=not args.no_apply,
        )
    else:
        result = run_batch(
            limit=batch_limit,
            api_key=get_api_key(args.api_key),
            use_llm=use_llm,
            apply=not args.no_apply,
        )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.catalog:
            print(f"Fila: {result['total']} pendentes | já vinculados: {result['already_linked']}")
        elif args.pending_id:
            print(f"{result.get('entity_code')} → {result.get('status')}")
        else:
            print(f"Processados: {result['processed']} | aplicados: {result['applied']} | fila: {result.get('queued', '?')} | erros: {len(result['errors'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
