#!/usr/bin/env python3
"""Regenera todos os artefatos DELIVERY derivados (Fase 2)."""
from __future__ import annotations

import sys

from compiler.clinical import build_terminology_bundle, build_tools_catalog
from compiler.manifest import write_manifest
from compiler.tools.apgar import build_apgar
from compiler.tools.glasgow import build_glasgow


def main() -> int:
    artifacts: list[dict] = []
    print("==> Terminologia clínica")
    artifacts.append(build_terminology_bundle("pt-BR"))
    print("==> Catálogo de ferramentas")
    artifacts.append(build_tools_catalog())
    print("==> Ferramenta: apgar")
    artifacts.extend(build_apgar())
    print("==> Ferramenta: glasgow")
    artifacts.extend(build_glasgow())
    print("==> Manifesto")
    artifacts.append(write_manifest(artifacts))
    print(f"\nOK: {len(artifacts)} artefatos em NIFS/DELIVERY/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
