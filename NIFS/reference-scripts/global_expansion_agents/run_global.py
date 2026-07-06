#!/usr/bin/env python3
"""Comando único — expansão global (países, idiomas, fusos, perfis, Grau A).

  python scripts/global_expansion_agents/run_global.py --rebuild
  python scripts/global_expansion_agents/run_global.py --all --llm --api-key sk-...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "global_expansion_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar_agents.llm import get_api_key  # noqa: E402
from orchestrator import run_global  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Todos os 4 perfis")
    parser.add_argument("--profiles", type=str, help="estudante,profissional,...")
    parser.add_argument("--rebuild", action="store_true", help="Regenerar registries")
    parser.add_argument("--llm", action="store_true")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--i18n-limit", type=int, default=10, help="Locales por execução LLM")
    parser.add_argument("--careers-limit", type=int, default=10)
    args = parser.parse_args()

    use_llm = not args.no_llm and (args.llm or bool(get_api_key(args.api_key)))
    profiles = None
    if args.profiles:
        profiles = [x.strip() for x in args.profiles.split(",") if x.strip()]
    elif args.all:
        profiles = ["estudante", "profissional", "gestor", "academico"]

    report = run_global(
        profiles=profiles,
        api_key=get_api_key(args.api_key),
        use_llm=use_llm,
        rebuild=args.rebuild or args.all,
        careers_limit=195 if args.all else args.careers_limit,
        i18n_limit=30 if args.all else args.i18n_limit,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        cov = report.get("coverage", {})
        print(f"=== Global Expansion ===")
        print(f"Países: {cov.get('countries')} | Idiomas: {cov.get('languages')} | Locales: {cov.get('locales')}")
        print(f"Validação: {'OK' if report.get('validation_ok') else 'FAIL'}")
        for p in report.get("profiles", []):
            print(f"  Perfil {p.get('profile')}: {'PASS' if p.get('ok') else 'FAIL'}")
        print(f"Salvo: {report.get('run_path', '')}")

    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
