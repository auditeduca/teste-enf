from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENERATED_MARKER = {
    "by": "compiler/build_all.py",
    "do_not_edit": True,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_generated_json(
    path: Path,
    payload: dict,
    *,
    sources: list[str],
    artifact_key: str | None = None,
) -> dict:
    """Escreve JSON com metadados _generated e retorna entrada de manifesto."""
    path.parent.mkdir(parents=True, exist_ok=True)
    out = dict(payload)
    out["_generated"] = {
        **GENERATED_MARKER,
        "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "artifact": artifact_key or str(path.relative_to(path.parents[4] if len(path.parents) > 4 else path.parent)),
        "sources": sources,
    }
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rel = path
    try:
        from compiler.paths import DELIVERY

        rel = path.relative_to(DELIVERY)
    except ValueError:
        rel = path.name
    return {
        "path": str(rel).replace("\\", "/"),
        "sha256": file_sha256(path),
        "sources": sources,
    }


def mirror_under_delivery(src: Path, rel_paths: list[str]) -> None:
    """Copia para caminhos espelhados (ex.: html/js) quando não são o mesmo inode."""
    from compiler.paths import DELIVERY

    for rel in rel_paths:
        dst = DELIVERY / rel
        if dst.resolve() == src.resolve():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
        except shutil.SameFileError:
            pass


def copy_generated(src: Path, dst: Path, sources: list[str]) -> dict:
    """Copia arquivo fonte para destino com envelope _generated JSON (se JSON)."""
    if src.suffix == ".json":
        data = load_json(src)
        return write_generated_json(dst, data, sources=sources)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    from compiler.paths import DELIVERY

    try:
        rel = dst.relative_to(DELIVERY)
    except ValueError:
        rel = dst.name
    return {
        "path": str(rel).replace("\\", "/"),
        "sha256": file_sha256(dst),
        "sources": sources,
    }
