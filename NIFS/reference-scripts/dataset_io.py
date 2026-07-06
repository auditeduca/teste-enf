"""Shard-aware dataset I/O for CALENF-NKD.

Large dataset envelopes are transparently split into shard files so individual
JSON files stay manageable. A sharded main file keeps the envelope metadata,
an empty ``records`` list, and a ``shard_files`` index; the shard files each
hold a plain JSON list of records.

Use ``read_envelope`` / ``write_envelope`` instead of raw json load/dump for any
dataset that may grow large. Both accept a path relative to the datasets root
(e.g. ``"content/translations.json"``) or an absolute Path.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "datasets"
DEFAULT_MAX_PER_SHARD = 20000


def _resolve(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else (ROOT / p)


def _shard_dir(main: Path) -> Path:
    return main.with_suffix(".shards")


def read_envelope(path: str | Path) -> dict:
    """Load an envelope, merging shard files when the dataset is sharded."""
    main = _resolve(path)
    with open(main, encoding="utf-8") as f:
        env = json.load(f)
    if not env.get("sharded"):
        return env
    records: list = []
    for rel in env.get("shard_files", []):
        with open(_resolve(rel), encoding="utf-8") as f:
            records.extend(json.load(f))
    env["records"] = records
    return env


def write_envelope(path: str | Path, env: dict, *, max_per_shard: int = DEFAULT_MAX_PER_SHARD) -> int:
    """Write an envelope, auto-sharding records above ``max_per_shard``.

    Returns the number of shard files written (0 when stored inline).
    """
    main = _resolve(path)
    main.parent.mkdir(parents=True, exist_ok=True)
    records = env.get("records", [])
    shard_dir = _shard_dir(main)

    if len(records) <= max_per_shard:
        if shard_dir.exists():
            shutil.rmtree(shard_dir)
        env.pop("sharded", None)
        env.pop("shard_files", None)
        env.pop("shard_count", None)
        with open(main, "w", encoding="utf-8", newline="\n") as f:
            json.dump(env, f, indent=2, ensure_ascii=False)
            f.write("\n")
        return 0

    if shard_dir.exists():
        shutil.rmtree(shard_dir)
    shard_dir.mkdir(parents=True, exist_ok=True)
    shard_files: list[str] = []
    rel_dir = shard_dir.relative_to(ROOT).as_posix()
    for i in range(0, len(records), max_per_shard):
        part = records[i : i + max_per_shard]
        idx = i // max_per_shard
        fname = f"part-{idx:03d}.json"
        with open(shard_dir / fname, "w", encoding="utf-8", newline="\n") as f:
            json.dump(part, f, indent=2, ensure_ascii=False)
            f.write("\n")
        shard_files.append(f"{rel_dir}/{fname}")

    manifest = {k: v for k, v in env.items() if k != "records"}
    manifest["count"] = len(records)
    manifest["sharded"] = True
    manifest["shard_count"] = len(shard_files)
    manifest["max_per_shard"] = max_per_shard
    manifest["shard_files"] = shard_files
    manifest["records"] = []
    with open(main, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return len(shard_files)


def read_envelope_meta(path: str | Path) -> dict:
    """Load envelope metadata only (does not read shard bodies)."""
    main = _resolve(path)
    with open(main, encoding="utf-8") as f:
        return json.load(f)


def iter_records(path: str | Path):
    """Yield records shard-by-shard to avoid loading entire datasets into memory."""
    meta = read_envelope_meta(path)
    if not meta.get("sharded"):
        yield from meta.get("records", [])
        return
    for rel in meta.get("shard_files", []):
        with open(_resolve(rel), encoding="utf-8") as f:
            yield from json.load(f)


def record_count(path: str | Path) -> int:
    """Return record count using manifest ``count`` when available."""
    meta = read_envelope_meta(path)
    if meta.get("count") is not None:
        return int(meta["count"])
    if not meta.get("sharded"):
        return len(meta.get("records", []))
    total = 0
    for rel in meta.get("shard_files", []):
        with open(_resolve(rel), encoding="utf-8") as f:
            total += len(json.load(f))
    return total


def find_record(path: str | Path, pk: str, record_id: str) -> dict | None:
    """Locate a single record without loading the full envelope."""
    rid = str(record_id)
    for rec in iter_records(path):
        if str(rec.get(pk, "")) == rid or str(rec.get("uuid", "")) == rid:
            return rec
    return None


def paginate_records(
    path: str | Path,
    predicate,
    *,
    offset: int = 0,
    limit: int = 50,
) -> tuple[int, list]:
    """Filter and paginate in a single lazy pass over records."""
    total = 0
    skipped = 0
    page: list = []
    for rec in iter_records(path):
        if predicate and not predicate(rec):
            continue
        if skipped < offset:
            skipped += 1
            total += 1
            continue
        if len(page) < limit:
            page.append(rec)
        total += 1
    return total, page
