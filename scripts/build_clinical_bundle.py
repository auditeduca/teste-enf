#!/usr/bin/env python3
"""Wrapper: python3 scripts/build_clinical_bundle.py → compiler."""
from __future__ import annotations

import sys

from compiler.clinical import build_terminology_bundle


def main() -> int:
    build_terminology_bundle("pt-BR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
