#!/usr/bin/env python3
"""Decode exact Google Drive bytes into public/drive/."""
from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

OUT_DIR = Path("/workspace/cko-controlled/public/drive")

SPECS = [
    {
        "name": "SOURCE_REGISTRY.json",
        "out": OUT_DIR / "SOURCE_REGISTRY.json",
        "expected": 8469,
        "b64_file": Path("/workspace/cko-controlled/scripts/drive_b64/SOURCE_REGISTRY.b64"),
        "kind": "json",
        "json_checks": True,
    },
    {
        "name": "NEXT_CONVERSATION_INSTRUCTION_WAVE6.md",
        "out": OUT_DIR / "NEXT_CONVERSATION_INSTRUCTION_WAVE6.md",
        "expected": 3815,
        "b64_file": Path("/workspace/cko-controlled/scripts/drive_b64/WAVE6.b64"),
        "kind": "utf8",
        "required": ["MODEL OUTPUT != FACT", "CLOSED != FROZEN", "dENY"],
    },
    {
        "name": "CKO-MODULO-LEGISLACAO-MEMORIA-v4.md",
        "out": OUT_DIR / "CKO-MODULO-LEGISLACAO-MEMORIA-v4.md",
        "expected": 5317,
        "b64_file": Path("/workspace/cko-controlled/scripts/drive_b64/MEMORIA.b64"),
        "kind": "utf8",
        "required": ["ROLLBACK-v4", "didático", "full_legal_text_status"],
    },
    {
        "name": "CONVERSATION_INVENTORY_README.md",
        "out": OUT_DIR / "CONVERSATION_INVENTORY_README.md",
        "expected": 5332,
        "b64_file": Path("/workspace/cko-controlled/scripts/drive_b64/README.b64"),
        "kind": "utf8",
        "required": ["Inventário inicial"],
    },
]


def validate_json_source_registry(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    src_ref = next((r for r in obj.get("records", []) if r.get("source_id") == "SRC-REF-0001"), None)
    checks = {
        "production_status_HOLD": obj.get("production_status") == "HOLD",
        "default_ai_processing_permission_DENY": obj.get("default_ai_processing_permission") == "DENY",
        "SRC-REF-0001_rights_status_mixed_unknown": (
            src_ref is not None and src_ref.get("rights_status") == "mixed_unknown"
        ),
    }
    return {"json_valid": True, "checks": checks, "all_passed": all(checks.values())}


def validate_utf8(path: Path, required: list[str]) -> dict:
    text = path.read_text(encoding="utf-8")
    present = {s: (s in text) for s in required}
    missing = [s for s, ok in present.items() if not ok]
    return {"utf8_valid": True, "required_present": present, "all_passed": not missing, "missing": missing}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    exit_code = 0

    for spec in SPECS:
        name = spec["name"]
        b64_path = spec["b64_file"]
        result = {"name": name, "out": str(spec["out"]), "expected": spec["expected"]}

        if not b64_path.exists():
            result.update({"written": False, "error": f"missing b64: {b64_path}"})
            results.append(result)
            exit_code = 1
            print(f"SKIP {name}: missing {b64_path}")
            continue

        b64 = b64_path.read_text(encoding="ascii").strip()
        data = base64.b64decode(b64)
        actual = len(data)
        result["actual"] = actual

        if actual != spec["expected"]:
            result.update({
                "written": False,
                "error": f"size mismatch expected {spec['expected']} got {actual}",
            })
            results.append(result)
            exit_code = 1
            print(f"FAIL {name}: expected {spec['expected']} got {actual}")
            continue

        spec["out"].write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        result.update({"bytes": actual, "sha256": digest, "written": True})
        print(name, actual, digest)

        if spec.get("json_checks"):
            result["validation"] = validate_json_source_registry(spec["out"])
        elif spec.get("required"):
            result["validation"] = validate_utf8(spec["out"], spec["required"])

        if not result.get("validation", {}).get("all_passed", True):
            exit_code = 1

        results.append(result)

    print("\n=== SUMMARY ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
