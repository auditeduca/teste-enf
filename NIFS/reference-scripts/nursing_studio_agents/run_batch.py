"""CLI — Nursing Studio."""
from __future__ import annotations

import argparse
import json

from status import collect_status
from workflow_runner import run_studio_pipeline


def main() -> None:
    p = argparse.ArgumentParser(description="NKOS Studio — social image generator + graph agents")
    p.add_argument("--status", action="store_true")
    p.add_argument("--tool", default="TOOL.BRADEN")
    p.add_argument("--format", default="instagram_post")
    p.add_argument("--persona", default="estudante")
    p.add_argument("--country", default="BR")
    args = p.parse_args()

    if args.status:
        print(json.dumps(collect_status(), ensure_ascii=False, indent=2))
        return

    print(json.dumps(run_studio_pipeline(
        tool_code=args.tool,
        format_id=args.format,
        persona=args.persona,
        country=args.country,
    ), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
