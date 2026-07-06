#!/usr/bin/env python3
"""CLI — dados abertos ANVISA (dados.gov.br / dados.anvisa.gov.br).

  python scripts/anvisa_open_data_agents/run_batch.py --sync-catalog
  python scripts/anvisa_open_data_agents/run_batch.py --discover
  python scripts/anvisa_open_data_agents/run_batch.py --fetch
  python scripts/anvisa_open_data_agents/run_batch.py --monthly
  python scripts/anvisa_open_data_agents/run_batch.py --validate
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import sync_catalog  # noqa: E402
from discover import discover  # noqa: E402
from extract import extract_all  # noqa: E402
from fetch_stage import fetch_all  # noqa: E402
from graph import run_pipeline  # noqa: E402
from validate_program import run_validation  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="ANVISA open data agents")
    p.add_argument("--sync-catalog", action="store_true", help="Sincroniza catálogo CSV dados.anvisa.gov.br")
    p.add_argument("--discover", action="store_true")
    p.add_argument("--fetch", action="store_true")
    p.add_argument("--extract", action="store_true")
    p.add_argument("--monthly", action="store_true", help="Pipeline mensal completo (sync+fetch stale+apply)")
    p.add_argument("--refresh", action="store_true", help="Alias de --monthly")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--limit", type=int, default=5, help="Máx. datasets prioritários por execução")
    p.add_argument("--all-sources", action="store_true", help="Fetch todos, não só stale")
    p.add_argument("--no-ssl-verify", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    verify_ssl = not args.no_ssl_verify

    if args.validate:
        rep = run_validation()
        result = {"ok": rep.ok, "errors": rep.errors, "warnings": rep.warnings}
    elif args.sync_catalog:
        result = sync_catalog(verify_ssl=verify_ssl)
    elif args.discover:
        result = discover(limit=args.limit if args.limit else None)
    elif args.fetch:
        result = fetch_all(
            limit=args.limit if args.limit else None,
            only_stale=not args.all_sources,
            verify_ssl=verify_ssl,
        )
    elif args.extract:
        result = extract_all(limit=args.limit if args.limit else None)
    elif args.monthly or args.refresh:
        result = run_pipeline(
            limit=args.limit,
            only_stale=not args.all_sources,
            apply=True,
            verify_ssl=verify_ssl,
        )
    else:
        result = run_pipeline(
            limit=args.limit,
            only_stale=not args.all_sources,
            apply=True,
            verify_ssl=verify_ssl,
        )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.validate:
            print(f"Validacao: {'OK' if result['ok'] else 'FAIL'} — {len(result['errors'])} erros")
        elif args.sync_catalog:
            print(f"Catalogo: {result.get('sources_total')} fontes ({result.get('priority_count')} prioritarias)")
        elif args.discover:
            print(f"Discover: {result['stale']} stale / {result['total']} fontes")
        elif args.fetch:
            print(f"Fetch: {result.get('fetched_ok')}/{result.get('total')} OK")
        elif args.extract:
            print(f"Extract: {result.get('rows_extracted')} linhas")
        else:
            print(
                f"Pipeline ANVISA: meds={result.get('medications_structured')} "
                f"links={result.get('links_matched')} ok={result.get('ok')}"
            )

    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
