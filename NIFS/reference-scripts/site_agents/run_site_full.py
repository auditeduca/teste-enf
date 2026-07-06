#!/usr/bin/env python3
"""Comando único — site zero→100% com agentes (espelho APGAR).

Exemplos:
  python scripts/site_agents/run_site_full.py --all --no-llm
  python scripts/site_agents/run_site_full.py --all --llm --approve
  python scripts/site_agents/run_site_full.py --modules M05_simulados,M08_flashcards --llm
  python scripts/site_agents/run_site_full.py --all --llm --build --bulk-limit 10
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "site_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar_agents.llm import get_api_key, resolve_model  # noqa: E402
from orchestrator import run_all  # noqa: E402
from site_full.field_registry import manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Site full — agentes zero→100%")
    parser.add_argument("--all", action="store_true", help="Todos os módulos M01–M18")
    parser.add_argument("--modules", type=str, help="IDs separados por vírgula (M05_simulados,...)")
    parser.add_argument("--llm", action="store_true")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--bulk-limit", type=int, default=5)
    parser.add_argument("--approve", action="store_true", help="Auto-aprovar workflows content")
    parser.add_argument("--build", action="store_true", help="Incluir build website (M18)")
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list", action="store_true", help="Listar módulos")
    args = parser.parse_args()

    if args.list:
        for m in manifest().get("modules", []):
            print(f"{m['id']:20} {m['code']:22} {m['label_pt']}")
        gaps = manifest().get("gaps_user_should_add", [])
        if gaps:
            print("\n--- Lacunas / não esquecer ---")
            for g in gaps:
                print(f"  • {g}")
        return 0

    if not args.all and not args.modules:
        parser.print_help()
        return 2

    use_llm = not args.no_llm and (args.llm or bool(get_api_key(args.api_key)))
    api_key = get_api_key(args.api_key)
    module_ids = None
    if args.modules:
        module_ids = [x.strip() for x in args.modules.split(",") if x.strip()]

    build = args.build or (args.all and not args.no_build)

    report = run_all(
        module_ids=module_ids,
        api_key=api_key,
        model=resolve_model(args.model),
        use_llm=use_llm,
        bulk_limit=max(1, min(args.bulk_limit, 20)),
        approve=args.approve,
        build=build,
        archive_dry_run=True,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"=== Site Full {report['modules_passed']}/{report['modules_total']} PASS ===")
        for r in report.get("results", []):
            mark = "PASS" if r.get("ok") else "FAIL"
            print(f"  {r.get('module_id', '?'):20} {mark}")
        print(f"\nSalvo: {report.get('run_path', '')}")
        gaps = manifest().get("gaps_user_should_add", [])
        if gaps:
            print("\nLacunas ainda no roadmap:")
            for g in gaps[:5]:
                print(f"  • {g}")
            print(f"  ... +{len(gaps)-5} (ver --list)")

    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
