"""Add linked_tool_codes to forum topics and career paths."""
from __future__ import annotations

import json
from pathlib import Path

from community_tool_links import CAREER_PATH_TOOLS, FORUM_SPECIALTY_TOOLS, filter_valid_tools

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"


def _patch(path: Path, key: str, mapper) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    tools = {
        t["tool_code"]
        for t in json.loads((DATASETS / "clinical" / "clinical_tools_catalog.json").read_text(encoding="utf-8"))["records"]
    }
    fixed = 0
    for rec in data["records"]:
        linked = filter_valid_tools(mapper(rec), tools)
        if rec.get("linked_tool_codes") != linked:
            rec["linked_tool_codes"] = linked
            fixed += 1
    data["count"] = len(data["records"])
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{path.name}: updated {fixed}/{len(data['records'])}")
    return fixed


def main() -> int:
    _patch(
        DATASETS / "community" / "forum_topics.json",
        "forum_topic_code",
        lambda r: FORUM_SPECIALTY_TOOLS.get(r.get("specialty", ""), []),
    )
    _patch(
        DATASETS / "community" / "career_paths.json",
        "career_path_code",
        lambda r: CAREER_PATH_TOOLS.get(r.get("career_path_code", ""), []),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
