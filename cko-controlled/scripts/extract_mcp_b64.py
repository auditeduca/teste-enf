#!/usr/bin/env python3
"""Extract base64 content fields from MCP download JSON files."""
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <mcp.json> <out.b64>", file=sys.stderr)
        return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    payload = json.loads(src.read_text(encoding="utf-8"))
    content = payload["content"]
    dst.write_text(content, encoding="ascii")
    print(f"extracted {len(content)} chars -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
