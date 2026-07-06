#!/usr/bin/env python3
"""CLI — Visual Experience Intelligence Platform (VEIP).

  python scripts/visual_intelligence_agents/run_batch.py --generate-all
  python scripts/visual_intelligence_agents/run_batch.py --generate sustentabilidade
  python scripts/visual_intelligence_agents/run_batch.py --audit website/assets/images/og/sustentabilidade-pt-br.svg
  python scripts/visual_intelligence_agents/run_batch.py --prompt-dna --page glasgow --persona estudante
  python scripts/visual_intelligence_agents/run_batch.py --status
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from og_generator import generate_all, generate_og  # noqa: E402
from prompt_dna import build_prompt, build_visual_dna  # noqa: E402
from status import collect_status  # noqa: E402
from vga_audit import audit_image, audit_manifest_entry  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Visual Intelligence agents (VEIP)")
    p.add_argument("--status", action="store_true")
    p.add_argument("--generate-all", action="store_true")
    p.add_argument("--generate", metavar="TEMPLATE", help="e.g. sustentabilidade, privacidade, glasgow")
    p.add_argument("--locale", default="pt-BR")
    p.add_argument("--persona", default="profissional")
    p.add_argument("--audit", metavar="PATH", help="Audit image file")
    p.add_argument("--audit-path", metavar="CANONICAL", help="Audit by canonical path e.g. /sustentabilidade")
    p.add_argument("--country", default="BR")
    p.add_argument("--page-type", default="sustainability")
    p.add_argument("--prompt-dna", action="store_true")
    p.add_argument("--page", default="sustentabilidade")
    p.add_argument("--tool", default=None)
    p.add_argument("--mode", default="study")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.status:
        result = collect_status()
    elif args.generate_all:
        result = generate_all(locale=args.locale)
    elif args.generate:
        result = generate_og(args.generate, locale=args.locale, persona=args.persona)
    elif args.audit:
        rep = audit_image(
            args.audit,
            country=args.country,
            page_type=args.page_type,
            persona=args.persona,
            template_key=args.generate,
        )
        result = rep.to_dict()
    elif args.audit_path:
        rep = audit_manifest_entry(args.audit_path)
        result = rep.to_dict() if rep else {"error": "No manifest entry"}
    elif args.prompt_dna:
        dna = build_visual_dna(
            locale=args.locale,
            persona=args.persona,
            tool=args.tool,
            page=args.page,
            mode=args.mode,
        )
        result = {"dna": dna, "prompt": build_prompt(dna, asset_type="og")}
    else:
        result = generate_all(locale=args.locale)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.status:
            print(
                f"VEIP: {result['manifest_entries']}/{result['templates_total']} templates · "
                f"{result['og_files_svg']} SVG · {result['completion_pct']}%"
            )
        elif args.generate or args.generate_all:
            print(f"Gerado: {result.get('generated', 1)} OG · ok={result.get('ok', True)}")
        elif args.audit or args.audit_path:
            print(f"Score: {result.get('overall_score')} ({result.get('level')})")
        elif args.prompt_dna:
            print(result["prompt"][:500] + "...")

    return 0 if result.get("ok", True) and "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
