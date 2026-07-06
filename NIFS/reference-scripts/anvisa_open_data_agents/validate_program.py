"""Validação do programa ANVISA open data."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from config import ANV_DIR, BR_OUT, SCRAPE_SOURCES


@dataclass
class ValidationReport:
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, code: str, msg: str) -> None:
        self.ok = False
        self.errors.append(f"{code}: {msg}")

    def warn(self, code: str, msg: str) -> None:
        self.warnings.append(f"{code}: {msg}")


def run_validation() -> ValidationReport:
    rep = ValidationReport()
    if not (ANV_DIR / "canonical.json").is_file():
        rep.fail("ANV.canonical", "canonical.json ausente")
    if not SCRAPE_SOURCES.is_file():
        rep.fail("ANV.sources", "scrape_sources.json ausente — rode sync_catalog")
    else:
        src = json.loads(SCRAPE_SOURCES.read_text(encoding="utf-8"))
        if not src.get("sources"):
            rep.fail("ANV.sources", "nenhuma fonte catalogada")
        elif src.get("sources_total", 0) < 5:
            rep.warn("ANV.sources", f"poucas fontes ({src.get('sources_total')})")
    meds = BR_OUT / "medications_registry.json"
    if not meds.is_file():
        rep.warn("ANV.medications", "medications_registry.json ainda não gerado")
    else:
        doc = json.loads(meds.read_text(encoding="utf-8"))
        n = len(doc.get("records", []))
        if n < 100:
            rep.warn("ANV.medications", f"apenas {n} medicamentos — rode refresh")
        else:
            rep.ok = rep.ok and True
    fetch = ANV_DIR / "fetch_report.json"
    if fetch.is_file():
        fr = json.loads(fetch.read_text(encoding="utf-8"))
        if fr.get("fetched_ok", 0) == 0:
            rep.fail("ANV.fetch", "último fetch sem sucesso")
    return rep
