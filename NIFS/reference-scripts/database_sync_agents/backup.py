"""Backup de segurança antes de finalizar ou fazer upload da base."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from config import ENTITY_TIERS, ROOT

BACKUPS_ROOT = ROOT / "datasets" / "backups"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _collect_paths(*, full: bool = False, tiers: list[str] | None = None) -> list[Path]:
    paths: set[Path] = set()

    if full:
        datasets = ROOT / "datasets"
        for p in datasets.rglob("*.json"):
            if "backups" in p.parts or "node_modules" in p.parts:
                continue
            paths.add(p)
        return sorted(paths)

    tier_keys = tiers or list(ENTITY_TIERS.keys())
    for tier in tier_keys:
        for meta in ENTITY_TIERS.get(tier, []):
            rel = meta["path"]
            src = ROOT / "datasets" / rel
            if src.is_file():
                paths.add(src)
            shard_dir = src.with_suffix(".shards")
            if shard_dir.is_dir():
                paths.update(shard_dir.rglob("*.json"))

    # Metadados críticos do sync
    for extra in (
        "metadata/canonical_registry.json",
        "master-data/database-sync/supabase_schema.sql",
    ):
        p = ROOT / "datasets" / extra
        if p.is_file():
            paths.add(p)

    return sorted(paths)


def create_security_backup(
    *,
    full: bool = False,
    tiers: list[str] | None = None,
    label: str = "pre_finalize",
) -> dict:
    """Copia arquivos para datasets/backups/BKP.{timestamp}/ com manifesto."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_id = f"BKP.{ts}"
    dest_root = BACKUPS_ROOT / backup_id
    dest_root.mkdir(parents=True, exist_ok=True)

    sources = _collect_paths(full=full, tiers=tiers)
    manifest_files: list[dict] = []
    copied = 0
    total_bytes = 0

    for src in sources:
        rel = src.relative_to(ROOT / "datasets")
        dest = dest_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        size = src.stat().st_size
        total_bytes += size
        copied += 1
        manifest_files.append({
            "relative_path": rel.as_posix(),
            "size_bytes": size,
            "sha256": _sha256(src),
        })

    manifest = {
        "backup_id": backup_id,
        "label": label,
        "created_at": _now(),
        "full": full,
        "tiers": tiers or list(ENTITY_TIERS.keys()),
        "file_count": copied,
        "total_bytes": total_bytes,
        "files": manifest_files,
        "restore_hint": f"Copie de datasets/backups/{backup_id}/ de volta para datasets/",
    }
    manifest_path = dest_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "backup_id": backup_id,
        "path": str(dest_root),
        "manifest_path": str(manifest_path),
        "file_count": copied,
        "total_bytes": total_bytes,
    }


def list_backups(limit: int = 20) -> list[dict]:
    if not BACKUPS_ROOT.is_dir():
        return []
    out = []
    for d in sorted(BACKUPS_ROOT.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        if not d.is_dir() or not d.name.startswith("BKP."):
            continue
        manifest_path = d / "manifest.json"
        if manifest_path.is_file():
            out.append(json.loads(manifest_path.read_text(encoding="utf-8")))
        else:
            out.append({"backup_id": d.name, "path": str(d)})
    return out


def restore_backup(backup_id: str, *, dry_run: bool = True) -> dict:
    """Restaura arquivos do backup (use dry_run=False com cuidado)."""
    src_root = BACKUPS_ROOT / backup_id
    manifest_path = src_root / "manifest.json"
    if not manifest_path.is_file():
        return {"ok": False, "error": "backup_not_found", "backup_id": backup_id}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored = []
    for entry in manifest.get("files", []):
        rel = entry["relative_path"]
        src = src_root / rel
        dest = ROOT / "datasets" / rel
        if not src.is_file():
            continue
        if dry_run:
            restored.append({"path": rel, "dry_run": True})
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            restored.append({"path": rel, "restored": True})

    return {
        "ok": True,
        "backup_id": backup_id,
        "dry_run": dry_run,
        "restored_count": len(restored),
        "files": restored[:50],
    }
