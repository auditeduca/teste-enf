"""Minimal HTML helpers (no third-party templating)."""

from __future__ import annotations

import html
import json
from typing import Any


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def attr(value: Any) -> str:
    return esc(value)


def dumps_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
