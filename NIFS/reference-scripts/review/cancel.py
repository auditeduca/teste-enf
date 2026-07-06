"""Cancel flag for long-running code review (checked between API batches)."""
from __future__ import annotations

import threading

_lock = threading.Lock()
_cancelled = False


def reset_cancel() -> None:
    global _cancelled
    with _lock:
        _cancelled = False


def request_cancel() -> None:
    global _cancelled
    with _lock:
        _cancelled = True


def is_cancelled() -> bool:
    with _lock:
        return _cancelled
