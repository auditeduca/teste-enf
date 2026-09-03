#!/usr/bin/env python3
"""Emit one POLICY_MASTER specialization per classified horizontal layer.

44/44 remain HOLD / NOT_RELEASED. Calculators and scales stay PAUSED.
DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED. Release remains HOLD / NOT_RELEASED.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cko_policy_contract import (
    CASCADE,
    FAIL_CLOSED_ID,
    POLICY_MASTER_ID,
    layer_policy_id,
    specialize,
)

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
CANON = Path(__file__).resolve().parent / "cko_44_layers.json"

OUT_POLICY = GATE / "public" / "policies" / "layer-policies.json"
OUT_SITE = SITE / "data" / "cko" / "layer-policies.json"
OUT_CASCADE = SITE / "data" / "cko" / "cascade" / "layer-policies.json"
LAYER_JSONS = [
    GATE / "public" / "data" / "layers.json",
    SITE / "data" / "cko" / "layers.json",
]

PAUSED = {"LYR-CLIN-CALC-001", "LYR-CLIN-SCALE-001"}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def layer_policy(row: dict) -> dict:
    layer_id = row["id"]
    policy_id = layer_policy_id(layer_id)
    paused = layer_id in PAUSED
    clinical = "PAUSED" if paused else "NOT_ASSERTED"
    modality = "MUST_NOT"
    deny_if = (
        f"{layer_id} clinical_state != PAUSED or action == promote"
        if paused
        else f"{layer_id}.published == true or {layer_id}.release == RELEASED"
    )
    if layer_id == "LYR-PUB-001":
        deny_if = "LYR-PUB-001.published == true or release_allowed == true"
    return {
        "id": policy_id,
        "kind": "policy-as-code",
        "layer_id": layer_id,
        "document_id": layer_id,
        "document_version": "1.0.0",
        "policy_type": "LAYER",
        "name": row["name"],
        "seq": row["seq"],
        "artifact": row["artifact"],
        "sha256": row["sha256"],
        "holds_n": row["holds_n"],
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "starts_at": "policy-as-code",
        "status": "CONTROLLED_LAYER_HOLD",
        "active": False,
        "implantado": False,
        "assured": False,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "published": False,
        "operational": "NOT_ASSERTED",
        "clinical_state": clinical,
        "modality": modality,
        "blocking_inspect": False,
        "blocking_release": True,
        "contract": specialize(
            policy_id=policy_id,
            policy_name=row["name"],
            policy_type="LAYER",
            objective=f"keep_{layer_id}_hold_not_released",
            deny_if=deny_if,
            layers=[layer_id],
            authority=["CKO-MD", "CKO-REG", "ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE"],
            extra_identity={"layer_id": layer_id, "seq": row["seq"]},
        ),
    }


def build() -> dict:
    rows = json.loads(CANON.read_text(encoding="utf-8"))
    if len(rows) != 44:
        raise SystemExit(f"canonical table must have 44 rows, got {len(rows)}")
    layers = [layer_policy(row) for row in rows]
    assert [p["layer_id"] for p in layers] == [r["id"] for r in rows]
    paused_n = sum(1 for p in layers if p["clinical_state"] == "PAUSED")
    return {
        "id": "POL-CKO-LAYER-CATALOG-1.0.0",
        "kind": "policy-as-code",
        "mode": "fail-closed",
        "root": False,
        "starts_at": "policy-as-code",
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "document_id": "CKO-POL-LYR-001",
        "document_version": "1.0.0",
        "status": "CONTROLLED_LAYER_HOLD",
        "frozen": True,
        "active": False,
        "cascade": CASCADE,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "published": False,
        "operational": "NOT_ASSERTED",
        "canonical_promotion": False,
        "documentado": True,
        "implantado": False,
        "assured": False,
        "new_architectural_root": False,
        "layer_count": 44,
        "paused_clinical_n": paused_n,
        "layers": layers,
        "rule": "Cada uma das 44 camadas classificadas especializa POLICY_MASTER_CONTRACT. Binding ≠ implantado. Calculadoras/escalas PAUSED. Nenhuma camada ACTIVE.",
        "evaluation": {
            "verdict": "LAYER_HOLD_NOT_RELEASED",
            "documentado": True,
            "implantado": False,
            "assured": False,
            "active": False,
            "clinical_promotion": "DENIED",
            "findings": [
                {
                    "id": "LYR-F-44-SPECIALIZED",
                    "severity": "HOLD",
                    "text": "44/44 camadas têm policy-as-code. Nenhuma é ACTIVE. LYR-PUB-001 continua a negar publicação.",
                },
                {
                    "id": "LYR-F-CLINICAL-PAUSED",
                    "severity": "HOLD",
                    "text": "LYR-CLIN-CALC-001 e LYR-CLIN-SCALE-001 permanecem PAUSED. Promoção clínica DENIED.",
                },
            ],
        },
    }


def bind_layers_catalog(policy: dict) -> None:
    by_id = {p["layer_id"]: p["id"] for p in policy["layers"]}
    for path in LAYER_JSONS:
        if not path.is_file():
            continue
        catalog = json.loads(path.read_text(encoding="utf-8"))
        catalog["policy"] = policy["id"]
        catalog["specializes"] = POLICY_MASTER_ID
        catalog["policy_status"] = "CONTROLLED_LAYER_HOLD"
        for layer in catalog.get("layers") or []:
            layer["policy_id"] = by_id[layer["id"]]
            layer["specializes"] = POLICY_MASTER_ID
            layer["policy_status"] = "CONTROLLED_LAYER_HOLD"
        write_json(path, catalog)


def generate() -> dict:
    policy = build()
    for dest in (OUT_POLICY, OUT_SITE, OUT_CASCADE):
        write_json(dest, policy)
    bind_layers_catalog(policy)
    return policy


if __name__ == "__main__":
    doc = generate()
    print(f"wrote {OUT_POLICY} layers={doc['layer_count']} status={doc['status']}")
