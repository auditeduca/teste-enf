"""Validação — entrada DICT vinculada ao DrugReference pai."""
from __future__ import annotations

from dataclasses import dataclass, field


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
    "drug_ref_code",
    "term_pt",
    "definition_pt",
)


def validate_entry(entry: dict) -> ValidationResult:
    res = ValidationResult(ok=True)
    for key in REQUIRED:
        if not (entry.get(key) or "").strip() if isinstance(entry.get(key), str) else entry.get(key) is None:
            res.errors.append(f"Campo obrigatório ausente: {key}")
            res.ok = False

    ec = entry.get("entity_code", "")
    concept = entry.get("concept_code", "")
    parent = entry.get("parent_entity_code", "")
    drug_ref = entry.get("drug_ref_code", "")

    if parent != drug_ref:
        res.errors.append("parent_entity_code deve ser igual a drug_ref_code")
        res.ok = False

    if ec and concept and not ec.startswith(f"{concept}_DICT_"):
        res.warnings.append(f"entity_code {ec} não segue {concept}_DICT_NNN")

    if parent and not str(parent).startswith("DRUG."):
        res.errors.append("parent_entity_code deve ser DRUG.*")
        res.ok = False

    if entry.get("parent_entity_type") != "DrugReference":
        res.errors.append("parent_entity_type deve ser DrugReference")
        res.ok = False

    if len((entry.get("definition_pt") or "")) < 40:
        res.warnings.append("definition_pt curta (<40 chars)")

    if not entry.get("evidence_grade"):
        res.warnings.append("evidence_grade ausente — usar A para Grau A")

    return res
