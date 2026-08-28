#!/usr/bin/env python3
"""Compila uma ferramenta: python3 -m compiler.build_tool --tool apgar"""
from __future__ import annotations

import argparse
import sys

from compiler.tools.apgar import build_apgar
from compiler.tools.generic import _load_all_tools, build_tool
from compiler.tools.glasgow import build_glasgow

BUILDERS = {
    "apgar": build_apgar,
    "glasgow": build_glasgow,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NIFS Compiler — build por ferramenta")
    parser.add_argument("--tool", required=True)
    args = parser.parse_args(argv)
    if args.tool in BUILDERS:
        entries = BUILDERS[args.tool]()
    else:
        tools = _load_all_tools()
        match = next((t for t in tools if t.get("slug") == args.tool), None)
        if not match:
            print(f"Ferramenta não encontrada: {args.tool}", file=sys.stderr)
            return 1
        entries = build_tool(match, tools)
    for e in entries:
        print(f"  → {e['path']}")
    print(f"OK: {args.tool} ({len(entries)} artefato(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
