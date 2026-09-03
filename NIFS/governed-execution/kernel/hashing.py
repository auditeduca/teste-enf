"""Canonical hashing for inputs, outputs, and evidence payloads."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hex(value: Any) -> str:
    payload = value if isinstance(value, (bytes, bytearray)) else canonical_dumps(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_uri(value: Any) -> str:
    return f"sha256:{sha256_hex(value)}"
