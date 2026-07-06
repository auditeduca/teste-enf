"""Live progress for code review (API status polling)."""
from __future__ import annotations

import threading

_lock = threading.Lock()
_state = {
    "phase": "idle",
    "batch_index": 0,
    "batch_total": 0,
}


def reset_progress() -> None:
    with _lock:
        _state.update({"phase": "idle", "batch_index": 0, "batch_total": 0})


def set_progress(*, phase: str, batch_index: int = 0, batch_total: int = 0) -> None:
    with _lock:
        _state.update({
            "phase": phase,
            "batch_index": batch_index,
            "batch_total": batch_total,
        })


def get_progress() -> dict:
    with _lock:
        return dict(_state)
