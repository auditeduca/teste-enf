"""Validação determinística do banco JSON antes do upload."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from config import all_entities, resolve_entities  # noqa: E402
from dataset_io import read_envelope  # noqa: E402


@dataclass
class ValidationReport:
    ok: bool = True
    checks: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    entities: dict[str, dict] = field(default_factory=dict)
    validated_at: str = ""

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        self.ok = False

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _check_entity(meta: dict) -> dict:
    rel = meta["path"]
    pk = meta["pk"]
    key = meta["entity_key"]
    info = {"entity_key": key, "path": rel, "record_count": 0, "ok": True, "issues": []}

    try:
        env = read_envelope(rel)
    except FileNotFoundError:
        info["ok"] = False
        info["issues"].append("file_not_found")
        return info
    except json.JSONDecodeError as exc:
        info["ok"] = False
        info["issues"].append(f"json_error:{exc.msg}")
        return info

    records = env.get("records", [])
    info["record_count"] = len(records)
    info["schema_version"] = env.get("schema_version")
    info["entity"] = env.get("entity")

    declared = env.get("count")
    if declared is not None and declared != len(records):
        info["issues"].append(f"count_mismatch:declared={declared},actual={len(records)}")

    seen: set[str] = set()
    missing_pk = 0
    for rec in records:
        val = rec.get(pk)
        if not val:
            missing_pk += 1
            continue
        s = str(val)
        if s in seen:
            info["issues"].append(f"duplicate_pk:{s}")
            info["ok"] = False
        seen.add(s)

    if missing_pk:
        info["issues"].append(f"missing_pk:{missing_pk}")

    if info["issues"] and info["ok"]:
        info["ok"] = not any("duplicate" in i or "json_error" in i or "file_not_found" in i for i in info["issues"])

    return info


def run_validation(entity_keys: list[str] | None = None) -> ValidationReport:
    rep = ValidationReport(validated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    entities = resolve_entities(entity_keys) or all_entities()

    for meta in entities:
        rep.checks += 1
        info = _check_entity(meta)
        rep.entities[meta["entity_key"]] = info
        if not info["ok"]:
            rep.ok = False
            for issue in info["issues"]:
                if "duplicate" in issue or "file_not_found" in issue or "json_error" in issue:
                    rep.fail(f"{meta['entity_key']}:{issue}")
                else:
                    rep.warn(f"{meta['entity_key']}:{issue}")

    # Relatório global de fases (somente leitura — não bloqueia tier isolado)
    try:
        phase_report_path = ROOT / "datasets" / "metadata" / "validation_phases_1_7_report.json"
        if phase_report_path.is_file():
            phase = json.loads(phase_report_path.read_text(encoding="utf-8"))
            rep.checks += phase.get("checks", 0)
            for err in phase.get("errors", [])[:15]:
                rep.warn(f"phase_1_7:{err}")
    except Exception as exc:
        rep.warn(f"phase_1_7_read_skipped:{exc}")

    rep.ok = len(rep.errors) == 0
    return rep
