"""Validação global do programa NC."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from config import JURISDICTIONS, LEGISLATION, OUTPUT
from validators import validate_entry


@dataclass
class Report:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def run_validation() -> Report:
    rep = Report(ok=True)
    for path, label in ((JURISDICTIONS, "jurisdictions"), (LEGISLATION, "legislation"), (OUTPUT, "conditions")):
        if not path.is_file():
            rep.errors.append(f"Dataset ausente: {label}")
            rep.ok = False
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not doc.get("records"):
            rep.warnings.append(f"{label}: sem registros")

    if OUTPUT.is_file():
        for rec in json.loads(OUTPUT.read_text(encoding="utf-8")).get("records", []):
            v = validate_entry(rec)
            if not v.ok:
                rep.errors.extend(f"{rec.get('entity_code')}: {e}" for e in v.errors)
                rep.ok = False
    return rep
