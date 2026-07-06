"""Validação determinística — agentes conteúdo."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from content.validate_content import run_validation  # noqa: E402


def validate_all_fields() -> dict:
    rep = run_validation()
    return {
        "checks": rep.checks,
        "errors": rep.errors,
        "warnings": rep.warnings,
        "passed": rep.passed,
        "ok": len(rep.errors) == 0,
    }


def validate_field(field_id: str) -> dict:
    result = validate_all_fields()
    related = [
        x
        for x in result["errors"] + result["warnings"] + result["passed"]
        if x.get("field_id") == field_id or field_id.split(".")[1] in x.get("field_id", "")
    ]
    return {
        "field_id": field_id,
        "ok": not any(x.get("status") == "fail" for x in related) and result["ok"],
        "findings": related[:10],
    }
