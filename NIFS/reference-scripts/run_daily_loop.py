#!/usr/bin/env python3
"""Loop 24h — agente diario ate concluir pendencias.

  python scripts/run_daily_loop.py
  python scripts/run_daily_loop.py --interval 12h --max-runs 10
  python scripts/run_daily_loop.py --stop-when-complete
  python scripts/run_daily_loop.py --once

Equivalente local ao cron CI (.github/workflows/daily-platform-loop.yml).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "datasets" / "metadata" / "daily_agent_state.json"


def _parse_interval(raw: str) -> int:
    raw = raw.strip().lower()
    m = re.match(r"^(\d+(?:\.\d+)?)(s|m|h|d)?$", raw)
    if not m:
        raise ValueError(f"intervalo invalido: {raw}")
    val = float(m.group(1))
    unit = m.group(2) or "h"
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    return int(val * mult)


def _is_complete() -> bool:
    if not STATE.is_file():
        return False
    try:
        st = json.loads(STATE.read_text(encoding="utf-8"))
        return bool(st.get("platform_complete"))
    except json.JSONDecodeError:
        return False


def main() -> int:
    p = argparse.ArgumentParser(description="Loop agente diario (default 24h)")
    p.add_argument("--interval", default="24h", help="Ex: 24h, 12h, 30m")
    p.add_argument("--max-runs", type=int, default=0, help="0 = infinito")
    p.add_argument("--stop-when-complete", action="store_true", help="Para quando inventario vazio")
    p.add_argument("--once", action="store_true", help="Um ciclo apenas")
    p.add_argument("--llm", action="store_true")
    p.add_argument("--full-audit", action="store_true")
    p.add_argument("--rebuild-site", action="store_true")
    args = p.parse_args()

    interval_s = _parse_interval(args.interval)
    agent_cmd = [sys.executable, str(ROOT / "scripts" / "run_daily_agent.py")]
    if args.llm:
        agent_cmd.append("--llm")
    if args.full_audit:
        agent_cmd.append("--full-audit")
    if args.rebuild_site:
        agent_cmd.append("--rebuild-site")

    runs = 0
    print(f"=== Daily loop: intervalo {args.interval} ({interval_s}s) ===")
    print(f"Comando: {' '.join(agent_cmd)}")

    while True:
        runs += 1
        print(f"\n--- Ciclo #{runs} @ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC ---")
        proc = subprocess.run(agent_cmd, cwd=str(ROOT))
        complete = _is_complete()
        print(f"Exit: {proc.returncode} | platform_complete={complete}")

        if args.once:
            return proc.returncode

        if args.stop_when_complete and complete:
            print("Pendencias zeradas — loop encerrado.")
            return 0

        if args.max_runs and runs >= args.max_runs:
            print(f"Max runs ({args.max_runs}) atingido.")
            return proc.returncode

        print(f"Aguardando {args.interval}...")
        time.sleep(interval_s)


if __name__ == "__main__":
    sys.exit(main())
