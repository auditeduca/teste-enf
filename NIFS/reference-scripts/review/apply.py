"""Apply DeepSeek-suggested fixes to reviewed files (with change log)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from review.change_log import DEFAULT_LOG, append_change
from review.config import (
    MAX_FILE_BYTES,
    REVIEW_EXTENSIONS,
    has_skip_dir_segment,
    is_under_skip_prefix,
)
from review.deepseek_client import chat_complete

FIX_SYSTEM = """Você corrige código do repositório CALENF-NKD com base nos achados da revisão.
Responda APENAS com JSON válido (sem markdown), no formato:
{
  "changes": [
    {
      "path": "scripts/exemplo.py",
      "summary": "descrição curta da correção",
      "replacements": [{"old": "trecho exato", "new": "trecho corrigido"}],
      "content": null
    }
  ]
}
Regras:
- Use "replacements" para patches pequenos (old deve existir literalmente no arquivo).
- Use "content" (arquivo completo) apenas se replacements não forem práticos.
- Não invente paths; só altere arquivos listados nos achados.
- Não altere secrets, .env, credenciais ou datasets grandes.
- Se não houver correção segura, omita o arquivo (lista vazia é válida)."""

BLOCKED_SUFFIXES = frozenset({".env", ".pem", ".key", ".p12"})
BLOCKED_NAMES = frozenset({".env", "credentials.json", "secrets.json"})


def _rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def validate_target_path(root: Path, rel: str) -> Path | None:
    rel = rel.replace("\\", "/").lstrip("/")
    if not rel or ".." in rel.split("/"):
        return None
    if Path(rel).name in BLOCKED_NAMES:
        return None
    if any(rel.lower().endswith(s) for s in BLOCKED_SUFFIXES):
        return None
    full = (root / rel).resolve()
    try:
        full.relative_to(root.resolve())
    except ValueError:
        return None
    if has_skip_dir_segment(Path(rel)):
        return None
    if is_under_skip_prefix(rel):
        return None
    if full.suffix.lower() not in REVIEW_EXTENSIONS:
        return None
    return full


def extract_paths_from_report(report_md: str) -> list[str]:
    found: list[str] = []
    for m in re.finditer(r"`((?:scripts|platform/src|docs)/[^`\s]+)`", report_md):
        p = m.group(1).replace("\\", "/")
        if p not in found:
            found.append(p)
    return found


def _parse_fix_json(raw: str) -> dict:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Resposta não é um objeto JSON")
    changes = data.get("changes")
    if changes is None:
        return {"changes": []}
    if not isinstance(changes, list):
        raise ValueError("Campo 'changes' inválido")
    return data


def apply_replacements(content: str, replacements: list[dict]) -> tuple[str, list[str]]:
    notes: list[str] = []
    for i, rep in enumerate(replacements):
        old = rep.get("old")
        new = rep.get("new")
        if not isinstance(old, str) or not isinstance(new, str):
            notes.append(f"replacement[{i}]: old/new inválidos")
            continue
        if old not in content:
            notes.append(f"replacement[{i}]: trecho não encontrado")
            continue
        content = content.replace(old, new, 1)
    return content, notes


def apply_single_change(
    root: Path,
    change: dict,
    *,
    log_path: Path = DEFAULT_LOG,
    source: str = "deepseek-apply",
    model: str = "",
    run_id: str = "",
) -> dict:
    rel = (change.get("path") or "").replace("\\", "/")
    summary = (change.get("summary") or "correção automática").strip()
    target = validate_target_path(root, rel)
    if not target:
        return {"path": rel, "applied": False, "error": "path não permitido"}

    if not target.exists():
        return {"path": rel, "applied": False, "error": "arquivo não existe"}

    before = target.read_text(encoding="utf-8")
    if len(before.encode("utf-8")) > MAX_FILE_BYTES:
        return {"path": rel, "applied": False, "error": "arquivo grande demais para aplicar"}

    full_content = change.get("content")
    replacements = change.get("replacements") or []
    after = before
    notes: list[str] = []

    if isinstance(full_content, str) and full_content.strip():
        after = full_content
    elif replacements:
        after, notes = apply_replacements(before, replacements)
    else:
        return {"path": rel, "applied": False, "error": "sem content nem replacements"}

    if after == before:
        return {"path": rel, "applied": False, "error": "nenhuma alteração efetiva", "notes": notes}

    if len(after.encode("utf-8")) > MAX_FILE_BYTES * 2:
        return {"path": rel, "applied": False, "error": "resultado excede limite de tamanho"}

    target.write_text(after, encoding="utf-8")
    log_entry = append_change(
        log_path,
        rel_path=rel,
        summary=summary,
        before=before,
        after=after,
        source=source,
        model=model,
        run_id=run_id,
        extra={"notes": notes} if notes else None,
    )
    return {"path": rel, "applied": True, "summary": summary, "log": log_entry, "notes": notes}


def request_fixes_from_deepseek(
    *,
    report_md: str,
    root: Path,
    paths: list[str],
    api_key: str,
    model: str,
) -> dict:
    blocks = []
    for rel in paths:
        target = validate_target_path(root, rel)
        if not target or not target.exists():
            continue
        content = target.read_text(encoding="utf-8")
        if len(content.encode("utf-8")) > MAX_FILE_BYTES:
            continue
        blocks.append(f"### `{rel}`\n```\n{content}\n```")

    if not blocks:
        return {"changes": []}

    user = (
        "Achados da revisão:\n\n"
        f"{report_md[:12000]}\n\n"
        "Arquivos a corrigir:\n\n"
        + "\n\n".join(blocks)
    )
    raw = chat_complete(
        [{"role": "system", "content": FIX_SYSTEM}, {"role": "user", "content": user}],
        api_key=api_key,
        model=model,
        max_tokens=8192,
    )
    return _parse_fix_json(raw)


def apply_fixes_from_report(
    *,
    root: Path | str,
    report_md: str,
    api_key: str,
    model: str = "deepseek-v4-flash",
    paths: list[str] | None = None,
    log_path: Path | None = None,
    run_id: str = "",
) -> dict:
    """Ask DeepSeek for fixes and apply them with audit log."""
    root = Path(root).resolve()
    log = log_path or DEFAULT_LOG
    targets = paths or extract_paths_from_report(report_md)
    if not targets:
        return {"applied": [], "skipped": [], "error": "Nenhum arquivo elegível nos achados."}

    try:
        fix_payload = request_fixes_from_deepseek(
            report_md=report_md,
            root=root,
            paths=targets,
            api_key=api_key,
            model=model,
        )
    except Exception as exc:
        return {"applied": [], "skipped": [], "error": str(exc)}

    applied: list[dict] = []
    skipped: list[dict] = []
    for change in fix_payload.get("changes") or []:
        result = apply_single_change(
            root,
            change,
            log_path=log,
            model=model,
            run_id=run_id,
        )
        if result.get("applied"):
            applied.append(result)
        else:
            skipped.append(result)
    return {
        "applied": applied,
        "skipped": skipped,
        "targets": targets,
        "error": "",
    }
