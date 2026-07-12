#!/usr/bin/env python3
"""Regenera todos os artefatos DELIVERY derivados (Fase 2 + CKO em lote)."""
from __future__ import annotations

import json
import sys

from compiler.clinical import build_terminology_bundle, build_tools_catalog
from compiler.io import write_generated_json
from compiler.manifest import write_manifest
from compiler.paths import BUNDLES
from compiler.tools.apgar import build_apgar
from compiler.tools.generic import build_all_generic, build_cko_index
from compiler.tools.glasgow import build_glasgow


def build_cko_index_artifact() -> dict:
    payload = {
        "schema_version": "2026.1.0",
        "count": len(build_cko_index()),
        "index": build_cko_index(),
    }
    out = BUNDLES / "cko-index.json"
    return write_generated_json(
        out,
        payload,
        sources=["compiler/tools/generic.py"],
        artifact_key="bundles/cko-index.json",
    )


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
    print("==> CKO genérico (todas as calculadoras)")
    generic = build_all_generic()
    artifacts.extend(generic)
    print(f"    {len(generic)} artefatos CKO")
    print("==> Índice CKO")
    artifacts.append(build_cko_index_artifact())
    print("==> Manifesto")
    artifacts.append(write_manifest(artifacts))
    print(f"\nOK: {len(artifacts)} artefatos em NIFS/DELIVERY/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
