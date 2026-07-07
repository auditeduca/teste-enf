"""Agente de geração — JSON de ferramenta e HTML a partir de data/tools/."""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .env import REF_SCRIPTS, load_env, llm_enabled

WORKSPACE = Path(__file__).resolve().parents[2]
DELIVERY_HTML = WORKSPACE / "NIFS" / "DELIVERY" / "html"
REF_WEBSITE = WORKSPACE / "reference-website"
TOOLS_JSON = REF_WEBSITE / "data" / "tools"
GENERATOR = REF_WEBSITE / "scripts" / "generate_tool_page.py"
SCHEMA_PATH = REF_WEBSITE / "data" / "schemas" / "tool.schema.json"


@dataclass
class GenerationReport:
    slug: str
    output_path: str | None = None
    json_path: str | None = None
    llm_used: bool = False
    steps: list[str] = field(default_factory=list)

    def add(self, step: str) -> None:
        self.steps.append(step)

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "output_path": self.output_path,
            "json_path": self.json_path,
            "llm_used": self.llm_used,
            "steps": self.steps,
        }


def _llm_draft_tool_json(
    *,
    slug: str,
    name: str,
    description: str,
    category: str = "Enfermagem",
) -> dict | None:
    if REF_SCRIPTS.is_dir() and str(REF_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(REF_SCRIPTS))
    try:
        from llm_router.router import route_chat_json
    except ImportError:
        return None

    schema_hint = ""
    if SCHEMA_PATH.is_file():
        schema_hint = SCHEMA_PATH.read_text(encoding="utf-8")[:8000]

    prompt_path = Path(__file__).parent / "prompts" / "generate_tool_json.md"
    system = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else (
        "Gere um JSON completo de calculadora/escala clínica de enfermagem "
        "seguindo tool.schema.json. Retorne apenas o objeto JSON."
    )

    user = json.dumps(
        {
            "slug": slug,
            "name": name,
            "description": description,
            "category": category,
            "schema_excerpt": schema_hint,
        },
        ensure_ascii=False,
        indent=2,
    )

    result = route_chat_json(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        task="bulk_content",
        temperature=0.3,
        max_tokens=12000,
    )
    parsed = result.get("parsed")
    if isinstance(parsed, dict):
        parsed.setdefault("slug", slug)
        parsed.setdefault("status", "draft")
        return parsed
    return None


def generate_html_from_json(
    json_path: Path,
    output_path: Path,
) -> None:
    if not GENERATOR.is_file():
        raise FileNotFoundError(f"Gerador não encontrado: {GENERATOR}")

    proc = subprocess.run(
        [sys.executable, str(GENERATOR), str(json_path)],
        capture_output=True,
        text=True,
        cwd=str(REF_WEBSITE),
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "generate_tool_page falhou")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(proc.stdout, encoding="utf-8")


def run_generation(
    slug: str,
    *,
    name: str | None = None,
    description: str | None = None,
    use_llm: bool = False,
    output_root: Path | None = None,
    draft_json: bool = False,
) -> GenerationReport:
    load_env()
    output_root = output_root or DELIVERY_HTML
    report = GenerationReport(slug=slug)
    json_path = TOOLS_JSON / f"{slug}.json"

    if draft_json or (use_llm and not json_path.is_file()):
        if not use_llm or not llm_enabled():
            report.add("erro: --llm requer DEEPSEEK_API_KEY")
            return report
        draft = _llm_draft_tool_json(
            slug=slug,
            name=name or slug.replace("-", " ").title(),
            description=description or f"Calculadora/escala clínica: {slug}",
        )
        if not draft:
            report.add("erro: LLM não retornou JSON válido")
            return report
        TOOLS_JSON.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
        report.json_path = str(json_path)
        report.llm_used = True
        report.add("json_gerado_via_llm")

    if not json_path.is_file():
        report.add(f"erro: JSON não encontrado em {json_path}")
        return report

    report.json_path = str(json_path)
    out = output_root / f"{slug}.html"
    generate_html_from_json(json_path, out)
    report.output_path = str(out)
    report.add("html_gerado_via_generate_tool_page")
    return report
