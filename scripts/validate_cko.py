#!/usr/bin/env python3
"""Validação mínima de CKO v3 (Fase 1.3 + Fase 4 Glasgow)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CKO_DIR = ROOT / "NIFS" / "DELIVERY" / "js" / "modules" / "data" / "cko"
CKO_FILES = [
    CKO_DIR / "CKO-APGAR-001.json",
    CKO_DIR / "CKO-GCS-001.json",
]


def validate_file(cko_path: Path) -> list[str]:
    errors: list[str] = []
    if not cko_path.is_file():
        return [f"{cko_path.name} ausente"]
    data = json.loads(cko_path.read_text(encoding="utf-8"))
    if not data.get("cko_id"):
        errors.append(f"{cko_path.name}: cko_id ausente")
    meta = data.get("metadata") or {}
    if not meta.get("version"):
        errors.append(f"{cko_path.name}: metadata.version ausente")

    term = data.get("terminology") or {}
    for kind in ("nanda", "nic", "noc"):
        for item in term.get(kind, []):
            if not item.get("code"):
                errors.append(f"{cko_path.name}: terminology.{kind} sem code")
            if item.get("label"):
                errors.append(f"{cko_path.name}: terminology.{kind} label inline proibido")

    np = data.get("nursing_process") or {}
    for field in ("diagnosis_codes", "intervention_codes", "outcome_codes"):
        if field not in np:
            errors.append(f"{cko_path.name}: nursing_process.{field} ausente")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in CKO_FILES:
        errors.extend(validate_file(path))

    for e in errors:
        print(f"  ERRO: {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK: {len(CKO_FILES)} CKO v3 — referências por código")
    return 0


if __name__ == "__main__":
    sys.exit(main())
