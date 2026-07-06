"""Etapa extract — parse CSV (;) para registros brutos."""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

from config import ANV_DIR, SCRAPE_CACHE, SCRAPE_SOURCES


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _detect_delimiter(sample: str) -> str:
    if sample.count(";") >= sample.count(","):
        return ";"
    return ","


def parse_csv_file(path: Path, *, max_rows: int | None = None) -> list[dict]:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "latin-1", "cp1252"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            text = raw.decode("latin-1", errors="replace")
    delim = _detect_delimiter(text[:4096])
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    rows = []
    for i, row in enumerate(reader):
        if max_rows and i >= max_rows:
            break
        clean = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
        if clean:
            rows.append(clean)
    return rows


def extract_from_cache(source: dict, *, max_rows: int | None = None) -> dict:
    sid = source["source_id"]
    csv_path = SCRAPE_CACHE / f"{sid.replace('.', '_')}.csv"
    meta_path = SCRAPE_CACHE / f"{sid.replace('.', '_')}.json"
    if not csv_path.is_file():
        return {"source_id": sid, "ok": False, "error": "csv_missing", "rows": []}
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    limit = max_rows
    fname = (source.get("filename") or "").upper()
    if "VIGIMED" in fname and limit is None:
        limit = 5000
    if "PRECOS" in fname and limit is None:
        limit = 20000
    rows = parse_csv_file(csv_path, max_rows=limit)
    return {
        "source_id": sid,
        "filename": source.get("filename"),
        "ok": bool(rows),
        "row_count": len(rows),
        "content_hash": meta.get("content_hash"),
        "rows": rows,
        "extracted_at": _now(),
    }


def extract_all(*, limit: int | None = None, priority_only: bool = True) -> dict:
    sources = json.loads(SCRAPE_SOURCES.read_text(encoding="utf-8")).get("sources", [])
    if priority_only:
        pri = [s for s in sources if s.get("priority") == 1]
        sources = pri or sources[:5]
    if limit:
        sources = sources[:limit]
    results = [extract_from_cache(s) for s in sources]
    total_rows = sum(r.get("row_count", 0) for r in results)
    report = {
        "generated_at": _now(),
        "sources": len(results),
        "rows_extracted": total_rows,
        "results": [{k: v for k, v in r.items() if k != "rows"} for r in results],
        "extracted": results,
    }
    out = ANV_DIR / "extract_report.json"
    # Persist full rows in separate cache files to keep report small
    for r in results:
        if r.get("rows"):
            sid = r["source_id"].replace(".", "_")
            (ANV_DIR / "extract_cache").mkdir(parents=True, exist_ok=True)
            (ANV_DIR / "extract_cache" / f"{sid}.json").write_text(
                json.dumps({"rows": r["rows"]}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    slim = {**report, "extracted": [{k: v for k, v in r.items() if k != "rows"} for r in results]}
    out.write_text(json.dumps(slim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["extracted"] = results
    return report
