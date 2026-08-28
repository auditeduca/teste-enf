#!/usr/bin/env python3
"""Validação mínima de CKO v3 (Fase 1.3)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CKO = ROOT / "NIFS" / "DELIVERY" / "js" / "modules" / "data" / "cko" / "CKO-APGAR-001.json"


def main() -> int:
    if not CKO.is_file():
        print(f"ERRO: {CKO} ausente", file=sys.stderr)
        return 1
    data = json.loads(CKO.read_text(encoding="utf-8"))
    errors: list[str] = []

    if not data.get("cko_id"):
        errors.append("cko_id ausente")
    meta = data.get("metadata") or {}
    if not meta.get("version"):
        errors.append("metadata.version ausente")

    term = data.get("terminology") or {}
    for kind in ("nanda", "nic", "noc"):
        for item in term.get(kind, []):
            if not item.get("code"):
                errors.append(f"terminology.{kind}: entrada sem code")
            if item.get("label"):
                errors.append(f"terminology.{kind}: label inline proibido (usar bundle global)")

    np = data.get("nursing_process") or {}
    for field in ("diagnosis_codes", "intervention_codes", "outcome_codes"):
        if field not in np:
            errors.append(f"nursing_process.{field} ausente")

    for e in errors:
        print(f"  ERRO: {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK: {CKO.name} v{meta.get('version')} — referências por código")
    return 0


if __name__ == "__main__":
    sys.exit(main())
