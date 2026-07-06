"""Validação — entrada NC vinculada ao LegislationInstrument pai."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from config import JURISDICTIONS, LEGISLATION

VALID_PERIODICITIES = frozenset({"immediate_24h", "weekly", "sentinel"})


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


REQUIRED = (
    "entity_code",
    "concept_code",
    "parent_entity_code",
    "parent_entity_type",
    "jurisdiction_code",
    "condition_name_pt",
    "notification_periodicity",
    "nursing_guidance_pt",
)


def _codes(path: Path, key: str = "entity_code") -> set[str]:
    if not path.is_file():
        return set()
    return {r.get(key) for r in json.loads(path.read_text(encoding="utf-8")).get("records", []) if r.get(key)}


def validate_entry(entry: dict) -> ValidationResult:
    res = ValidationResult(ok=True)
    for key in REQUIRED:
        val = entry.get(key)
        if val is None or (isinstance(val, str) and not val.strip()):
            res.errors.append(f"Campo obrigatório ausente: {key}")
            res.ok = False

    ec = entry.get("entity_code", "")
    concept = entry.get("concept_code", "")
    parent = entry.get("parent_entity_code", "")
    jur = entry.get("jurisdiction_code", "")

    if ec and concept and not ec.startswith(f"{concept}_NC_"):
        res.warnings.append(f"entity_code {ec} não segue {concept}_NC_NNN")

    if entry.get("parent_entity_type") != "LegislationInstrument":
        res.errors.append("parent_entity_type deve ser LegislationInstrument")
        res.ok = False

    leg_codes = _codes(LEGISLATION)
    if parent and leg_codes and parent not in leg_codes:
        res.errors.append(f"parent_entity_code {parent} não existe em legislation_instruments.json")
        res.ok = False

    jur_codes = _codes(JURISDICTIONS)
    if jur and jur_codes and jur not in jur_codes:
        res.errors.append(f"jurisdiction_code {jur} inválido")
        res.ok = False

    per = entry.get("notification_periodicity")
    if per and per not in VALID_PERIODICITIES:
        res.errors.append(f"notification_periodicity inválida: {per}")
        res.ok = False

    if not any(entry.get(k) for k in ("notify_ms", "notify_ses", "notify_sms")):
        res.warnings.append("Nenhuma esfera MS/SES/SMS marcada para notificação")

    if len(entry.get("nursing_guidance_pt") or "") < 40:
        res.warnings.append("nursing_guidance_pt curta (<40 chars)")

    return res
