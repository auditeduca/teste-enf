"""Orquestrador — executa todos os agentes de micro-fase APGAR."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from phases.registry import PHASE_AGENTS  # noqa: E402

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
RUNS = ROOT / "datasets" / "master-data" / "apgar" / "agent_runs"


def main() -> int:
    parser = argparse.ArgumentParser(description="Orquestrador micro-fases APGAR")
    parser.add_argument("--phase", help="M1..M11")
    parser.add_argument("--llm", action="store_true", help="M11 usa translation_graph DeepSeek")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.phase and args.phase.upper() == "M11" and args.llm:
        from apgar_agents.llm import get_api_key, resolve_model  # noqa: E402
        from translation_graph import run_translation_graph  # noqa: E402

        key = get_api_key()
        if not key:
            print("ERRO: DEEPSEEK_API_KEY necessaria para --llm")
            return 2
        out = run_translation_graph(api_key=key, model=resolve_model(), use_llm=True, write=False)
        print(f"M11 Translation LLM: {'PASS' if out.get('ok') else 'FAIL'}")
        if args.json:
            RUNS.mkdir(parents=True, exist_ok=True)
            path = RUNS / f"phase_m11_llm_{NOW.replace(':', '').replace('-', '')[:15]}.json"
            path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return 0 if out.get("ok") else 1

    agents = PHASE_AGENTS
    if args.phase:
        agents = [a for a in PHASE_AGENTS if a.phase_id == args.phase.upper()]
        if not agents:
            print(f"Fase desconhecida: {args.phase}")
            return 2

    results = []
    print("=== APGAR Micro-Phase Agents ===")
    for agent in agents:
        r = agent.run()
        status = "PASS" if r.ok else "FAIL"
        print(f"  {r.phase_id} {r.name_pt}: {status}")
        results.append({
            "phase_id": r.phase_id,
            "name_pt": r.name_pt,
            "ok": r.ok,
            "trace": r.trace,
            "validate": r.validate,
        })

    failed = sum(1 for r in results if not r["ok"])
    print(f"\nTotal: {len(results)} | Fail: {failed}")

    if args.json:
        RUNS.mkdir(parents=True, exist_ok=True)
        path = RUNS / f"phases_{NOW.replace(':', '').replace('-', '')[:15]}.json"
        path.write_text(
            json.dumps({"generated_at": NOW, "results": results}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Salvo: {path.relative_to(ROOT)}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
