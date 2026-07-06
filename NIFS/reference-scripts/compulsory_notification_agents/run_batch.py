#!/usr/bin/env python3
"""CLI — agente notificação compulsória (BR nacional + estadual).

  python scripts/compulsory_notification_agents/run_batch.py --scrape
  python scripts/compulsory_notification_agents/run_batch.py --catalog
  python scripts/compulsory_notification_agents/run_batch.py --scrape --limit 10
  python scripts/compulsory_notification_agents/run_batch.py --validate
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "compulsory_notification_agents"))

from apgar_agents.llm import get_api_key  # noqa: E402
from catalog import build_queue  # noqa: E402
from graph import run_batch, run_item, run_scrape  # noqa: E402
from validate_program import run_validation  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--scrape", action="store_true")
    p.add_argument("--catalog", action="store_true")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--scrape-limit", type=int, default=None)
    p.add_argument("--pending-id", default="")
    p.add_argument("--llm", action="store_true")
    p.add_argument("--no-apply", action="store_true")
    p.add_argument("--api-key", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    use_llm = args.llm and bool(get_api_key(args.api_key))

    if args.validate:
        rep = run_validation()
        result = {"ok": rep.ok, "errors": rep.errors, "warnings": rep.warnings}
    elif args.scrape and not args.catalog and not args.pending_id:
        result = run_scrape(limit=args.scrape_limit)
    elif args.catalog:
        if args.scrape:
            run_scrape(limit=args.scrape_limit)
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
            limit=args.limit,
            api_key=get_api_key(args.api_key),
            use_llm=use_llm,
            apply=not args.no_apply,
            scrape_first=args.scrape,
            scrape_limit=args.scrape_limit,
        )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.validate:
            print(f"Validação: {'OK' if result['ok'] else 'FAIL'} — {len(result['errors'])} erros")
        elif args.scrape and not args.catalog and not args.pending_id and "results" in result:
            print(f"Raspagem: {result.get('fetched_ok')}/{result.get('total')} OK")
        elif args.catalog:
            print(f"Fila: {result['total']} pendentes | estruturados: {result['already_structured']}")
        elif args.pending_id:
            print(f"{result.get('entity_code')} → {result.get('status')}")
        else:
            print(f"Processados: {result['processed']} | aplicados: {result['applied']} | erros: {len(result['errors'])}")

    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
