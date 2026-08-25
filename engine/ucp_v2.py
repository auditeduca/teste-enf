"""COMPARE CKO UCP v2.0 attachments. Not a promotion into schemas/.

Owner dropped Draft 2020-12 contracts + two registers. Constitution:
RECOVER → COMPARE → GAP ONLY. CONTROLLED_CANDIDATE ≠ IMPLEMENTED ≠ ASSURED.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT

INBOX = ROOT / "cko_inbox" / "ucp_v2"
CATALOG_PATH = ROOT / "cko_md" / "ucp_v2_compare.json"
SCHEMA_DIR = ROOT / "schemas"
REGISTER_NAME = "artifact-register.csv"
CAPABILITY_NAME = "capability-acceleration.csv"
POLICY = "POL-CKO-UCP-001-v2.0"
BUSINESS_KEY = "MD-UCP-V2-COMPARE-001"

EXPECTED_SCHEMAS = (
    "agent-contract.schema.json",
    "content-atom.schema.json",
    "content-object.schema.json",
    "engine-contract.schema.json",
    "knowledge-object.schema.json",
    "library-object.schema.json",
    "publishing-contract.schema.json",
    "render-contract.schema.json",
    "render-instance.schema.json",
    "studio-contract.schema.json",
    "validator-contract.schema.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _read_csv(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    rows = []
    with io.StringIO(text, newline="") as handle:
        for row in csv.DictReader(handle):
            cleaned = {}
            for key, value in row.items():
                name = (key or "").replace("\ufeff", "").strip()
                cleaned[name] = value.strip() if isinstance(value, str) else value
            rows.append(cleaned)
    return rows


def compare_ucp_v2() -> dict:
    """AG-UCP-V2-COMPARE — hash attachments, gap vs schemas/, do not promote."""
    schema_files = []
    for name in EXPECTED_SCHEMAS:
        path = INBOX / name
        rec = {
            "file": name,
            "present": path.is_file(),
            "bytes": path.stat().st_size if path.is_file() else None,
            "sha256": _sha256(path) if path.is_file() else None,
            "draft": None,
            "schema_id": None,
            "title": None,
            "policy": None,
            "copied_into_schemas": False,
        }
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            rec["draft"] = payload.get("$schema")
            rec["schema_id"] = payload.get("$id")
            rec["title"] = payload.get("title")
            rec["policy"] = payload.get("x-cko-policy")
            rec["authority_chain"] = payload.get("x-cko-authority-chain")
            rec["pack_sha256_declared"] = payload.get("x-source-attachment-sha256")
        schema_files.append(rec)

    existing = []
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        existing.append({
            "file": path.name,
            "draft": payload.get("$schema"),
            "schema_id": payload.get("$id"),
            "title": payload.get("title"),
        })

    register_path = INBOX / REGISTER_NAME
    capability_path = INBOX / CAPABILITY_NAME
    register_rows = _read_csv(register_path) if register_path.is_file() else []
    capability_rows = _read_csv(capability_path) if capability_path.is_file() else []
    present_names = {path.name for path in INBOX.iterdir() if path.is_file()}
    missing_register = []
    for row in register_rows:
        filename = (row.get("file") or "").strip()
        if filename and filename not in present_names:
            missing_register.append({
                "artifact_id": row.get("artifact_id"),
                "artifact_class": row.get("artifact_class"),
                "file": filename,
                "status": row.get("status") or "CONTROLLED_CANDIDATE",
            })

    ucp_ids = {item.get("schema_id") for item in schema_files if item.get("schema_id")}
    existing_ids = {item.get("schema_id") for item in existing if item.get("schema_id")}
    engine_contract = next((item for item in schema_files if item["file"] == "engine-contract.schema.json"), {})
    engine_payload = {}
    engine_path = INBOX / "engine-contract.schema.json"
    if engine_path.is_file():
        engine_payload = json.loads(engine_path.read_text(encoding="utf-8"))
    authority_mode = ((engine_payload.get("properties") or {}).get("authority_mode") or {}).get("const")

    gaps = [
        {
            "id": "GAP-UCP-DRAFT",
            "status": "COMPARE_ONLY",
            "reason": "UCP v2 usa JSON Schema 2020-12; schemas/ vigentes no GitHub são draft-07.",
        },
        {
            "id": "GAP-UCP-ID-OVERLAP",
            "status": "OBSERVED",
            "reason": "Nenhum $id UCP coincide com schemas/ atuais (tool.schema.json não tem $id).",
            "ucp_ids": sorted(ucp_ids),
            "existing_ids": sorted(x for x in existing_ids if x),
        },
        {
            "id": "GAP-UCP-MODELS-MISSING",
            "status": "EVIDENCE_PENDING",
            "reason": "O registo lista modelos/piloto que não vieram neste lote.",
            "missing_count": len(missing_register),
        },
        {
            "id": "GAP-UCP-NOT-PROMOTED",
            "status": "HOLD",
            "reason": "CONTROLLED_CANDIDATE. Não copiar para schemas/. Não substituir tool.schema.json. Não ASSURED.",
        },
        {
            "id": "GAP-UCP-UUID",
            "status": "HOLD",
            "reason": "tool.schema.json vigente descreve UUID v4; constituição mantém UUIDv7 HOLD e uuid=null.",
        },
    ]

    catalog = {
        "business_key": BUSINESS_KEY,
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "implemented": False,
        "publication": "HOLD",
        "assured": False,
        "promotes_to_md": False,
        "copied_into_schemas": False,
        "policy": POLICY,
        "layer": "L10",
        "frente": "F23",
        "method": "RECOVER → COMPARE → GAP ONLY",
        "inbox": "cko_inbox/ucp_v2",
        "schema_count": sum(1 for item in schema_files if item["present"]),
        "register_artifact_count": len(register_rows),
        "capability_count": len(capability_rows),
        "missing_register_count": len(missing_register),
        "existing_schema_count": len(existing),
        "draft_ucp": "https://json-schema.org/draft/2020-12/schema",
        "draft_existing": "http://json-schema.org/draft-07/schema#",
        "engine_authority_mode": authority_mode,
        "engine_authority_aligned": authority_mode == "DERIVED_NOT_AUTHORITY",
        "registers": {
            "artifact_register": {
                "file": REGISTER_NAME,
                "present": register_path.is_file(),
                "sha256": _sha256(register_path) if register_path.is_file() else None,
            },
            "capability_acceleration": {
                "file": CAPABILITY_NAME,
                "present": capability_path.is_file(),
                "sha256": _sha256(capability_path) if capability_path.is_file() else None,
            },
        },
        "schemas": schema_files,
        "existing_schemas": existing,
        "missing_from_register": missing_register,
        "capabilities": [
            {
                "capability_id": row.get("capability_id"),
                "capability_name": row.get("capability_name"),
                "control_plane_status": row.get("control_plane_status"),
                "runtime_status": "NOT_IMPLEMENTED",
            }
            for row in capability_rows
        ],
        "gaps": gaps,
        "do_not": [
            "Copiar estes JSON para schemas/ neste ciclo.",
            "Tratar CONTROLLED_CANDIDATE / CONTROL_PLANE_V2_DEFINED como ASSURED ou PUBLICADO.",
            "Substituir schemas/tool.schema.json dos cinco pilotos.",
            "Inventar os 10 artefatos MODEL/PILOT ausentes.",
        ],
        "evaluated_at": _now(),
    }
    _dump(CATALOG_PATH, catalog)
    return {
        "agent_id": "AG-UCP-V2-COMPARE",
        "class": "MONITORING",
        "role": "CHECKER",
        "status": "COMPARE_ONLY",
        "promotes_to_md": False,
        "copied_into_schemas": False,
        "publication": "HOLD",
        "assured": False,
        "writes_to": "cko_md/ucp_v2_compare.json",
        "schema_count": catalog["schema_count"],
        "missing_register_count": catalog["missing_register_count"],
        "business_key": BUSINESS_KEY,
    }
