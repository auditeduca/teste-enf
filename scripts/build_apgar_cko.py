#!/usr/bin/env python3
"""Wrapper legado → compiler.build_all (mantém nome para scripts existentes)."""
from __future__ import annotations

import sys

from compiler.build_all import main

if __name__ == "__main__":
    sys.exit(main())
