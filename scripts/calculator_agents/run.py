"""CLI — agentes de validação, correção e geração de calculadoras."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .correct import run_correction
from .env import env_status, load_env
from .generate import run_generation
from .validate import run_validation


def cmd_status(_args: argparse.Namespace) -> int:
    load_env()
    print(json.dumps(env_status(), ensure_ascii=False, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    slugs = args.slugs if args.slugs else None
    report = run_validation(slugs=slugs)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 1 if report.to_dict()["errors"] else 0


def cmd_correct(args: argparse.Namespace) -> int:
    use_llm = args.llm and not args.no_llm
    reports = []
    for slug in args.slugs:
        reports.append(run_correction(slug, use_llm=use_llm).to_dict())
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    use_llm = args.llm and not args.no_llm
    report = run_generation(
        args.slug,
        name=args.name,
        description=args.description,
        use_llm=use_llm,
        draft_json=args.draft,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.output_path else 1


def cmd_pipeline(args: argparse.Namespace) -> int:
    """validate → correct → validate (relatório final)."""
    slugs = args.slugs
    use_llm = args.llm and not args.no_llm

    before = run_validation(slugs=slugs)
    corrections = [run_correction(s, use_llm=use_llm).to_dict() for s in slugs]
    after = run_validation(slugs=slugs)

    payload = {
        "before": before.to_dict(),
        "corrections": corrections,
        "after": after.to_dict(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if after.to_dict()["errors"] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Agentes de validação, correção e geração — calculadoras/escalas",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Status das APIs e .env")
    p_status.set_defaults(func=cmd_status)

    p_val = sub.add_parser("validate", help="Validar páginas HTML")
    p_val.add_argument("slugs", nargs="*", help="Slugs (vazio = todas calculadoras)")
    p_val.set_defaults(func=cmd_validate)

    p_cor = sub.add_parser("correct", help="Corrigir páginas (sync JSON, footer, LLM)")
    p_cor.add_argument("slugs", nargs="+", help="Slugs das calculadoras")
    p_cor.add_argument("--llm", action="store_true", help="Revisão clínica via API")
    p_cor.add_argument("--no-llm", action="store_true", help="Forçar sem LLM")
    p_cor.set_defaults(func=cmd_correct)

    p_gen = sub.add_parser("generate", help="Gerar HTML a partir de JSON")
    p_gen.add_argument("slug", help="Slug da ferramenta")
    p_gen.add_argument("--name", help="Nome para rascunho LLM")
    p_gen.add_argument("--description", help="Descrição para rascunho LLM")
    p_gen.add_argument("--draft", action="store_true", help="Gerar JSON via LLM antes do HTML")
    p_gen.add_argument("--llm", action="store_true", help="Usar LLM para rascunho JSON")
    p_gen.add_argument("--no-llm", action="store_true")
    p_gen.set_defaults(func=cmd_generate)

    p_pipe = sub.add_parser("pipeline", help="validate → correct → validate")
    p_pipe.add_argument("slugs", nargs="+")
    p_pipe.add_argument("--llm", action="store_true")
    p_pipe.add_argument("--no-llm", action="store_true")
    p_pipe.set_defaults(func=cmd_pipeline)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
