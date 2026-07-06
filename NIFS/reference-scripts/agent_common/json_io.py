"""Leitura/escrita JSON segura — evita corrupção por escrita concorrente."""
from __future__ import annotations

import json
from pathlib import Path


def load_json(path: Path, *, default: dict | None = None) -> dict:
    if not path.is_file():
        return default or {}
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(text)
        if isinstance(obj, dict):
            return obj
        raise


def save_json_atomic(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
