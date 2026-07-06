#!/usr/bin/env python3
"""Resource expansion — build, sync assets, slides.

  python scripts/resource_expansion_agents/run_resources.py --all
  python scripts/resource_expansion_agents/run_resources.py --sync-assets --limit 30
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "resource_expansion"))
sys.path.insert(0, str(ROOT / "scripts" / "resource_expansion_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar_agents.llm import get_api_key  # noqa: E402
from orchestrator import run_resources  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true")
    p.add_argument("--rebuild", action="store_true")
    p.add_argument("--sync-assets", action="store_true")
    p.add_argument("--slides", action="store_true")
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--med-dict-limit", type=int, default=None, help="Lote DICT (default: inventário)")
    p.add_argument("--use-inventory", action="store_true", default=True)
    p.add_argument("--no-med-dict", action="store_true")
    p.add_argument("--llm", action="store_true")
    p.add_argument("--no-llm", action="store_true")
    p.add_argument("--api-key", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    use_llm = not args.no_llm and (args.llm or bool(get_api_key(args.api_key)))
    report = run_resources(
        rebuild=args.rebuild or args.all,
        sync_assets=args.sync_assets or args.all,
        build_slides=args.slides or args.all,
        asset_limit=args.limit,
        api_key=get_api_key(args.api_key),
        use_llm=use_llm,
        run_medication_dictionary=not args.no_med_dict,
        medication_dict_limit=args.med_dict_limit,
        use_pending_inventory=args.use_inventory,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"=== Resource Expansion ===")
        print(f"Validação: {'OK' if report.get('validation_ok') else 'FAIL'}")
        print(f"Assets: {report.get('asset_sync', {})}")
        print(f"Slides: {report.get('slides_built', 0)}")
        md = report.get("medication_dictionary") or {}
        print(f"Medicamentos DICT: {md.get('applied', 0)} aplicados")
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
