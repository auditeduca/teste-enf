#!/usr/bin/env python3
"""Emit the extraction policy-as-code catalog.

Extraction existed as zip/readback code, not as a POLICY_MASTER specialization.
This catalog binds those streams. None are ACTIVE or assured.
DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED. Release remains HOLD / NOT_RELEASED.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cko_policy_contract import CASCADE, FAIL_CLOSED_ID, POLICY_MASTER_ID, specialize

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
MD_REG = GATE / "public" / "policies" / "md-reg-frontend.json"

OUT_POLICY = GATE / "public" / "policies" / "extraction.json"
OUT_SITE = SITE / "data" / "cko" / "extraction.json"
OUT_CASCADE = SITE / "data" / "cko" / "cascade" / "extraction.json"
OUT_MD_REG_SITE = SITE / "data" / "cko" / "md-reg-frontend.json"

STREAMS = [
    {
        "stream_id": "EXT-LAYER-ZIP",
        "policy_id": "POL-CKO-EXT-LAYER-ZIP-1.0.0",
        "name": "Extração dos 44 pacotes ZIP das camadas",
        "kind": "LAYER_PACKAGE",
        "progress": "generate_layers.py verifica SHA-256 e extrai package.zip; extracted_n é evidência de ficheiro, não de política ACTIVE",
        "deny_if": "layer.zip_verified != true or layer_count != 44",
        "layers": ["CKO-MD", "LYR-PUB-001"],
        "authority": ["ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE", "DO_NOT_ALTER_DRIVE_FILE"],
        "count": 44,
    },
    {
        "stream_id": "EXT-PDF-PACK",
        "policy_id": "POL-CKO-EXT-PDF-PACK-1.0.0",
        "name": "Inventário dos pacotes PDF do fecho técnico",
        "kind": "PDF_INVENTORY",
        "progress": "44 artefactos classificados no snapshot; extração ≠ promoção canónica",
        "deny_if": "canonical_promotion == true",
        "layers": ["LYR-EXPORT-001", "LYR-DOC-TPL-001"],
        "authority": ["CKO-REG", "ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE"],
        "count": 44,
    },
    {
        "stream_id": "EXT-DRIVE-SNAPSHOT",
        "policy_id": "POL-CKO-EXT-DRIVE-SNAPSHOT-1.0.0",
        "name": "Leitura do snapshot Drive imutável",
        "kind": "DRIVE_READBACK",
        "progress": "ALL-SHA256-MANIFEST-20260902 e regra DO_NOT_ALTER_DRIVE_FILE; extrair ≠ alterar Drive",
        "deny_if": "mutate_drive == true",
        "layers": ["CKO-MD", "CKO-REG"],
        "authority": ["CKO-DRIVE-IMMUTABLE-1.0.0", "DO_NOT_ALTER_DRIVE_FILE"],
        "count": 449,
    },
    {
        "stream_id": "EXT-REG-CORPUS",
        "policy_id": "POL-CKO-EXT-REG-CORPUS-1.0.0",
        "name": "Extração do corpus normativo (H03)",
        "kind": "REGULATORY_CORPUS",
        "progress": "H03: nenhum denominador de extração do corpus normativo criado nesta vaga",
        "deny_if": "regulatory_corpus.extracted == true without authorized denominator",
        "layers": ["CKO-REG"],
        "authority": ["CKO-REG", "H03"],
        "count": 0,
    },
    {
        "stream_id": "EXT-ABNT-CLAUSE",
        "policy_id": "POL-CKO-EXT-ABNT-CLAUSE-1.0.0",
        "name": "Extração clause-level ABNT 6023/10520/5891",
        "kind": "ABNT_CLAUSE",
        "progress": "NBR 6023:2025 cutover registado; clause-level permanece HOLD até exemplar autorizado",
        "deny_if": "abnt.clause_level == PASS without authorized exemplar",
        "layers": ["LYR-REF-001", "CKO-REG"],
        "authority": ["ABNT NBR 6023:2025", "CKO-POL-UT-001"],
        "count": 3,
    },
    {
        "stream_id": "EXT-MD-FIELDS",
        "policy_id": "POL-CKO-EXT-MD-FIELDS-1.0.0",
        "name": "Classificação dos 2496 campos CKO-MD",
        "kind": "MASTER_DATA",
        "progress": "2496 campos classificados e congelados; bindings de campo não materializados",
        "deny_if": "materialized_field_bindings == true",
        "layers": ["CKO-MD"],
        "authority": ["CKO-MD", "ART-CKO-MASTER-DATA-FINAL-CONTROLLED"],
        "count": 2496,
    },
    {
        "stream_id": "EXT-REG-BINDINGS",
        "policy_id": "POL-CKO-EXT-REG-BINDINGS-1.0.0",
        "name": "Classificação das 10913 amarrações CKO-REG",
        "kind": "REGULATORY_BINDINGS",
        "progress": "10913 amarrações classificadas; não materializadas no runtime",
        "deny_if": "materialized_field_bindings == true",
        "layers": ["CKO-REG"],
        "authority": ["CKO-REG", "ART-CKO-REGULATORY-FINAL-CONTROLLED"],
        "count": 10913,
    },
    {
        "stream_id": "EXT-LOCALE",
        "policy_id": "POL-CKO-EXT-LOCALE-1.0.0",
        "name": "Extração das 360 células de locale Wave2",
        "kind": "LOCALE_CELLS",
        "progress": "360 células no ledger; seletor desativado; HOLD-HUMAN-LOCALE-ACTIVATE",
        "deny_if": "activate_in_selector == true",
        "layers": ["LYR-I18N-001"],
        "authority": ["CKO-REG", "HOLD-HUMAN-LOCALE-ACTIVATE"],
        "count": 360,
    },
]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stream_policy(row: dict) -> dict:
    return {
        "id": row["policy_id"],
        "kind": "policy-as-code",
        "stream_id": row["stream_id"],
        "document_id": row["stream_id"],
        "document_version": "1.0.0",
        "policy_type": "EXTRACTION",
        "extraction_kind": row["kind"],
        "name": row["name"],
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "starts_at": "policy-as-code",
        "status": "CONTROLLED_EXTRACTION_HOLD",
        "active": False,
        "implantado": False,
        "assured": False,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "published": False,
        "operational": "NOT_ASSERTED",
        "modality": "MUST_NOT",
        "count": row["count"],
        "progress": row["progress"],
        "blocking_inspect": False,
        "blocking_release": True,
        "contract": specialize(
            policy_id=row["policy_id"],
            policy_name=row["name"],
            policy_type="EXTRACTION",
            objective=f"keep_{row['stream_id']}_extraction_hold",
            deny_if=row["deny_if"],
            layers=row["layers"],
            authority=row["authority"],
            extra_identity={"stream_id": row["stream_id"], "extraction_kind": row["kind"]},
        ),
    }


def bind_md_reg() -> dict:
    policy = json.loads(MD_REG.read_text(encoding="utf-8"))
    policy["parent"] = POLICY_MASTER_ID
    policy["specializes"] = POLICY_MASTER_ID
    policy["inherits"] = [FAIL_CLOSED_ID, POLICY_MASTER_ID]
    policy["starts_at"] = "policy-as-code"
    policy["active"] = False
    policy["implantado"] = False
    policy["assured"] = False
    policy["documentado"] = True
    policy["contract"] = specialize(
        policy_id=policy["id"],
        policy_name="MD/REG através do frontend",
        policy_type="FRONTEND",
        objective="keep_md_reg_executable_through_frontend_without_release",
        deny_if="release_allowed == true or human_decisions.blocking_inspect == true",
        layers=["CKO-MD", "CKO-REG"],
        authority=["CKO-MD", "CKO-REG", "NIFS-900-03", "NIFS-600-15"],
        extra_identity={"document_id": "CKO-MD-REG", "chain_id": policy.get("chain_id")},
    )
    policy["contract"]["fields"]["IDENTITY"]["policy_status"] = "HOLD / NOT_RELEASED"
    write_json(MD_REG, policy)
    write_json(OUT_MD_REG_SITE, policy)
    return policy


def build() -> dict:
    streams = [stream_policy(row) for row in STREAMS]
    assert len(streams) == 8
    return {
        "id": "POL-CKO-EXTRACTION-1.0.0",
        "kind": "policy-as-code",
        "mode": "fail-closed",
        "root": False,
        "starts_at": "policy-as-code",
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "document_id": "CKO-POL-EXTRACT-001",
        "document_version": "1.0.0",
        "status": "CONTROLLED_EXTRACTION_HOLD",
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
        "stream_count": 8,
        "streams": streams,
        "rule": "Extração = policy-as-code. ZIP/readback/classificação DOCUMENTADO não é corpus normativo extraído, nem clause-level ABNT, nem ACTIVE.",
        "evaluation": {
            "verdict": "EXTRACTION_HOLD_NOT_IMPLEMENTED",
            "documentado": True,
            "implantado": False,
            "assured": False,
            "active": False,
            "findings": [
                {
                    "id": "EXT-F-NO-PRIOR-POLICY",
                    "severity": "HOLD",
                    "text": "Antes deste catálogo a extração era só código (zip/SHA). Não havia POL-CKO-EXTRACTION.",
                },
                {
                    "id": "EXT-F-H03-NO-DENOMINATOR",
                    "severity": "HOLD",
                    "text": "H03 permanece sem denominador de corpus normativo. ABNT clause-level HOLD.",
                },
                {
                    "id": "EXT-F-NOT-MATERIALIZED",
                    "severity": "HOLD",
                    "text": "2496 campos e 10913 amarrações classificados ≠ bindings materializados.",
                },
            ],
        },
    }


def generate() -> dict:
    bind_md_reg()
    policy = build()
    for dest in (OUT_POLICY, OUT_SITE, OUT_CASCADE):
        write_json(dest, policy)
    return policy


if __name__ == "__main__":
    doc = generate()
    print(f"wrote {OUT_POLICY} streams={doc['stream_count']} status={doc['status']}")
