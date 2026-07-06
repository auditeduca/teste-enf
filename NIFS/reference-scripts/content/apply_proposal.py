"""Aplica proposta aprovada nos datasets + backup em _archive_temp."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
ARCHIVE_ROOT = ROOT / "datasets" / "_archive_temp"
PENDING_PATH = ROOT / "datasets" / "master-data" / "content-pending" / "pending_items.json"
GENERATED_DIR = ROOT / "datasets" / "master-data" / "content-pending" / "generated"

PROTECTED_PREFIXES = (
    "design/",
    "metadata/design",
    "metadata/schemas",
)


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup_file(rel_path: str) -> str | None:
    src = ROOT / rel_path.replace("/", "\\") if "\\" in rel_path else ROOT / rel_path
    src = ROOT / rel_path
    if not src.exists():
        return None
    dest_dir = ARCHIVE_ROOT / _now_stamp() / Path(rel_path).parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / Path(rel_path).name
    shutil.copy2(src, dest)
    return str(dest.relative_to(ROOT))


def _load_pending_items() -> dict:
    return json.loads(PENDING_PATH.read_text(encoding="utf-8"))


def _save_pending_items(doc: dict) -> None:
    PENDING_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _find_pending(pending_id: str) -> dict | None:
    for item in _load_pending_items().get("items", []):
        if item.get("pending_id") == pending_id:
            return item
    return None


def _update_pending_status(pending_id: str, *, status: str, completion_pct: int) -> None:
    doc = _load_pending_items()
    for item in doc.get("items", []):
        if item.get("pending_id") == pending_id:
            item["status"] = status
            item["completion_pct"] = completion_pct
            item["lifecycle"] = "validated" if status == "applied" else item.get("lifecycle", "draft")
            item["blocker"] = None if status == "applied" else item.get("blocker")
            break
    _save_pending_items(doc)


def _write_generated_artifact(entity_code: str, payload: dict) -> str:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_DIR / f"{entity_code}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT))


def _proposal_back_text(proposal: dict, *, fallback: str = "Gerado por agente") -> str:
    raw = proposal.get("proposed_value")
    if raw is None:
        nested = proposal.get("proposal")
        if isinstance(nested, dict):
            return str(nested.get("summary_pt") or nested.get("rationale_pt") or fallback)
        return fallback
    if isinstance(raw, dict):
        return str(raw.get("summary_pt") or raw.get("rationale_pt") or fallback)
    if isinstance(raw, str):
        text = raw.strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return str(parsed.get("summary_pt") or parsed.get("rationale_pt") or text[:500])
            except json.JSONDecodeError:
                pass
        return text[:500] if text else fallback
    return str(raw)[:500]


def _merge_flashcards(item: dict, proposal: dict) -> dict:
    rel = item.get("target_dataset", "datasets/education/flashcards.json")
    path = ROOT / rel
    backup_file(rel)
    doc = json.loads(path.read_text(encoding="utf-8"))
    records = doc.setdefault("records", [])
    deck_code = f"DECK.{item.get('concept_code', 'UNKNOWN')}"
    stub = {
        "flashcard_code": f"FC.{item.get('concept_code')}.MD001",
        "deck_code": deck_code,
        "entity_code": item.get("entity_code"),
        "linked_entity_code": item.get("parent_entity_code"),
        "front_pt": proposal.get("title_pt") or item.get("title_pt"),
        "back_pt": _proposal_back_text(proposal, fallback=item.get("title_pt") or "Gerado por agente"),
        "content_source": "AGENT_WORKFLOW",
        "status": "review",
        "master_data_workflow": True,
    }
    records.append(stub)
    doc["count"] = len(records)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"dataset": rel, "record_added": stub["flashcard_code"]}


def apply_workflow(workflow: dict) -> dict:
    """Persiste proposta aprovada — backup + merge no dataset alvo."""
    pending_id = workflow.get("pending_id")
    item = _find_pending(pending_id) if pending_id else None
    if not item:
        raise KeyError(f"Item pendente não encontrado: {pending_id}")

    proposal = workflow.get("proposal") or {}
    entity_code = workflow.get("entity_code") or item.get("entity_code")
    artifact_path = _write_generated_artifact(
        entity_code,
        {
            "entity_code": entity_code,
            "artifact_type": workflow.get("artifact_type"),
            "proposal": proposal,
            "review": workflow.get("review"),
            "validation": workflow.get("validation"),
            "applied_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )

    merge_result: dict[str, Any] = {"generated_artifact": artifact_path}
    artifact_type = workflow.get("artifact_type") or item.get("artifact_type")

    if artifact_type == "FLA":
        merge_result.update(_merge_flashcards(item, proposal))
    else:
        rel = item.get("target_dataset")
        if rel:
            merge_result["backup"] = backup_file(rel)
            merge_result["note"] = f"Artefato {artifact_type} salvo em generated/ — merge manual pendente"

    _update_pending_status(pending_id, status="applied", completion_pct=100)
    return merge_result


def archive_legacy_datasets(*, dry_run: bool = False) -> dict:
    """Move datasets legados para _archive_temp (exceto design system)."""
    datasets_dir = ROOT / "datasets"
    moved: list[str] = []
    skipped: list[str] = []
    stamp = ARCHIVE_ROOT / _now_stamp()

    for path in sorted(datasets_dir.rglob("*.json")):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel.startswith("datasets/_archive_temp"):
            continue
        if rel.startswith("datasets/master-data"):
            skipped.append(rel)
            continue
        if any(rel.startswith(f"datasets/{p}") or p in rel for p in PROTECTED_PREFIXES):
            skipped.append(rel)
            continue
        if "design" in rel.lower() and "design-token" in rel.lower():
            skipped.append(rel)
            continue

        dest = stamp / rel
        if dry_run:
            moved.append(rel)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(dest))
        moved.append(rel)

    return {"moved": moved, "skipped_count": len(skipped), "archive_dir": str(stamp.relative_to(ROOT)), "dry_run": dry_run}
