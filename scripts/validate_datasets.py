#!/usr/bin/env python3
"""Valida integridade de NIFS/reference-datasets/ (Fase 1.1)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "NIFS" / "reference-datasets"
REGISTRY = DATASETS / "metadata" / "canonical_registry.json"

# Arquivos com envelope alternativo (sem records[])
ALT_ENVELOPE = {
    DATASETS / "metadata" / "ai_prompt_templates.json": {"version_key": "version"},
    DATASETS / "clinical" / "drug_monographs.json": {"optional_schema": True},
}

CLINICAL_CODE_FIELDS = {
    "NursingDiagnosis": ("nanda_code", "name_pt", "name"),
    "NursingIntervention": ("nic_code", "name_pt", "name"),
    "NursingOutcome": ("noc_code", "name_pt", "name"),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_registry(data: dict, errors: list[str], warnings: list[str]) -> None:
    if not REGISTRY.is_file():
        warnings.append("canonical_registry.json ausente — pulando cruzamento")
        return
    reg = load_json(REGISTRY)
    missing = 0
    for ent in reg.get("entities", []):
        rel = ent.get("file")
        if not rel:
            continue
        path = DATASETS / rel
        if not path.is_file():
            missing += 1
            continue
        payload = load_json(path)
        records = payload.get("records")
        if records is None:
            continue
        expected = ent.get("records")
        if expected is not None and len(records) != expected:
            warnings.append(
                f"{rel}: count registry={expected} real={len(records)} ({ent.get('entity')})"
            )
    if missing:
        warnings.append(
            f"registry: {missing} entidade(s) referenciada(s) sem arquivo no disco (roadmap NIFS)"
        )


def check_clinical_record(entity: str, rec: dict, path: str, idx: int, warnings: list[str]) -> None:
    spec = CLINICAL_CODE_FIELDS.get(entity)
    if not spec:
        return
    code_key, pt_key, en_key = spec
    if not rec.get(code_key):
        warnings.append(f"{path} records[{idx}]: sem {code_key}")
    if not rec.get("localized_labels"):
        if not rec.get(pt_key) and not rec.get(en_key):
            warnings.append(f"{path} records[{idx}]: sem localized_labels nem name/name_pt")


def validate_file(path: Path, errors: list[str], warnings: list[str]) -> None:
    rel = path.relative_to(DATASETS)
    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: JSON inválido — {exc}")
        return

    alt = ALT_ENVELOPE.get(path)
    if alt and alt.get("optional_schema"):
        if "schema_version" not in data and "entity" in data:
            warnings.append(f"{rel}: sem schema_version (envelope clínico legado)")
        return

    if alt and "version_key" in alt:
        if "schema_version" not in data and alt["version_key"] not in data:
            errors.append(f"{rel}: falta schema_version ou {alt['version_key']}")
        return

    if "records" not in data:
        if path.name.endswith(".json"):
            warnings.append(f"{rel}: sem array records (envelope não padrão)")
        return

    if "schema_version" not in data:
        errors.append(f"{rel}: falta schema_version")

    entity = data.get("entity", "")
    for i, rec in enumerate(data.get("records", [])):
        check_clinical_record(entity, rec, str(rel), i, warnings)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not DATASETS.is_dir():
        print("ERRO: pasta reference-datasets não encontrada", file=sys.stderr)
        return 1

    files = sorted(DATASETS.rglob("*.json"))
    files = [p for p in files if "schemas" not in p.parts]

    for path in files:
        validate_file(path, errors, warnings)

    if REGISTRY.is_file():
        try:
            check_registry(load_json(REGISTRY), errors, warnings)
        except json.JSONDecodeError as exc:
            errors.append(f"canonical_registry.json: JSON inválido — {exc}")

    print(f"Arquivos verificados: {len(files)}")
    for w in warnings:
        print(f"  AVISO: {w}")
    for e in errors:
        print(f"  ERRO: {e}", file=sys.stderr)

    if errors:
        print(f"\nFalhou: {len(errors)} erro(s), {len(warnings)} aviso(s)", file=sys.stderr)
        return 1

    print(f"\nOK: {len(files)} datasets, {len(warnings)} aviso(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
