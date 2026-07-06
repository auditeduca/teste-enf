"""Métricas da fila editorial — conteúdos pendentes."""
from __future__ import annotations

from collections import Counter


def compute_queue_stats(pending_doc: dict) -> dict:
    items = pending_doc.get("items", [])
    by_status = Counter(item.get("status", "pending") for item in items)
    total = len(items)
    applied = int(by_status.get("applied", 0))
    pending = int(by_status.get("pending", 0) + by_status.get("draft", 0))

    completion_pct = round(applied / total * 100) if total else 0
    if applied >= total and total:
        program_status = "COMPLETE"
    elif applied:
        program_status = "IN_PROGRESS"
    else:
        program_status = "PENDING_QUEUE"

    return {
        "catalog_total": total,
        "pending_count": pending,
        "applied_count": applied,
        "counts_by_status": dict(by_status),
        "overall_completion_pct": completion_pct,
        "program_status": program_status,
    }
