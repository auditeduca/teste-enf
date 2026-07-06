"""CLI — pipeline agentes conteúdo pendente."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))
sys.path.insert(1, str(ROOT / "scripts"))
sys.path.insert(2, str(ROOT / "scripts" / "apgar_agents"))

from apgar_agents.llm import get_api_key, resolve_model  # noqa: E402
from content.field_registry import field_docs, modules  # noqa: E402
from content_agents.validators import validate_all_fields  # noqa: E402

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
RUNS_DIR = ROOT / "datasets" / "master-data" / "content-pending" / "agent_runs"


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline agentes conteúdo (LangGraph + DeepSeek)")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--field", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--llm", action="store_true")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.validate_only:
        result = validate_all_fields()
        print(f"Checks: {result['checks']} | Errors: {len(result['errors'])}")
        return 1 if result["errors"] else 0

    use_llm = not args.no_llm and (args.llm or bool(get_api_key(args.api_key)))
    api_key = get_api_key(args.api_key)
    model = resolve_model(args.model)
    if use_llm and not api_key:
        use_llm = False

    import graph as content_graph

    run_field = content_graph.run_field
    run_all_agent_fields = content_graph.run_all_agent_fields

    if args.field:
        outputs = [run_field(args.field, api_key=api_key, model=model, use_llm=use_llm)]
    elif args.all:
        outputs = run_all_agent_fields(api_key=api_key, model=model, use_llm=use_llm)
    else:
        parser.print_help()
        return 2

    print(f"=== Content Field Pipeline ({len(outputs)} campos) ===")
    for out in outputs:
        v = out.get("validation") or {}
        print(f"  {out['field_id']}: {'PASS' if v.get('validation_passed') else 'FAIL'}")

    if args.json:
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        path = RUNS_DIR / f"run_{NOW.replace(':', '').replace('-', '')[:15]}.json"
        path.write_text(
            json.dumps(
                {
                    "generated_at": NOW,
                    "program_code": "CONTENT_PENDING",
                    "llm_enabled": use_llm,
                    "runs": outputs,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Salvo: {path.relative_to(ROOT)}")

    failed = sum(1 for o in outputs if not (o.get("validation") or {}).get("validation_passed"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
