#!/usr/bin/env python3
"""Compila uma ferramenta: python3 -m compiler.build_tool --tool apgar"""
from __future__ import annotations

import argparse
import sys

from compiler.tools.apgar import build_apgar

BUILDERS = {
    "apgar": build_apgar,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NIFS Compiler — build por ferramenta")
    parser.add_argument("--tool", required=True, choices=sorted(BUILDERS))
    args = parser.parse_args(argv)
    builder = BUILDERS[args.tool]
    entries = builder()
    for e in entries:
        print(f"  → {e['path']}")
    print(f"OK: {args.tool} ({len(entries)} artefato(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
