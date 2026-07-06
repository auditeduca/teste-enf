"""Persiste corpus, provisions e tool links."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from config import CORPUS, PROVISIONS, ROOT, TOOL_LINKS

ARCHIVE = ROOT / "datasets" / "_archive_temp"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"schema_version": "2026.2.9", "records": []}


def _save(path: Path, doc: dict) -> None:
    doc["count"] = len(doc.get("records", []))
    doc["generated_at"] = _now()
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _archive(path: Path) -> None:
    if path.is_file():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        rel = path.relative_to(ROOT / "datasets")
        dest = ARCHIVE / stamp / "datasets" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def apply_records(*, corpus: list | None = None, provisions: list | None = None, tool_links: list | None = None) -> dict:
    applied = {"corpus": 0, "provisions": 0, "tool_links": 0}

    if corpus:
        _archive(CORPUS)
        doc = _load(CORPUS)
        records = {r["entity_code"]: r for r in doc.get("records", [])}
        for item in corpus:
            records[item["entity_code"]] = {**item, "updated_at": _now()}
        doc["records"] = list(records.values())
        doc["entity"] = "LegislationCorpus"
        _save(CORPUS, doc)
        applied["corpus"] = len(corpus)

    if provisions:
        _archive(PROVISIONS)
        doc = _load(PROVISIONS)
        records = {r["entity_code"]: r for r in doc.get("records", [])}
        for item in provisions:
            rec = {**item, "updated_at": _now()}
            if "created_at" not in rec:
                rec["created_at"] = _now()
            records[item["entity_code"]] = rec
        doc["records"] = list(records.values())
        doc["entity"] = "LegalProvision"
        doc["code_pattern"] = "{CONCEPT}_PROV_{NNN}"
        _save(PROVISIONS, doc)
        applied["provisions"] = len(provisions)

    if tool_links:
        _archive(TOOL_LINKS)
        doc = _load(TOOL_LINKS)
        records = {r["entity_code"]: r for r in doc.get("records", [])}
        for item in tool_links:
            records[item["entity_code"]] = item
        doc["records"] = list(records.values())
        doc["entity"] = "LegislationToolLink"
        _save(TOOL_LINKS, doc)
        applied["tool_links"] = len(tool_links)

    return applied
