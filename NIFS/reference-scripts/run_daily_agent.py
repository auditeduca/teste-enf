#!/usr/bin/env python3
"""Agente diário — um ciclo de finalização (24h).

  python scripts/run_daily_agent.py
  python scripts/run_daily_agent.py --full-audit
  python scripts/run_daily_agent.py --rebuild-site --llm
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "daily_agent"))

from orchestrator import REPORT, STATE, run_daily_cycle  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Agente diário — finaliza pendências")
    p.add_argument("--llm", action="store_true")
    p.add_argument("--full-audit", action="store_true", help="Auditoria completa (default: ecosystem)")
    p.add_argument("--rebuild-site", action="store_true", help="Regenerar website i18n")
    p.add_argument("--med-limit", type=int, default=25)
    p.add_argument("--asset-limit", type=int, default=50)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    report = run_daily_cycle(
        use_llm=args.llm,
        med_limit=args.med_limit,
        asset_limit=args.asset_limit,
        full_audit=args.full_audit,
        rebuild_site=args.rebuild_site,
    )

    if report.get("locked"):
        print("Agente diario: LOCKED (ja em execucao)")
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"=== Daily agent: {'COMPLETE' if report.get('platform_complete') else 'IN_PROGRESS'} ===")
        print(f"Steps OK: {report.get('steps_ok')} | FAIL: {report.get('steps_fail')}")
        print(f"Pendencias: {report.get('actions_before')} -> {report.get('actions_after')}")
        print(f"Proximo ciclo: {report.get('next_run_at')}")
        print(f"Relatorio: {report.get('report_path', REPORT)}")

    if STATE.is_file() and not args.json:
        st = json.loads(STATE.read_text(encoding="utf-8"))
        if st.get("platform_complete"):
            print("\nPlataforma sem pendencias criticas. Loop pode parar com --stop-when-complete.")

    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
