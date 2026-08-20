"""Validate tool JSON files against tool.schema.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft7Validator

from .paths import SCHEMA_PATH, TOOLS_DIR


def load_schema(path: Path | None = None) -> dict[str, Any]:
    schema_path = path or SCHEMA_PATH
    return json.loads(schema_path.read_text(encoding="utf-8"))


def load_tool(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_tool(tool: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    validator = Draft7Validator(schema or load_schema())
    return sorted(error.message for error in validator.iter_errors(tool))


def iter_tool_files(tools_dir: Path | None = None) -> Iterable[Path]:
    directory = tools_dir or TOOLS_DIR
    return sorted(directory.glob("*.json"))


def validate_tools_dir(tools_dir: Path | None = None, schema: dict[str, Any] | None = None) -> dict[str, list[str]]:
    schema = schema or load_schema()
    failures: dict[str, list[str]] = {}
    for path in iter_tool_files(tools_dir):
        errors = validate_tool(load_tool(path), schema)
        if errors:
            failures[path.name] = errors
    return failures
