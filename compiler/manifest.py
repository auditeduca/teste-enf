from __future__ import annotations

from datetime import datetime, timezone

from compiler.io import write_generated_json
from compiler.paths import MANIFEST


def write_manifest(artifacts: list[dict]) -> dict:
    payload = {
        "schema_version": "2026.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "compiler": "build_all.py",
        "artifacts": {a["path"]: {"sha256": a["sha256"], "sources": a["sources"]} for a in artifacts},
    }
    return write_generated_json(
        MANIFEST,
        payload,
        sources=["compiler/build_all.py"],
        artifact_key="build-manifest.json",
    )
