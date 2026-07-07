"""Agente de correção — sincroniza JSON, estrutura HTML e revisão clínica via LLM."""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .env import REF_SCRIPTS, load_env, llm_enabled
from .validate import TOOL_CONFIG_RX, ValidationReport, run_validation

WORKSPACE = Path(__file__).resolve().parents[2]
DELIVERY_HTML = WORKSPACE / "NIFS" / "DELIVERY"
TOOLS_JSON = WORKSPACE / "reference-website" / "data" / "tools"


@dataclass
class CorrectionAction:
    slug: str
    action: str
    detail: str


@dataclass
class CorrectionReport:
    slug: str
    actions: list[CorrectionAction] = field(default_factory=list)
    llm_used: bool = False

    def add(self, action: str, detail: str) -> None:
        self.actions.append(CorrectionAction(self.slug, action, detail))

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "llm_used": self.llm_used,
            "actions": [{"action": a.action, "detail": a.detail} for a in self.actions],
        }


def _sync_embed_from_json(html_path: Path, source: dict, report: CorrectionReport) -> bool:
    content = html_path.read_text(encoding="utf-8")
    m = TOOL_CONFIG_RX.search(content)
    if not m:
        return False
    try:
        embedded = json.loads(m.group(1))
    except json.JSONDecodeError:
        embedded = None
    if embedded == source:
        return False

    new_block = (
        '<script type="application/json" id="tool-config">'
        + json.dumps(source, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )
    new_content = content[: m.start()] + new_block + content[m.end() :]
    html_path.write_text(new_content, encoding="utf-8")
    report.add("sync_tool_config", "tool-config sincronizado com data/tools/")
    return True


def _normalize_footer(html_path: Path, report: CorrectionReport) -> bool:
    content = html_path.read_text(encoding="utf-8")
    if 'src="js/partials-loader.js"' not in content:
        return False

    body_end = content.rfind("</body>")
    if body_end < 0:
        return False

    before = content[:body_end]
    footer_idx = before.rfind('<div id="site-cookie"></div>')
    if footer_idx < 0:
        return False

    # Preserva scripts inline customizados (ex.: apgar)
    inline_scripts = []
    for m in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>.*?</script>", before, re.DOTALL):
        block = m.group(0)
        if 'id="tool-config"' in block:
            continue
        if any(x in block for x in ("partials-loader", "calc-engine", "nurse-palm", "cognitive-ui")):
            continue
        inline_scripts.append(block)

    prefix = before[: footer_idx + len('<div id="site-cookie"></div>')]
    tail = '\n\n<script src="js/partials-loader.js"></script>\n'
    for script in inline_scripts:
        tail += "\n" + script + "\n"
    new_content = prefix + tail + content[body_end:]
    if new_content == content:
        return False

    html_path.write_text(new_content, encoding="utf-8")
    report.add("normalize_footer", "Footer padronizado (apenas partials-loader)")
    return True


def _llm_review_tool_config(cfg: dict, slug: str) -> dict | None:
    if REF_SCRIPTS.is_dir() and str(REF_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(REF_SCRIPTS))
    try:
        from llm_router.router import route_chat_json
    except ImportError:
        return None

    prompt_path = Path(__file__).parent / "prompts" / "review_tool_config.md"
    system = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else (
        "Revise o JSON de calculadora clínica. Retorne JSON com: "
        '{"issues":[],"suggestions":[],"severity":"ok|warning|critical"}'
    )

    user = json.dumps(
        {"slug": slug, "tool_config": cfg},
        ensure_ascii=False,
        indent=2,
    )

    try:
        result = route_chat_json(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            task="clinical_decision_content",
            temperature=0.1,
            max_tokens=4096,
        )
        return result.get("parsed")
    except Exception as exc:
        return {"error": str(exc)}


def run_correction(
    slug: str,
    *,
    root: Path | None = None,
    use_llm: bool = False,
    sync_json: bool = True,
    normalize_footer: bool = True,
) -> CorrectionReport:
    load_env()
    root = root or DELIVERY_HTML
    html_path = root / f"{slug}.html"
    report = CorrectionReport(slug=slug)

    if not html_path.is_file():
        report.add("error", f"Arquivo não encontrado: {html_path}")
        return report

    if sync_json and TOOLS_JSON.is_dir():
        json_path = TOOLS_JSON / f"{slug}.json"
        if json_path.is_file():
            source = json.loads(json_path.read_text(encoding="utf-8"))
            _sync_embed_from_json(html_path, source, report)

    if normalize_footer:
        _normalize_footer(html_path, report)

    if use_llm and llm_enabled():
        m = TOOL_CONFIG_RX.search(html_path.read_text(encoding="utf-8"))
        if m:
            try:
                cfg = json.loads(m.group(1))
                review = _llm_review_tool_config(cfg, slug)
                report.llm_used = True
                if review:
                    report.add("llm_review", json.dumps(review, ensure_ascii=False)[:500])
            except json.JSONDecodeError:
                report.add("llm_skipped", "tool-config inválido para revisão LLM")

    return report
