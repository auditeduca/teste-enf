"""Validação — vínculos pai doc 14."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from config import CORPUS, DOMAINS, INSTRUMENTS, PROVISIONS, TOOL_LINKS


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _codes(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return {r.get("entity_code") for r in json.loads(path.read_text(encoding="utf-8")).get("records", []) if r.get("entity_code")}


VALID_PARENT_TYPES = frozenset({
    "LegislationInstrument",
    "LegislationDomain",
    "LegalProvision",
    "LegislationCorpus",
    "Jurisdiction",
})


def validate_provision(entry: dict, *, leg_codes: set[str], domain_codes: set[str]) -> ValidationResult:
    res = ValidationResult(ok=True)
    for key in ("entity_code", "concept_code", "parent_entity_code", "parent_entity_type", "text_pt"):
        if not entry.get(key):
            res.errors.append(f"{entry.get('entity_code')}: ausente {key}")
            res.ok = False
    parent = entry.get("parent_entity_code")
    if parent and leg_codes and parent not in leg_codes:
        res.errors.append(f"{entry.get('entity_code')}: parent {parent} não encontrado em instruments")
        res.ok = False
    dom = entry.get("domain_code")
    if dom and domain_codes and dom not in domain_codes:
        res.warnings.append(f"{entry.get('entity_code')}: domain {dom} não catalogado")
    return res


def validate_tool_link(entry: dict, *, prov_codes: set[str], corpus_codes: set[str]) -> ValidationResult:
    res = ValidationResult(ok=True)
    parent = entry.get("parent_entity_code")
    ptype = entry.get("parent_entity_type")
    if ptype == "LegalProvision" and parent not in prov_codes:
        res.errors.append(f"{entry.get('entity_code')}: parent provision {parent} inexistente")
        res.ok = False
    if ptype == "LegislationCorpus" and parent not in corpus_codes:
        res.errors.append(f"{entry.get('entity_code')}: parent corpus {parent} inexistente")
        res.ok = False
    if not entry.get("tool_code"):
        res.errors.append(f"{entry.get('entity_code')}: tool_code ausente")
        res.ok = False
    return res


def run_validation() -> ValidationResult:
    rep = ValidationResult(ok=True)
    leg = _codes(INSTRUMENTS)
    dom = _codes(DOMAINS)
    prov_codes = _codes(PROVISIONS)
    corpus_codes = _codes(CORPUS)

    for rec in json.loads(PROVISIONS.read_text(encoding="utf-8")).get("records", []) if PROVISIONS.is_file() else []:
        v = validate_provision(rec, leg_codes=leg, domain_codes=dom)
        rep.errors.extend(v.errors)
        rep.warnings.extend(v.warnings)
        if not v.ok:
            rep.ok = False

    for rec in json.loads(TOOL_LINKS.read_text(encoding="utf-8")).get("records", []) if TOOL_LINKS.is_file() else []:
        v = validate_tool_link(rec, prov_codes=prov_codes, corpus_codes=corpus_codes)
        rep.errors.extend(v.errors)
        if not v.ok:
            rep.ok = False

    return rep
