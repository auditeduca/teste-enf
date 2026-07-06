"""CLI — pipeline agentes APGAR (LangGraph + DeepSeek).

Exemplos:
  python scripts/apgar_agents/run_field_pipeline.py --validate-only
  python scripts/apgar_agents/run_field_pipeline.py --field APGAR.scl.score_max --llm
  python scripts/apgar_agents/run_field_pipeline.py --all --llm --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar.field_registry import field_docs, modules  # noqa: E402
from apgar_agents.llm import get_api_key, resolve_model  # noqa: E402
from apgar_agents.validators import validate_all_fields  # noqa: E402

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
RUNS_DIR = ROOT / "datasets" / "master-data" / "apgar" / "agent_runs"


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline agentes APGAR (LangGraph + DeepSeek)")
    parser.add_argument("--validate-only", action="store_true", help="Só validação determinística")
    parser.add_argument("--field", type=str, help="field_id específico")
    parser.add_argument("--all", action="store_true", help="Todos os campos com agent_roles")
    parser.add_argument("--llm", action="store_true", help="Usar DeepSeek nos nós generate/review")
    parser.add_argument("--no-llm", action="store_true", help="Forçar modo determinístico")
    parser.add_argument("--model", default=None, help="Modelo DeepSeek (default: deepseek-v4-flash)")
    parser.add_argument("--api-key", default=None, help="DeepSeek API key (ou DEEPSEEK_API_KEY)")
    parser.add_argument("--json", action="store_true", help="Salvar run em agent_runs/")
    args = parser.parse_args()

    if args.validate_only:
        result = validate_all_fields()
        print("=== APGAR Validate Agent (deterministico) ===")
        print(f"Checks: {result['checks']} | Errors: {len(result['errors'])} | Warnings: {len(result['warnings'])}")
        for e in result["errors"]:
            print(f"  FAIL {e['field_id']}: {e['message']}")
        return 1 if result["errors"] else 0

    use_llm = not args.no_llm and (args.llm or bool(get_api_key(args.api_key)))
    api_key = get_api_key(args.api_key)
    model = resolve_model(args.model)

    if use_llm and not api_key:
        print("AVISO: --llm ativo mas DEEPSEEK_API_KEY ausente — modo deterministico.")
        use_llm = False

    from graph import run_all_agent_fields, run_field  # noqa: E402

    if args.field:
        outputs = [run_field(args.field, api_key=api_key, model=model, use_llm=use_llm)]
    elif args.all:
        outputs = run_all_agent_fields(api_key=api_key, model=model, use_llm=use_llm)
    else:
        parser.print_help()
        return 2

    print(f"=== APGAR Field Pipeline ({len(outputs)} campos) ===")
    print(f"LLM: {'DeepSeek ' + model if use_llm else 'deterministico'}")
    for out in outputs:
        fid = out["field_id"]
        v = out.get("validation") or {}
        status = "PASS" if v.get("validation_passed") else "FAIL"
        print(f"  {fid}: {status} | trace: {' -> '.join(out.get('trace', []))}")

    if args.json:
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        path = RUNS_DIR / f"run_{NOW.replace(':', '').replace('-', '')[:15]}.json"
        payload = {
            "generated_at": NOW,
            "concept_code": "APGAR",
            "llm_enabled": use_llm,
            "model": model,
            "modules_completion_pct": modules().get("overall_completion_pct"),
            "runs": outputs,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nSalvo: {path.relative_to(ROOT)}")

    failed = sum(1 for o in outputs if not (o.get("validation") or {}).get("validation_passed"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
