#!/usr/bin/env python3
"""Carreiras globais — Brasil + 195 países.

  python scripts/career_agents/run_careers.py --rebuild
  python scripts/career_agents/run_careers.py --all --no-llm
  python scripts/career_agents/run_careers.py --countries BR,US,PT --llm
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "career_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar_agents.llm import get_api_key  # noqa: E402
from orchestrator import run_careers  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Todos os 195 países")
    parser.add_argument("--countries", type=str, help="BR,US,PT,...")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--llm", action="store_true")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    countries = None
    if args.countries:
        countries = [x.strip().upper() for x in args.countries.split(",") if x.strip()]
    limit = 195 if args.all else args.limit

    use_llm = not args.no_llm and (args.llm or bool(get_api_key(args.api_key)))
    report = run_careers(
        countries=countries,
        limit=limit,
        api_key=get_api_key(args.api_key),
        use_llm=use_llm,
        rebuild=args.rebuild or args.all,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=== Careers Global ===")
        print(f"Validação: {'OK' if report.get('validation_ok') else 'FAIL'}")
        print(f"Países: {report.get('countries_ok')}/{report.get('countries_processed')}")
        print(f"Salvo: {report.get('run_path', '')}")

    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
