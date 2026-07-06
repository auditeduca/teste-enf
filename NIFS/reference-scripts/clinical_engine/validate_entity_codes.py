#!/usr/bin/env python3
"""
Valida entity_code do clinical-engine contra datasets NKOS e master proposal.

Uso:
  python scripts/clinical_engine/validate_entity_codes.py
  python scripts/clinical_engine/validate_entity_codes.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Códigos publicados pelo motor (espelha identifiers/nkosEntityCodes.js)
ENGINE_ID = "DRIP_RATE_CAL_001"
NANDA_CODES = ["NANDA_00046", "NANDA_00031", "NANDA_00033"]
NIC_CODES = ["NIC_2500", "NIC_2510", "NIC_2550"]

SAMPLE_EDGES = [
    {"from": ENGINE_ID, "relation_type": "supports_diagnosis", "to": "NANDA_00046"},
    {"from": ENGINE_ID, "relation_type": "triggers", "to": "NANDA_00031"},
    {"from": "NANDA_00031", "relation_type": "treated_by", "to": "NIC_2500"},
    {"from": "NANDA_00046", "relation_type": "maps_to", "to": "NIC_2550"},
]


def load_json(rel: str) -> dict | list | None:
    path = ROOT / rel
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def normalize_code(code: str | None) -> str | None:
    if not code:
        return None
    return code.replace(".", "_")


def collect_proposal_codes(proposal: dict | None) -> set[str]:
    codes: set[str] = set()
    if not proposal:
        return codes
    for code in (proposal.get("examples") or {}).values():
        if isinstance(code, str):
            codes.add(code)
    for concept in proposal.get("concepts") or []:
        for art in concept.get("artifacts") or []:
            if art.get("entity_code"):
                codes.add(art["entity_code"])
    return codes


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida entity_code NKOS do clinical-engine")
    parser.add_argument("--json", action="store_true", help="Saída JSON para CI")
    args = parser.parse_args()

    diagnoses = load_json("datasets/clinical/nursing_diagnoses.json") or {}
    interventions = load_json("datasets/clinical/nursing_interventions.json") or {}
    proposal = load_json("datasets/metadata/master_code_sequence_proposal.json")

    diag_codes = {
        normalize_code(r.get("diagnosis_code"))
        for r in diagnoses.get("records", [])
        if r.get("diagnosis_code")
    }
    nic_codes = {
        normalize_code(r.get("intervention_code"))
        for r in interventions.get("records", [])
        if r.get("intervention_code")
    }
    proposal_codes = collect_proposal_codes(proposal if isinstance(proposal, dict) else None)

    engine_codes = [ENGINE_ID, *NANDA_CODES, *NIC_CODES]
    results = []
    ok = True

    for code in engine_codes:
        in_clinical = code in diag_codes or code in nic_codes or "CAL_" in code
        in_proposal = code in proposal_codes
        status = "OK" if (in_clinical or in_proposal) else "WARN"
        if status == "WARN":
            ok = False
        results.append(
            {
                "entity_code": code,
                "status": status,
                "in_clinical": in_clinical,
                "in_proposal": in_proposal,
            }
        )

    payload = {
        "ok": ok,
        "engine_codes": results,
        "sample_edges": SAMPLE_EDGES,
        "sources": {
            "nursing_diagnoses": len(diag_codes),
            "nursing_interventions": len(nic_codes),
            "master_proposal": len(proposal_codes),
        },
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("=== Validação entity_code (Python) ===\n")
        for row in results:
            print(
                f"{row['status']} {row['entity_code']} "
                f"clinical={row['in_clinical']} proposal={row['in_proposal']}"
            )
        print("\nArestas demo (relation_type):")
        for edge in SAMPLE_EDGES:
            print(f"  {edge['from']} --[{edge['relation_type']}]--> {edge['to']}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
