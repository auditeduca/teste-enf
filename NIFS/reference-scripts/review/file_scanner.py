"""Collect and classify files for AI review — skip large / vendor trees."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from review.config import (
    MAX_FILE_BYTES,
    MAX_FILE_LINES,
    MAX_FILES_TO_REVIEW,
    MAX_PATHS_DEFAULT,
    REVIEW_EXTENSIONS,
    has_skip_dir_segment,
    is_under_skip_prefix,
)


@dataclass
class FileEntry:
    path: str
    rel: str
    size: int
    lines: int
    mode: str  # full | skipped | omitted
    content: str = ""
    reason: str = ""


@dataclass
class ScanResult:
    root: Path
    entries: list[FileEntry] = field(default_factory=list)
    skipped: list[FileEntry] = field(default_factory=list)


def _line_count(text: str) -> int:
    return text.count("\n") + (1 if text and not text.endswith("\n") else 0)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def classify_file(root: Path, path: Path) -> FileEntry:
    rel = path.relative_to(root)
    rel_posix = rel.as_posix()
    size = path.stat().st_size

    skip_dir = has_skip_dir_segment(rel)
    if skip_dir:
        return FileEntry(str(path), rel_posix, size, 0, "skipped", reason=skip_dir)

    prefix = is_under_skip_prefix(rel_posix)
    if prefix:
        return FileEntry(str(path), rel_posix, size, 0, "skipped", reason=prefix)

    if path.suffix.lower() not in REVIEW_EXTENSIONS:
        return FileEntry(
            str(path), rel_posix, size, 0, "skipped",
            reason=f"extensão não revisável: {path.suffix or '(sem ext)'}",
        )

    if size > MAX_FILE_BYTES:
        return FileEntry(
            str(path), rel_posix, size, 0, "skipped",
            reason=f"arquivo grande ({size:,} bytes > {MAX_FILE_BYTES:,})",
        )

    try:
        text = _read_text(path)
    except OSError as exc:
        return FileEntry(str(path), rel_posix, size, 0, "skipped", reason=str(exc))

    lines = _line_count(text)
    if lines > MAX_FILE_LINES:
        return FileEntry(
            str(path), rel_posix, size, lines, "skipped",
            reason=f"muitas linhas ({lines} > {MAX_FILE_LINES})",
        )

    return FileEntry(str(path), rel_posix, size, lines, "full", content=text)


def iter_target_files(root: Path, targets: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in targets:
        p = (root / raw).resolve()
        if not str(p).startswith(str(root.resolve())):
            continue
        if not p.exists():
            continue
        if p.is_file():
            out.append(p)
            continue
        for fp in sorted(p.rglob("*")):
            if fp.is_file():
                out.append(fp)
    return out


def scan_paths(
    root: Path,
    targets: list[str] | None = None,
    *,
    max_files: int = MAX_FILES_TO_REVIEW,
) -> ScanResult:
    """Walk targets, classify each file, cap reviewable count."""
    root = root.resolve()
    target_list = targets or list(MAX_PATHS_DEFAULT)
    files = iter_target_files(root, target_list)
    result = ScanResult(root=root)

    reviewable = 0
    for path in files:
        entry = classify_file(root, path)
        if entry.mode == "full":
            if reviewable >= max_files:
                entry.mode = "skipped"
                entry.content = ""
                entry.reason = f"limite de {max_files} arquivos revisáveis atingido"
                result.skipped.append(entry)
            else:
                reviewable += 1
                result.entries.append(entry)
        else:
            result.skipped.append(entry)

    return result


def batch_entries(entries: list[FileEntry], max_chars: int) -> list[list[FileEntry]]:
    """Group files into LLM batches under char budget."""
    batches: list[list[FileEntry]] = []
    current: list[FileEntry] = []
    size = 0
    for entry in entries:
        block = f"### {entry.rel}\n```\n{entry.content}\n```\n"
        if current and size + len(block) > max_chars:
            batches.append(current)
            current = []
            size = 0
        current.append(entry)
        size += len(block)
    if current:
        batches.append(current)
    return batches
