#!/usr/bin/env python3
"""Wrapper: python3 scripts/sync_cko_apgar_v3.py → compiler."""
from __future__ import annotations

import sys

from compiler.tools.apgar import build_apgar


def main() -> int:
    build_apgar()
    print("Sincronizado via compiler (CKO-APGAR-001 + overlay → apgar-cko.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
