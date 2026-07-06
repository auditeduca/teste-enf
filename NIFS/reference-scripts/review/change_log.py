"""Append-only audit log for automated code review fixes."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_LOG = Path(__file__).resolve().parents[2] / "datasets" / "metadata" / "code_review_changes.jsonl"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def append_change(
    log_path: Path,
    *,
    rel_path: str,
    summary: str,
    before: str,
    after: str,
    source: str = "deepseek-apply",
    model: str = "",
    run_id: str = "",
    extra: dict[str, Any] | None = None,
) -> dict:
    entry = {
        "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "path": rel_path.replace("\\", "/"),
        "summary": summary,
        "source": source,
        "model": model,
        "run_id": run_id,
        "before_sha256": _sha(before),
        "after_sha256": _sha(after),
        "bytes_before": len(before.encode("utf-8")),
        "bytes_after": len(after.encode("utf-8")),
    }
    if extra:
        entry["extra"] = extra
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_changes(log_path: Path, *, limit: int = 100) -> list[dict]:
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    out: list[dict] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
