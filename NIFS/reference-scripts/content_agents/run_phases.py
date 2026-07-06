"""CLI — micro-fases M1–M9 conteúdo pendente."""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))

from phases.registry import PHASE_AGENTS  # noqa: E402

RUNS_DIR = ROOT / "datasets" / "master-data" / "content-pending" / "agent_runs"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=str, help="M1..M9")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    agents = PHASE_AGENTS
    if args.phase:
        phase = args.phase.strip().upper()
        agents = [a for a in PHASE_AGENTS if a.phase_id == phase]
        if not agents:
            print(f"Fase desconhecida: {phase}")
            return 2

    results = [dataclasses.asdict(a.run()) for a in agents]
    ok = all(r.get("ok") for r in results)

    if args.json:
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = RUNS_DIR / f"phases_{ts}.json"
        path.write_text(json.dumps({"ok": ok, "results": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"ok": ok, "phases": len(results)}, ensure_ascii=False))
    else:
        for r in results:
            print(f"{r['phase_id']} {r['name_pt']}: {'PASS' if r['ok'] else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
