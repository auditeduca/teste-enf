#!/usr/bin/env python3
"""CLI — Clinical Article Factory (dores + soluções + soft skills por ferramenta).

  python scripts/clinical_article_agents/run_batch.py --pilot --apply
  python scripts/clinical_article_agents/run_batch.py --tool TOOL.INFUSION --apply
  python scripts/clinical_article_agents/run_batch.py --all --apply
  python scripts/clinical_article_agents/run_batch.py --status
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from article_builder import build_pair  # noqa: E402
from merge import merge_articles  # noqa: E402
from paths import load_tools_catalog  # noqa: E402
from status import collect_status  # noqa: E402

PILOT_TOOLS = [
    "TOOL.INFUSION",
    "TOOL.CAPURRO",
    "TOOL.APGAR",
    "TOOL.BRADEN",
    "TOOL.GCS",
    "TOOL.BMI",
    "TOOL.MCG_KG_MIN",
    "TOOL.INSULIN",
]


def main() -> int:
    p = argparse.ArgumentParser(description="Clinical Article Factory")
    p.add_argument("--status", action="store_true")
    p.add_argument("--pilot", action="store_true", help="8 ferramentas prioritárias com dores detalhadas")
    p.add_argument("--all", action="store_true", help="Todas as ferramentas do catálogo (usa defaults por categoria)")
    p.add_argument("--tool", metavar="TOOL.CODE", help="Uma ferramenta específica")
    p.add_argument("--apply", action="store_true", help="Gravar em datasets/content/editorial/articles.json")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.status:
        result = collect_status()
    else:
        if args.tool:
            tools = [args.tool]
        elif args.pilot:
            tools = PILOT_TOOLS
        elif args.all:
            tools = [t["tool_code"] for t in load_tools_catalog()]
        else:
            tools = PILOT_TOOLS

        records = []
        errors = []
        for tc in tools:
            try:
                records.extend(build_pair(tc))
            except Exception as exc:
                errors.append({"tool": tc, "error": str(exc)})

        if args.apply:
            merge_result = merge_articles(records)
            result = {"ok": not errors, "generated": len(records), "errors": errors, **merge_result}
        else:
            result = {"ok": not errors, "generated": len(records), "errors": errors, "records": records}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.status:
            print(
                f"Artigos: {result['articles_total']} total · "
                f"{result['problem_articles']} problema · {result['solution_articles']} solução · "
                f"{result['tools_with_articles']} ferramentas"
            )
        else:
            print(f"Gerados: {result.get('generated', 0)} artigos · ok={result.get('ok')}")
            if args.apply:
                print(f"  +{result.get('added', 0)} novos · ~{result.get('updated', 0)} atualizados · total={result.get('total')}")

    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
