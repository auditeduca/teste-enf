"""CLI — Professional Intelligence Hub."""
from __future__ import annotations

import argparse
import json

from exam_planner import build_exam_plan
from regulatory_agent import query_regulatory
from status import collect_status
from tool_context import resolve_tool_context


def main() -> None:
    p = argparse.ArgumentParser(description="NPIH — Professional Intelligence agents")
    p.add_argument("--status", action="store_true")
    p.add_argument("--tool", help="TOOL.BRADEN etc.")
    p.add_argument("--persona", default="profissional")
    p.add_argument("--question", help="Regulatory query")
    p.add_argument("--exam-goal", help="Exam prep goal")
    p.add_argument("--exam-days", type=int, default=30)
    args = p.parse_args()

    if args.status:
        print(json.dumps(collect_status(), ensure_ascii=False, indent=2))
        return
    if args.tool:
        print(json.dumps(resolve_tool_context(args.tool, persona=args.persona), ensure_ascii=False, indent=2))
        return
    if args.question:
        print(json.dumps(query_regulatory(args.question), ensure_ascii=False, indent=2))
        return
    if args.exam_goal:
        print(json.dumps(build_exam_plan(args.exam_goal, days=args.exam_days), ensure_ascii=False, indent=2))
        return
    print(json.dumps(collect_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
