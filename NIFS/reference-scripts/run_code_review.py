#!/usr/bin/env python3
"""CLI — LangGraph code review with DeepSeek (skips large / node_modules / nodes)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from review.graph import run_review_graph  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Revisão de código via LangGraph + DeepSeek")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=["scripts", "platform/src"],
        help="Pastas/arquivos relativos ao repo (default: scripts platform/src)",
    )
    parser.add_argument("--focus", default="", help="Instrução extra para o revisor")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--json", action="store_true", help="Emitir JSON em stdout")
    args = parser.parse_args()

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("Defina DEEPSEEK_API_KEY", file=sys.stderr)
        return 1

    repo = ROOT.parent
    result = run_review_graph(
        root=repo,
        target_paths=args.paths,
        api_key=api_key,
        model=args.model,
        focus=args.focus,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["report"])
        if result.get("error"):
            print(f"\n[erro] {result['error']}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
