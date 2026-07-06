"""Aprovação humana — Doc 14 / master_code_sequence_proposal.json."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROPOSAL = ROOT / "datasets" / "metadata" / "master_code_sequence_proposal.json"
APPROVAL = ROOT / "datasets" / "metadata" / "master_code_sequence_approval.json"
DOC14 = ROOT / "docs" / "14-master-data-sequencia-revisao.md"

CHECKLIST: list[dict] = [
    {"id": "code_pattern", "label_pt": "Padrão {CONCEITO}_{ARTEFATO}_{NNN} aprovado"},
    {"id": "scl_cal_prt", "label_pt": "Separação SCL/CAL/PRT + edge layer (sem entidade REL)"},
    {"id": "nine_rights_prt", "label_pt": "9RIGHTS_PRT_001 (protocolo, não CAL) conferido"},
    {"id": "flashcards_fla", "label_pt": "Flashcards *_FLA_001 por escala aprovados"},
    {"id": "slug_mapping", "label_pt": "Mapeamento slug→conceito revisado (ex. gcs→GLASGOW)"},
    {"id": "sitemap_urls", "label_pt": "URLs do sitemap conferidas"},
]

REQUIRED_IDS = [c["id"] for c in CHECKLIST]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_proposal() -> dict:
    return json.loads(PROPOSAL.read_text(encoding="utf-8"))


def get_status() -> dict:
    prop = load_proposal()
    approval = {}
    if APPROVAL.is_file():
        approval = json.loads(APPROVAL.read_text(encoding="utf-8"))
    counts = prop.get("counts", {})
    return {
        "schema_version": prop.get("schema_version"),
        "status": prop.get("status", "PENDING_REVIEW"),
        "is_approved": prop.get("status") == "APPROVED",
        "can_migrate": prop.get("status") == "APPROVED",
        "counts": counts,
        "checklist": CHECKLIST,
        "approval": approval.get("record") if approval else None,
        "review_instructions": prop.get("review_instructions"),
        "examples": prop.get("examples", {}),
        "proposal_path": str(PROPOSAL.relative_to(ROOT)),
        "doc_path": str(DOC14.relative_to(ROOT)),
    }


def is_approved() -> bool:
    return load_proposal().get("status") == "APPROVED"


def approve(*, approver: str, checklist: dict[str, bool], notes: str = "") -> dict:
    approver = (approver or "").strip()
    if not approver:
        raise ValueError("Nome do aprovador é obrigatório")

    missing = [cid for cid in REQUIRED_IDS if not checklist.get(cid)]
    if missing:
        raise ValueError(f"Checklist incompleto — faltam: {', '.join(missing)}")

    prop = load_proposal()
    if prop.get("status") == "APPROVED":
        return get_status()

    now = _now()
    record = {
        "approver": approver,
        "approved_at": now,
        "checklist": {cid: True for cid in REQUIRED_IDS},
        "notes": notes or None,
        "schema_version": prop.get("schema_version"),
        "total_codes": prop.get("counts", {}).get("total_codes"),
    }

    prop["status"] = "APPROVED"
    prop["approved_at"] = now
    prop["approved_by"] = approver
    prop["approval_checklist"] = record["checklist"]
    if notes:
        prop["approval_notes"] = notes

    PROPOSAL.write_text(json.dumps(prop, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    approval_doc = {
        "schema_version": "2026.2.8-code-sequence-approval",
        "record": record,
        "history": [],
    }
    if APPROVAL.is_file():
        prev = json.loads(APPROVAL.read_text(encoding="utf-8"))
        if prev.get("record"):
            approval_doc["history"] = prev.get("history", []) + [prev["record"]]
    approval_doc["record"] = record
    APPROVAL.write_text(json.dumps(approval_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    _sync_doc14_status("APPROVED", approver, now)

    return get_status()


def reject(*, approver: str, reason: str) -> dict:
    approver = (approver or "").strip()
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("Motivo da rejeição é obrigatório")

    prop = load_proposal()
    prop["status"] = "PENDING_REVIEW"
    prop.pop("approved_at", None)
    prop.pop("approved_by", None)
    prop["last_rejection"] = {"by": approver or "unknown", "at": _now(), "reason": reason}
    PROPOSAL.write_text(json.dumps(prop, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    _sync_doc14_status("PENDING_REVIEW")

    return get_status()


def _sync_doc14_status(status: str, approver: str | None = None, when: str | None = None) -> None:
    if not DOC14.is_file():
        return
    text = DOC14.read_text(encoding="utf-8")
    if status == "APPROVED" and approver and when:
        date = when[:10]
        text = re.sub(
            r"> \*\*Status: `PENDING_REVIEW`\*\*.*",
            f"> **Status: `APPROVED`** — aprovado por **{approver}** em {date}.",
            text,
            count=1,
        )
        text = text.replace(
            "- [ ] Padrão `{CONCEITO}_{ARTEFATO}_{NNN}` aprovado",
            "- [x] Padrão `{CONCEITO}_{ARTEFATO}_{NNN}` aprovado",
        )
        for cid in REQUIRED_IDS:
            pass  # checklist in doc is static; approval record is source of truth
        text = re.sub(
            r"- \[ \] Aprovador: _+ Data: _+",
            f"- [x] Aprovador: {approver} Data: {date}",
            text,
        )
    else:
        text = re.sub(
            r"> \*\*Status: `APPROVED`\*\*[^\n]*",
            "> **Status: `PENDING_REVIEW`** — aguardando aprovação antes de migrar datasets ou UI.",
            text,
            count=1,
        )
    DOC14.write_text(text, encoding="utf-8")
