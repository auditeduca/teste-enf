#!/usr/bin/env python3
"""CLI — legislação brasileira (CF, LOSUS, profissional, ferramentas).

  python scripts/brazilian_legislation_agents/run_batch.py --discover
  python scripts/brazilian_legislation_agents/run_batch.py --fetch
  python scripts/brazilian_legislation_agents/run_batch.py --refresh
  python scripts/brazilian_legislation_agents/run_batch.py --validate
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from discover import discover  # noqa: E402
from extract import extract_all  # noqa: E402
from fetch_stage import fetch_all  # noqa: E402
from graph import run_pipeline  # noqa: E402
from validate_program import run_validation  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--discover", action="store_true")
    p.add_argument("--fetch", action="store_true")
    p.add_argument("--extract", action="store_true")
    p.add_argument("--refresh", action="store_true", help="Pipeline completo")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--all-sources", action="store_true", help="Fetch all, not only stale")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.validate:
        rep = run_validation()
        result = {"ok": rep.ok, "errors": rep.errors, "warnings": rep.warnings}
    elif args.discover:
        result = discover(limit=args.limit if args.limit else None)
    elif args.fetch:
        result = fetch_all(limit=args.limit if args.limit else None, only_stale=not args.all_sources)
    elif args.extract:
        result = extract_all(limit=args.limit if args.limit else None)
    elif args.refresh:
        result = run_pipeline(limit=args.limit, only_stale=not args.all_sources, apply=True)
    else:
        result = run_pipeline(limit=args.limit, only_stale=not args.all_sources, apply=True)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.validate:
            print(f"Validação: {'OK' if result['ok'] else 'FAIL'} — {len(result['errors'])} erros")
        elif args.discover:
            print(f"Discover: {result['stale']} desatualizadas / {result['total']} fontes")
        elif args.fetch:
            print(f"Fetch: {result.get('fetched_ok')}/{result.get('total')} OK")
        elif args.extract:
            print(f"Extract: {result.get('articles_extracted')} artigos")
        elif args.refresh or True:
            print(
                f"Pipeline: provisions={result.get('provisions_structured')} "
                f"corpus={result.get('corpus_updated')} ok={result.get('ok')}"
            )

    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
