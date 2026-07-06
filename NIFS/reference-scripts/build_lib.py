"""Build orchestration helpers: validation samples, reports, deploy zip."""
from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from seo_lib import SITE_NAME

JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def validate_jsonld_sample(out_dir: Path, *, sample: int = 60) -> dict:
    """Check JSON-LD presence and parseability on a random sample of pages."""
    locale_dirs = {"en", "es", "fr", "de", "it", "ja"}
    pages = [
        p for p in out_dir.rglob("*.html")
        if not (p.relative_to(out_dir).parts and p.relative_to(out_dir).parts[0] in locale_dirs)
    ][:sample]
    missing, invalid = [], []
    for p in pages:
        rel = p.relative_to(out_dir).as_posix()
        try:
            content = p.read_text(encoding="utf-8")
        except OSError:
            continue
        m = JSONLD_RE.search(content)
        if not m:
            missing.append(rel)
            continue
        try:
            json.loads(m.group(1))
        except json.JSONDecodeError:
            invalid.append(rel)
    return {
        "sampled": len(pages),
        "missing_count": len(missing),
        "invalid_count": len(invalid),
        "missing_sample": missing[:10],
        "invalid_sample": invalid[:10],
        "passed": len(invalid) == 0,
    }


def validate_a11y_sample(out_dir: Path, *, sample: int = 40) -> dict:
    locale_dirs = {"en", "es", "fr", "de", "it", "ja"}
    pages = [
        p for p in out_dir.rglob("*.html")
        if not (p.relative_to(out_dir).parts and p.relative_to(out_dir).parts[0] in locale_dirs)
    ][:sample]
    issues = []
    for p in pages:
        rel = p.relative_to(out_dir).as_posix()
        try:
            c = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if "<html lang=" not in c:
            issues.append({"file": rel, "issue": "Falta lang no html"})
        if 'name="description"' not in c:
            issues.append({"file": rel, "issue": "Falta meta description"})
    return {"sampled": len(pages), "issues_count": len(issues), "issues": issues[:15], "passed": len(issues) == 0}


def count_build_files(out_dir: Path) -> dict:
    counts = {"html": 0, "css": 0, "js": 0, "json": 0, "xml": 0, "txt": 0, "other": 0}
    for f in out_dir.rglob("*"):
        if not f.is_file():
            continue
        ext = f.suffix.lstrip(".").lower()
        counts[ext if ext in counts else "other"] += 1
    return counts


def write_build_report(
    out_dir: Path,
    *,
    phase_results: list[dict],
    file_counts: dict,
    link_audit: dict | None = None,
    jsonld: dict | None = None,
    a11y: dict | None = None,
    elapsed_s: float = 0,
) -> tuple[Path, Path]:
    """Write build-report.txt and build-report.json next to the site output."""
    root = out_dir.parent
    now = datetime.now(timezone.utc)
    lines = [
        "=" * 60,
        f"NKOS BUILD — {SITE_NAME}",
        now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "=" * 60,
        "",
        "ETAPAS",
        "-" * 60,
    ]
    for r in phase_results:
        icon = "OK" if r.get("status") == "OK" else "ERR"
        lines.append(f"  [{icon}] {r.get('name', '?'):<40} {r.get('elapsed_s', 0):>6.2f}s")

    lines += [
        "",
        "ARQUIVOS",
        "-" * 60,
        f"  HTML: {file_counts.get('html', 0)}",
        f"  TOTAL: {sum(file_counts.values())}",
        "",
    ]
    if link_audit:
        lines += [
            "LINKS",
            f"  Quebrados (main): {link_audit.get('broken_count', '?')}",
            f"  Quebrados (chrome): {link_audit.get('chrome_broken_count', '?')}",
            "",
        ]
    if jsonld:
        lines += [f"JSON-LD (amostra {jsonld.get('sampled', 0)}): sem={jsonld.get('missing_count', 0)} inválido={jsonld.get('invalid_count', 0)}", ""]
    lines += ["=" * 60, f"Tempo total: {elapsed_s:.1f}s", "=" * 60]

    txt_path = root / "build-report.txt"
    txt_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    report = {
        "built_at": now.isoformat().replace("+00:00", "Z"),
        "elapsed_s": round(elapsed_s, 2),
        "phases": phase_results,
        "file_counts": file_counts,
        "link_audit": link_audit,
        "jsonld_validation": jsonld,
        "a11y_validation": a11y,
    }
    json_path = root / "build-report.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return txt_path, json_path


def zip_build(out_dir: Path, zip_name: str = "nkos-site-build.zip") -> Path:
    zip_path = out_dir.parent / zip_name
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in out_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(out_dir))
    return zip_path
