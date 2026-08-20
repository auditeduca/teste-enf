"""Generate static HTML pages from tool JSON."""

from __future__ import annotations

import json
from pathlib import Path

from .html import attr, dumps_json, esc
from .paths import TOOLS_DIR, WEB_DIR
from .score import compute, format_result, interpret
from .validate import iter_tool_files, load_tool


def _options_html(inp: dict) -> str:
    current = inp.get("defaultValue", "")
    parts: list[str] = []
    for opt in inp.get("options") or []:
        selected = " selected" if str(opt.get("value")) == str(current) else ""
        label = esc(opt.get("label"))
        desc = opt.get("description")
        title = f' title="{attr(desc)}"' if desc else ""
        parts.append(f'<option value="{attr(opt.get("value"))}"{title}{selected}>{label}</option>')
    return "\n              ".join(parts)


def _input_html(inp: dict) -> str:
    inp_id = attr(inp["id"])
    label = esc(inp.get("label"))
    description = esc(inp.get("description") or "")
    unit = inp.get("unit")
    unit_html = f'<span class="field-unit">{esc(unit)}</span>' if unit else ""
    if inp.get("type") == "select":
        control = f"""<select id="input-{inp_id}" name="{inp_id}" data-calc-input="{inp_id}">
              {_options_html(inp)}
            </select>"""
    else:
        extras = []
        for key in ("min", "max", "step"):
            if inp.get(key) is not None:
                extras.append(f'{key}="{attr(inp[key])}"')
        extra = (" " + " ".join(extras)) if extras else ""
        control = (
            f'<input id="input-{inp_id}" name="{inp_id}" type="number" '
            f'data-calc-input="{inp_id}" value="{attr(inp.get("defaultValue", ""))}"{extra}>'
        )
    return f"""
          <label class="field">
            <span class="field-label">{label}{unit_html}</span>
            <span class="field-help">{description}</span>
            {control}
          </label>"""


def _list_html(items: list[str], class_name: str = "") -> str:
    cls = f' class="{class_name}"' if class_name else ""
    lis = "\n".join(f"<li>{esc(item)}</li>" for item in items)
    return f"<ul{cls}>{lis}</ul>"


def _sae_html(tool: dict) -> str:
    sae = tool.get("sae") or {}
    nanda = sae.get("nanda") or []
    noc = sae.get("noc") or []
    nic = sae.get("nic") or []
    if not (nanda or noc or nic):
        return ""

    def cards(title: str, rows: list[dict], heading_key: str, extra_key: str, extra_is_list: bool) -> str:
        blocks = []
        for row in rows:
            extra = row.get(extra_key)
            if extra_is_list and extra:
                extra_html = _list_html(extra)
            else:
                extra_html = f"<p>{esc(extra)}</p>" if extra else ""
            blocks.append(f"<article><h4>{esc(row.get(heading_key))}</h4>{extra_html}</article>")
        return f'<section class="sae-col"><h3>{esc(title)}</h3>{"".join(blocks)}</section>'

    return f"""
      <section class="clinical-step" id="step-sae" hidden>
        <h2>Raciocínio NANDA · NIC · NOC</h2>
        <div class="sae-grid">
          {cards("NANDA", nanda, "diagnosis", "definition", False)}
          {cards("NIC", nic, "intervention", "activities", True)}
          {cards("NOC", noc, "outcome", "indicators", True)}
        </div>
      </section>"""


def _recommendations_html(range_item: dict | None) -> str:
    if not range_item:
        return ""
    recs = (range_item.get("recommendations") or "").split("\n")
    recs = [line.lstrip("• ").strip() for line in recs if line.strip()]
    if not recs:
        return ""
    return f"""
      <section class="clinical-step" id="step-plan" hidden>
        <h2>Plano de ação</h2>
        {_list_html(recs, "action-list")}
      </section>"""


def _about_html(tool: dict) -> str:
    about = tool.get("about") or {}
    faq = tool.get("faq") or []
    evidence = tool.get("evidence") or {}
    learning = tool.get("learning") or {}
    tips = learning.get("tips") or []
    quiz = learning.get("quiz") or []
    refs = evidence.get("references") or []
    examples = learning.get("examples") or []

    faq_html = ""
    if faq:
        items = []
        for item in faq:
            items.append(
                f"<details><summary>{esc(item.get('q'))}</summary><p>{esc(item.get('a'))}</p></details>"
            )
        faq_html = f'<section class="panel"><h2>Perguntas frequentes</h2>{"".join(items)}</section>'

    tips_html = f'<section class="panel"><h2>Dicas clínicas</h2>{_list_html(tips)}</section>' if tips else ""
    refs_html = (
        f'<section class="panel"><h2>Referências</h2>{_list_html([r.get("text", "") for r in refs])}</section>'
        if refs
        else ""
    )

    quiz_html = ""
    if quiz:
        cards = []
        for index, item in enumerate(quiz):
            opts = []
            for opt_i, opt in enumerate(item.get("opts") or []):
                opts.append(
                    f'<button type="button" class="quiz-opt" data-quiz="{index}" data-opt="{opt_i}">{esc(opt)}</button>'
                )
            cards.append(
                f"""<article class="quiz-card" data-quiz-card="{index}" data-correct="{attr(item.get('correct'))}">
            <p class="quiz-q">{esc(item.get('q'))}</p>
            <div class="quiz-opts">{"".join(opts)}</div>
            <p class="quiz-expl" hidden>{esc(item.get('expl'))}</p>
          </article>"""
            )
        quiz_html = f'<section class="panel"><h2>Quiz</h2>{"".join(cards)}</section>'

    examples_html = ""
    if examples:
        buttons = []
        for ex in examples:
            payload = json.dumps(ex.get("values") or {}, ensure_ascii=False)
            buttons.append(
                f'<button type="button" class="example-btn" data-example data-values=\'{attr(payload)}\'>'
                f'{esc(ex.get("emoji", ""))} {esc(ex.get("label"))} — {esc(ex.get("sublabel"))}</button>'
            )
        examples_html = f'<div class="examples">{"".join(buttons)}</div>'

    about_title = esc(about.get("title") or "Sobre esta ferramenta")
    about_body = about.get("html") or ""
    foundation = esc(evidence.get("foundation") or "")
    limitations = esc(evidence.get("limitations") or "")
    extra = ""
    if foundation:
        extra += f"<p>{foundation}</p>"
    if limitations:
        extra += f"<p><strong>Limitações:</strong> {limitations}</p>"

    return f"""
      <section class="panel">
        <h2>{about_title}</h2>
        {about_body}
        {extra}
        {examples_html}
      </section>
      {tips_html}
      {quiz_html}
      {faq_html}
      {refs_html}"""


def generate_tool_page(tool: dict) -> str:
    overview = tool.get("overview") or {}
    formula = tool["calculator"]["formula"]
    default_total = compute(tool)
    default_range = interpret(tool, default_total)
    result_str = format_result(tool, default_total)
    range_label = esc((default_range or {}).get("label") or "")
    range_color = attr((default_range or {}).get("color") or "#0f766e")
    implications = esc((default_range or {}).get("clinicalImplications") or "")
    fields = "\n".join(_input_html(inp) for inp in tool["calculator"]["inputs"])
    specialties = " · ".join(overview.get("specialty") or [])
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc((tool.get("seo") or {}).get("title") or overview.get("name"))}</title>
  <meta name="description" content="{attr((tool.get("seo") or {}).get("description") or overview.get("objective"))}">
  <link rel="canonical" href="{attr((tool.get("seo") or {}).get("canonical") or "")}">
  <link rel="stylesheet" href="../css/app.css">
</head>
<body>
  <a class="skip-link" href="#conteudo">Ir para o conteúdo</a>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="../index.html">NIS</a>
      <p class="brand-sub">Nursing Intelligence System</p>
    </div>
  </header>
  <main id="conteudo" class="wrap tool-page">
    <nav class="breadcrumb" aria-label="Trilha">
      <a href="../index.html">Calculadoras</a>
      <span aria-hidden="true">/</span>
      <span>{esc((tool.get("breadcrumb") or {}).get("category") or "Ferramenta")}</span>
    </nav>
    <header class="tool-hero">
      <p class="eyebrow">{esc(overview.get("categoryBadge") or "")}</p>
      <h1>{esc(overview.get("name"))}</h1>
      <p class="lede">{esc(overview.get("objective"))}</p>
      <p class="meta">{esc(specialties)}{(" · " + esc(overview.get("averageTime"))) if overview.get("averageTime") else ""}</p>
    </header>
    <form id="calcForm" class="calc-card">
      <input type="hidden" name="slug" value="{attr(tool.get("slug"))}">
      <fieldset>
        <legend>1. Avaliação</legend>
        <p class="hint">{esc(overview.get("indication") or "")}</p>
        {fields}
      </fieldset>
      <div class="result-block" id="resultBlock" style="--risk:{range_color}">
        <p class="result-kicker">{esc(formula.get("resultLabel") or "Resultado")}</p>
        <p class="result-value"><span id="calcResultValue">{esc(result_str)}</span>
          <span id="calcResultUnit" class="result-unit">{esc(formula.get("resultUnit") or "")}</span></p>
        <p id="calcStatusTitle" class="result-label">{range_label}</p>
        <p id="calcStatusText" class="result-note">{implications}</p>
      </div>
      <p class="actions">
        <button type="submit" class="btn-primary" id="calcSubmit">Calcular e ver raciocínio</button>
      </p>
    </form>
    {_sae_html(tool)}
    {_recommendations_html(default_range)}
    {_about_html(tool)}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p>Protótipo greenfield do NIS. Conteúdo clínico de apoio — não substitui julgamento profissional.</p>
    </div>
  </footer>
  <script type="application/json" id="tool-config">{dumps_json(tool)}</script>
  <script src="../js/calc-engine.js"></script>
</body>
</html>
"""


def generate_index(tools: list[dict]) -> str:
    cards = []
    for tool in tools:
        overview = tool.get("overview") or {}
        cards.append(
            f"""<a class="tool-card" href="tools/{attr(tool["slug"])}.html">
        <p class="eyebrow">{esc(overview.get("categoryBadge") or "")}</p>
        <h2>{esc(overview.get("name"))}</h2>
        <p>{esc(overview.get("objective"))}</p>
      </a>"""
        )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NIS — Calculadoras de Enfermagem</title>
  <meta name="description" content="Nursing Intelligence System. Calculadoras clínicas geradas a partir de JSON canônico.">
  <link rel="stylesheet" href="css/app.css">
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="index.html">NIS</a>
      <p class="brand-sub">Nursing Intelligence System</p>
    </div>
  </header>
  <main class="wrap">
    <header class="page-hero">
      <p class="eyebrow">Repositório greenfield</p>
      <h1>Calculadoras de enfermagem, a partir da especificação.</h1>
      <p class="lede">JSON canônico → motor de pontuação → HTML estático. Primeira entrega: Apgar e IMC.</p>
    </header>
    <section class="catalog" aria-label="Ferramentas">
      {"".join(cards)}
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap"><p>Audit Educa · calculadorasdeenfermagem.com.br</p></div>
  </footer>
</body>
</html>
"""


def build(tools_dir: Path | None = None, web_dir: Path | None = None) -> list[Path]:
    tools_dir = tools_dir or TOOLS_DIR
    web_dir = web_dir or WEB_DIR
    out_dir = web_dir / "tools"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    tools: list[dict] = []
    for path in iter_tool_files(tools_dir):
        tool = load_tool(path)
        tools.append(tool)
        dest = out_dir / f"{tool['slug']}.html"
        dest.write_text(generate_tool_page(tool), encoding="utf-8")
        written.append(dest)
    index = web_dir / "index.html"
    index.write_text(generate_index(tools), encoding="utf-8")
    written.append(index)
    return written
