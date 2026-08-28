#!/usr/bin/env python3
"""Verifica que artefatos gerados têm _generated.do_not_edit e batem com manifest."""
from __future__ import annotations

import sys

from compiler.io import file_sha256, load_json
from compiler.paths import DELIVERY, MANIFEST

REQUIRED_GENERATED = [
    DELIVERY / "js/bundles/clinical-terminology.pt-BR.json",
    DELIVERY / "js/bundles/tools-catalog.json",
    DELIVERY / "js/modules/data/apgar-cko.json",
    DELIVERY / "js/modules/data/apgar-edges.json",
    DELIVERY / "build-manifest.json",
]


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_GENERATED:
        if not path.is_file():
            errors.append(f"ausente: {path.relative_to(DELIVERY)}")
            continue
        data = load_json(path)
        gen = data.get("_generated") or {}
        if not gen.get("do_not_edit"):
            errors.append(f"sem _generated.do_not_edit: {path.relative_to(DELIVERY)}")

    if MANIFEST.is_file():
        manifest = load_json(MANIFEST)
        for rel, meta in manifest.get("artifacts", {}).items():
            path = DELIVERY / rel
            if not path.is_file():
                errors.append(f"manifest referencia arquivo ausente: {rel}")
                continue
            if meta.get("sha256") != file_sha256(path):
                errors.append(f"hash divergente (regenerar): {rel}")

    for e in errors:
        print(f"  ERRO: {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK: {len(REQUIRED_GENERATED)} artefatos gerados verificados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
