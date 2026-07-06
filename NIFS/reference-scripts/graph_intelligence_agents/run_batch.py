"""CLI — Graph Intelligence agents."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Carrega .env antes de qualquer agente LLM
_scripts = Path(__file__).resolve().parent.parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from agent_common.env_loader import load_project_env  # noqa: E402

load_project_env()

from content_agent import generate_clinical_content, generate_cross_tool_intelligence
from graph_snapshot import build_inventory_stats, detect_structural_issues
from status import collect_status
from validator_agent import fast_screen, validate_graph


def main() -> None:
    p = argparse.ArgumentParser(description="Graph Intelligence — validação e conteúdo clínico")
    p.add_argument("--status", action="store_true")
    p.add_argument("--inventory", action="store_true")
    p.add_argument("--structural", action="store_true")
    p.add_argument("--validate", action="store_true", help="Validação completa (Claude se disponível)")
    p.add_argument("--fast-screen", action="store_true", help="Screening rápido (Groq/Llama)")
    p.add_argument("--tool", help="TOOL.GCS etc. — conteúdo ou cross-tool")
    p.add_argument("--content", action="store_true", help="Gerar conteúdo de decisão clínica")
    p.add_argument("--cross-tool", action="store_true", help="Inteligência entre ferramentas")
    p.add_argument("--phase-content-batch", action="store_true", help="P4 — conteúdo clínico em lote")
    p.add_argument("--phase-cross-batch", action="store_true", help="P5 — cross-tool em lote")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--no-llm", action="store_true")
    p.add_argument("--provider", choices=["claude", "deepseek", "groq"])
    p.add_argument("--api-key", help="Override API key")
    args = p.parse_args()

    payload = {}
    if args.api_key:
        payload["api_key"] = args.api_key
    if args.no_llm:
        payload["no_llm"] = True
    if args.provider:
        payload["provider"] = args.provider

    if args.status:
        print(json.dumps(collect_status(), ensure_ascii=False, indent=2))
        return
    if args.inventory:
        print(json.dumps(build_inventory_stats(), ensure_ascii=False, indent=2))
        return
    if args.structural:
        print(json.dumps(detect_structural_issues(), ensure_ascii=False, indent=2))
        return
    if args.validate:
        print(json.dumps(
            validate_graph(use_llm=not args.no_llm, provider=args.provider, payload=payload),
            ensure_ascii=False,
            indent=2,
        ))
        return
    if args.fast_screen:
        print(json.dumps(fast_screen(payload=payload), ensure_ascii=False, indent=2))
        return
    if args.tool and args.content:
        print(json.dumps(
            generate_clinical_content(args.tool, use_llm=not args.no_llm, payload=payload),
            ensure_ascii=False,
            indent=2,
        ))
        return
    if args.tool and args.cross_tool:
        print(json.dumps(
            generate_cross_tool_intelligence(args.tool, payload=payload),
            ensure_ascii=False,
            indent=2,
        ))
        return
    if args.phase_content_batch:
        from paths import clinical_tools  # noqa: WPS433

        tools = [t for t in clinical_tools() if t.get("tool_code")][: args.limit]
        results = []
        for tool in tools:
            code = tool["tool_code"]
            results.append(generate_clinical_content(code, use_llm=not args.no_llm, payload=payload))
        ok = sum(1 for r in results if r.get("ok"))
        print(json.dumps({
            "ok": ok > 0,
            "phase": "P4_content_enrichment",
            "processed": len(results),
            "succeeded": ok,
            "results": results,
        }, ensure_ascii=False, indent=2))
        return
    if args.phase_cross_batch:
        from paths import clinical_tools  # noqa: WPS433

        tools = [t for t in clinical_tools() if t.get("tool_code")][: args.limit]
        results = []
        for tool in tools:
            code = tool["tool_code"]
            results.append(generate_cross_tool_intelligence(code, payload=payload))
        ok = sum(1 for r in results if r.get("ok"))
        print(json.dumps({
            "ok": ok > 0,
            "phase": "P5_cross_tool",
            "processed": len(results),
            "succeeded": ok,
            "results": results,
        }, ensure_ascii=False, indent=2))
        return

    print(json.dumps(collect_status(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
