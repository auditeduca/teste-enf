"""Migrate invalid NIC related_tool_codes (TOOL.CALC/ESCAL/PROTO) to real catalog tools."""
from __future__ import annotations

import json
from pathlib import Path

from nkos_nnn_2026_catalog import resolve_nic_tool_codes, _INVALID_TOOL_BUCKETS

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"


def main() -> int:
    tools = json.loads((DATASETS / "clinical" / "clinical_tools_catalog.json").read_text(encoding="utf-8"))["records"]
    path = DATASETS / "clinical" / "nursing_interventions.json"
    envelope = json.loads(path.read_text(encoding="utf-8"))
    records = envelope["records"]
    fixed = 0
    for rec in records:
        codes = list(rec.get("related_tool_codes") or [])
        if not codes:
            nic_num = (rec.get("nic_code") or rec.get("intervention_code", "").replace("NIC.", ""))
            bucket = ["TOOL.CALC", "TOOL.ESCAL", "TOOL.PROTO"][int(nic_num or 0) % 3]
            codes = [bucket]
        if not any(c in _INVALID_TOOL_BUCKETS for c in codes):
            continue
        nic_num = (rec.get("nic_code") or rec.get("intervention_code", "").replace("NIC.", ""))
        resolved = resolve_nic_tool_codes(str(nic_num), codes, tools)
        if resolved and resolved != codes:
            rec["related_tool_codes"] = resolved
            fixed += 1
    envelope["records"] = records
    envelope["count"] = len(records)
    path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Fixed {fixed}/{len(records)} NIC records -> real tool_code FKs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
