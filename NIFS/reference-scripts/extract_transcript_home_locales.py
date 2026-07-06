#!/usr/bin/env python3
"""Extract all home_page 2026.3 JSON blocks from agent transcript."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRANSCRIPT_DIR = Path.home() / ".cursor" / "projects" / "c-Github-CALENF-NKD" / "agent-transcripts"
TRANSCRIPT = Path(
    os.environ.get(
        "CALENF_TRANSCRIPT",
        DEFAULT_TRANSCRIPT_DIR
        / "73f51c25-f43e-414f-8f4a-f0d64f6ba808"
        / "73f51c25-f43e-414f-8f4a-f0d64f6ba808.jsonl",
    )
)
OUT = ROOT / "datasets" / "content" / "schemas" / "extracted-locales"
BY_LOCALE = ROOT / "datasets" / "by-locale"

TARGET_LOCALES = [
    "ar", "zh-CN", "hi-IN", "ru-RU", "ko-KR", "tr-TR", "id-ID", "vi-VN",
    "pl-PL", "nl-NL", "th-TH",
]


def _parse_json_blocks(text: str) -> list[dict]:
    blocks: list[dict] = []
    for m in re.finditer(r"```json\s*\n(\{.*?\})\s*\n```", text, re.DOTALL):
        try:
            data = json.loads(m.group(1))
            if data.get("schema_version") == "2026.3.0" and data.get("page_sections_order"):
                blocks.append(data)
        except json.JSONDecodeError:
            continue
    # fallback: raw object starting with schema_version 2026.3
    if not blocks and '"schema_version": "2026.3.0"' in text and "page_sections_order" in text:
        start = text.find('{\n  "generated_at"')
        if start < 0:
            start = text.find('{"generated_at"')
        if start < 0:
            start = text.find('{')
        if start >= 0:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            data = json.loads(text[start : i + 1])
                            if data.get("schema_version") == "2026.3.0":
                                blocks.append(data)
                        except json.JSONDecodeError:
                            pass
                        break
    return blocks


def main() -> int:
    if not TRANSCRIPT.is_file():
        print(f"Transcript not found: {TRANSCRIPT}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    best: dict[str, tuple[int, dict]] = {}

    with TRANSCRIPT.open(encoding="utf-8") as f:
        for line in f:
            if "2026.3.0" not in line:
                continue
            try:
                obj = json.loads(line)
                text = obj["message"]["content"][0]["text"]
            except (json.JSONDecodeError, KeyError, IndexError):
                text = line
            for data in _parse_json_blocks(text):
                loc = str(data.get("locale", "")).strip()
                if not loc:
                    continue
                size = len(json.dumps(data, ensure_ascii=False))
                if loc not in best or size > best[loc][0]:
                    best[loc] = (size, data)

    for loc, (_, data) in sorted(best.items()):
        safe = loc.replace("/", "-")
        path = OUT / f"home_page.{safe}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("extracted", loc, "->", path.relative_to(ROOT))

    copied = 0
    for loc in TARGET_LOCALES:
        src = OUT / f"home_page.{loc.replace('/', '-')}.json"
        if not src.is_file():
            print("missing", loc)
            continue
        data = json.loads(src.read_text(encoding="utf-8"))
        data["locale"] = loc
        data["i18n_status"] = "translated"
        data["partition"] = "locale"
        data.pop("daily_tip", None)
        data.pop("education_block", None)
        dst_dir = BY_LOCALE / loc
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / "home_page.json"
        dst.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("copied", dst.relative_to(ROOT))
        copied += 1

    print(f"Total extracted locales: {len(best)}; copied targets: {copied}/{len(TARGET_LOCALES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
