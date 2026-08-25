"""Generate fetch and inline HTML from canonical JSON."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from .bootstrap import layer_records, write_registries
from .html import attr, dumps_json, esc
from .paths import (
    ADMIN_DIR,
    ASSETS_DIR,
    FETCH_DIR,
    INLINE_DIR,
    LAYER_REGISTRY_PATH,
    PUBLIC_DIR,
    ROOT,
    TEMPLATES_DIR,
    TOOLS_DIR,
)
from .score import compute, format_result, interpret
from .validate import iter_tool_files, load_tool

SITE_NAME = "CKO"
SITE_SUB = "Calculadoras de Enfermagem"
DISCLAIMER = (
    "Apoio à decisão clínica e ao estudo. Não substitui julgamento profissional, "
    "protocolo institucional nem prescrição."
)


def _read_css() -> str:
    return (ASSETS_DIR / "css" / "app.css").read_text(encoding="utf-8")


def _shell(title: str, description: str, body: str, *, css_href: str | None, css_inline: str | None, extra_head: str = "", scripts: str = "") -> str:
    if css_inline:
        style = f"<style>\n{_read_css() if css_inline == 'file' else css_inline}\n</style>"
    else:
        style = f'<link rel="stylesheet" href="{attr(css_href)}">'
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{attr(description)}">
  <meta name="theme-color" content="#1A3E74">
  {style}
  {extra_head}
</head>
<body>
  <a class="skip-link" href="#conteudo">Ir para o conteúdo</a>
  {body}
  {scripts}
</body>
</html>
"""


def _header_footer(home_href: str) -> tuple[str, str]:
    header = f"""<header class="site-header">
    <div class="wrap header-row">
      <div>
        <a class="brand" href="{attr(home_href)}">{SITE_NAME}</a>
        <p class="brand-sub">{SITE_SUB}</p>
      </div>
      <nav class="nav" aria-label="Principal">
        <a href="{attr(home_href)}">Início</a>
        <a href="{attr(home_href.replace('index.html', 'inspector.html') if home_href.endswith('index.html') else 'inspector.html')}">Inspector</a>
        <a href="{attr(home_href.replace('index.html', 'admin.html') if home_href.endswith('index.html') else 'admin.html')}">Admin</a>
      </nav>
    </div>
  </header>"""
    footer = f"""<footer class="site-footer">
    <div class="wrap">
      <p>{esc(DISCLAIMER)}</p>
      <p>Audit Educa · CKO · Constituição CKO-INS-AI-PROJECT-001</p>
    </div>
  </footer>"""
    return header, footer


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


def _list_html(items: list, class_name: str = "") -> str:
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
    hold = sae.get("status") == "HOLD"
    banner = (
        '<p class="hold-banner">SAE em HOLD: códigos NIC/NOC são candidatos internos até fonte canônica/licenciada.</p>'
        if hold
        else ""
    )

    def cards(title: str, rows: list[dict], heading_key: str, extra_key: str, extra_is_list: bool) -> str:
        blocks = []
        for row in rows:
            extra = row.get(extra_key)
            if extra_is_list and extra:
                extra_html = _list_html(extra)
            else:
                extra_html = f"<p>{esc(extra)}</p>" if extra else ""
            code = f'<p class="code">{esc(row.get("code"))}</p>' if row.get("code") else ""
            blocks.append(f"<article>{code}<h4>{esc(row.get(heading_key))}</h4>{extra_html}</article>")
        return f'<section class="sae-col"><h3>{esc(title)}</h3>{"".join(blocks)}</section>'

    return f"""
      <section class="clinical-step" id="step-sae" hidden>
        <h2>Raciocínio NANDA · NIC · NOC</h2>
        {banner}
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


def _quiz_html(quiz: list) -> str:
    if not quiz:
        return ""
    cards = []
    for index, item in enumerate(quiz):
        opts = []
        for opt_i, opt in enumerate(item.get("opts") or []):
            opts.append(
                f'<button type="button" class="quiz-opt" data-opt="{opt_i}">{esc(opt)}</button>'
            )
        cards.append(
            f"""<article class="quiz-card" data-quiz-card="{index}" data-correct="{attr(item.get('correct'))}">
            <p class="quiz-q">{esc(item.get('q'))}</p>
            <div class="quiz-opts">{"".join(opts)}</div>
            <p class="quiz-expl" hidden>{esc(item.get('expl'))}</p>
          </article>"""
        )
    return f'<section class="panel"><h2>Questões</h2>{"".join(cards)}</section>'


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
    examples_html = ""
    if examples:
        buttons = []
        for ex in examples:
            payload = json.dumps(ex.get("values") or {}, ensure_ascii=False)
            buttons.append(
                f'<button type="button" class="example-btn" data-example data-values="{attr(payload)}">'
                f'{esc(ex.get("emoji", ""))} {esc(ex.get("label"))} — {esc(ex.get("sublabel"))}</button>'
            )
        examples_html = f'<div class="examples">{"".join(buttons)}</div>'

    about_title = esc(about.get("title") or "Sobre este objeto")
    about_body = about.get("html") or ""
    foundation = esc(evidence.get("foundation") or "")
    limitations = esc(evidence.get("limitations") or "")
    extra = ""
    if foundation:
        extra += f"<p>{foundation}</p>"
    if limitations:
        extra += f"<p><strong>Limitações:</strong> {limitations}</p>"
    content_html = _content_sections(tool)

    return f"""
      {content_html}
      <section class="panel">
        <h2>{about_title}</h2>
        {about_body}
        {extra}
        {examples_html}
      </section>
      {tips_html}
      {_quiz_html(quiz)}
      {faq_html}
      {refs_html}"""


def _content_sections(tool: dict) -> str:
    sections = (tool.get("content") or {}).get("sections") or []
    if not sections:
        return ""
    blocks = []
    for section in sections:
        items = section.get("items") or []
        items_html = ""
        if items:
            cards = []
            for item in items:
                cards.append(
                    f"""<article class="content-card">
            <p class="eyebrow">{esc(item.get("kicker") or "")}</p>
            <h3>{esc(item.get("title"))}</h3>
            <p>{esc(item.get("body"))}</p>
          </article>"""
                )
            items_html = f'<div class="catalog">{"".join(cards)}</div>'
        body = section.get("html") or (f"<p>{esc(section.get('body'))}</p>" if section.get("body") else "")
        blocks.append(f'<section class="panel"><h2>{esc(section.get("title"))}</h2>{body}{items_html}</section>')
    return "\n".join(blocks)


def _hold_banner(tool: dict) -> str:
    if tool.get("status") != "hold":
        return ""
    reason = esc((tool.get("hold") or {}).get("reason") or "Objeto em HOLD até evidência e aprovação.")
    return f'<p class="hold-banner" role="status">{reason}</p>'


def generate_tool_page(tool: dict, *, css_href: str, script_href: str, home_href: str, inline_css: bool) -> str:
    overview = tool.get("overview") or {}
    kind = tool.get("kind") or "calculator"
    header, footer = _header_footer(home_href)
    specialties = " · ".join(overview.get("specialty") or [])
    form_html = ""
    if kind in {"calculator", "scale"} and tool.get("calculator"):
        formula = tool["calculator"]["formula"]
        default_total = compute(tool)
        default_range = interpret(tool, default_total)
        result_str = format_result(tool, default_total)
        range_label = esc((default_range or {}).get("label") or "")
        range_color = attr((default_range or {}).get("color") or "#1A3E74")
        implications = esc((default_range or {}).get("clinicalImplications") or "")
        fields = "\n".join(_input_html(inp) for inp in tool["calculator"]["inputs"])
        form_html = f"""
    <form id="calcForm" class="calc-card">
      <input type="hidden" name="slug" value="{attr(tool.get("slug"))}">
      <fieldset>
        <legend>Avaliação</legend>
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
    {_recommendations_html(default_range)}"""

    body = f"""{header}
  <main id="conteudo" class="wrap tool-page">
    <nav class="breadcrumb" aria-label="Trilha">
      <a href="{attr(home_href)}">Início</a>
      <span aria-hidden="true">/</span>
      <span>{esc((tool.get("breadcrumb") or {}).get("category") or "Objeto")}</span>
    </nav>
    {_hold_banner(tool)}
    <header class="tool-hero">
      <p class="eyebrow">{esc(overview.get("categoryBadge") or kind)}</p>
      <h1>{esc(overview.get("name"))}</h1>
      <p class="lede">{esc(overview.get("objective"))}</p>
      <p class="meta">{esc(specialties)}</p>
    </header>
    {form_html}
    {_about_html(tool)}
  </main>
  {footer}"""
    scripts = ""
    if kind in {"calculator", "scale", "exam"} or (tool.get("learning") or {}).get("quiz"):
        scripts = (
            f'<script type="application/json" id="tool-config">{dumps_json(tool)}</script>\n'
            f'<script src="{attr(script_href)}"></script>'
        )
        if inline_css:
            js = (ASSETS_DIR / "js" / "calc-engine.js").read_text(encoding="utf-8")
            scripts = (
                f'<script type="application/json" id="tool-config">{dumps_json(tool)}</script>\n'
                f"<script>\n{js}\n</script>"
            )
    title = (tool.get("seo") or {}).get("title") or overview.get("name") or SITE_NAME
    description = (tool.get("seo") or {}).get("description") or overview.get("objective") or SITE_SUB
    return _shell(
        str(title),
        str(description),
        body,
        css_href=None if inline_css else css_href,
        css_inline="file" if inline_css else None,
        scripts=scripts,
    )


def generate_index(tools: list[dict], *, css_href: str, home_href: str, inline_css: bool, inspector_href: str) -> str:
    cards = []
    for tool in tools:
        overview = tool.get("overview") or {}
        status = tool.get("status") or "draft"
        cards.append(
            f"""<a class="tool-card" href="tools/{attr(tool["slug"])}.html">
        <p class="eyebrow">{esc(overview.get("categoryBadge") or tool.get("kind"))} · {esc(status)}</p>
        <h2>{esc(overview.get("name"))}</h2>
        <p>{esc(overview.get("objective"))}</p>
      </a>"""
        )
    header, footer = _header_footer(home_href)
    body = f"""{header}
  <main id="conteudo" class="wrap">
    <header class="page-hero">
      <p class="eyebrow">Constituição CKO-INS-AI-PROJECT-001 · lote piloto</p>
      <h1>Conhecimento canônico, projetado em HTML.</h1>
      <p class="lede">CKO-MD e CKO-REG nascem no GitHub. Cinco objetos piloto são candidatos de domínio, não golden records. Admin e frontend leem os mesmos contratos.</p>
      <p class="meta"><a href="admin.html">Abrir Admin</a> · <a href="{attr(inspector_href)}">Abrir Inspector</a></p>
    </header>
    <section class="catalog" aria-label="Pilotos">
      {"".join(cards)}
    </section>
    <section class="panel">
      <h2>Como este aplicativo funciona</h2>
      <p>Registries Day Zero vivem em <code>cko_core</code>, <code>cko_md</code>, <code>cko_reg</code> e <code>cko_assurance</code>. Candidatos de domínio vivem em <code>data/tools</code>. O motor valida o contrato, calcula quando há fórmula, e gera duas projeções HTML semanticamente equivalentes: preview inline e produção fetch, ambas first-party, sem CDN.</p>
      <p>O Admin não grava fórmula. O frontend não grava objeto canônico.</p>
    </section>
  </main>
  {footer}"""
    return _shell(
        f"{SITE_NAME} — {SITE_SUB}",
        "Engine canônico de calculadoras, escalas, guias e simulados de enfermagem.",
        body,
        css_href=None if inline_css else css_href,
        css_inline="file" if inline_css else None,
    )


def generate_inspector(tools: list[dict], completeness: dict, *, css_href: str, home_href: str, inline_css: bool) -> str:
    rows = []
    for tool in tools:
        overview = tool.get("overview") or {}
        rows.append(
            f"<tr><td><a href=\"tools/{attr(tool['slug'])}.html\">{esc(tool.get('slug'))}</a></td>"
            f"<td>{esc(tool.get('kind'))}</td><td>{esc(tool.get('status'))}</td>"
            f"<td>{esc(overview.get('name'))}</td></tr>"
        )
    findings = completeness.get("blockingFindings") or []
    finding_items = "".join(f"<li>{esc(item.get('id'))}: {esc(item.get('reason', item.get('id')))}</li>" for item in findings) or "<li>Nenhum achado estrutural de schema.</li>"
    header, footer = _header_footer(home_href)
    body = f"""{header}
  <main id="conteudo" class="wrap">
    <header class="page-hero">
      <p class="eyebrow">Inspector de candidatos</p>
      <h1>Inspeção read-only do catálogo piloto.</h1>
      <p class="lede">Este inspector não edita objetos e não é o Layer Registry. Completude clínica do lote: <strong>{esc(completeness.get('status'))}</strong>. Governança das 44 camadas está em <a href="admin.html">Admin</a>.</p>
    </header>
    <section class="panel">
      <h2>Objetos</h2>
      <table class="inspect">
        <thead><tr><th>Slug</th><th>Tipo</th><th>Status</th><th>Nome</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </section>
    <section class="panel">
      <h2>Achados de completude</h2>
      <ul>{finding_items}</ul>
    </section>
  </main>
  {footer}"""
    return _shell(
        "Inspector — CKO",
        "Inspeção read-only do catálogo canônico.",
        body,
        css_href=None if inline_css else css_href,
        css_inline="file" if inline_css else None,
    )


def generate_admin(
    tools: list[dict],
    completeness: dict,
    layers: list[dict],
    contract: dict,
    *,
    css_href: str,
    home_href: str,
    inline_css: bool,
) -> str:
    layer_rows = []
    for layer in layers:
        layer_rows.append(
            "<tr>"
            f"<td>{esc(layer.get('layer_code'))}</td>"
            f"<td>{esc(layer.get('canonical_name'))}</td>"
            f"<td>{esc(layer.get('maturity'))}</td>"
            f"<td>{esc(layer.get('md_profile_ref'))}</td>"
            f"<td>{esc(layer.get('reg_profile_ref'))}</td>"
            "</tr>"
        )
    tool_rows = []
    for tool in tools:
        overview = tool.get("overview") or {}
        tool_rows.append(
            "<tr>"
            f"<td><a href=\"tools/{attr(tool['slug'])}.html\">{esc(tool.get('slug'))}</a></td>"
            f"<td>{esc(overview.get('name'))}</td>"
            f"<td>{esc(tool.get('status'))}</td>"
            f"<td>{esc(tool.get('kind'))}</td>"
            "</tr>"
        )
    comm = contract.get("communication") or {}
    header, footer = _header_footer(home_href)
    body = f"""{header}
  <main id="conteudo" class="wrap wrap-wide">
    <header class="page-hero">
      <p class="eyebrow">Admin · GitHub Day Zero</p>
      <h1>Projeção dos contratos governados.</h1>
      <p class="lede">Admin e frontend compartilham os mesmos JSON. Esta página não grava verdade clínica. Store: {esc(contract.get("store"))}</p>
      <p class="hold-banner" role="status">Modo {esc(comm.get("mode") or "SHARED_GITHUB_CONTRACTS")} · UUID HOLD · Clinical completeness {esc(completeness.get("status"))}</p>
    </header>
    <section class="panel">
      <h2>Contrato admin ↔ frontend</h2>
      <ul>
        <li>Admin: {esc((contract.get("admin") or {}).get("role"))}</li>
        <li>Frontend: {esc((contract.get("frontend") or {}).get("role"))}</li>
        <li>Privacidade: {esc(contract.get("privacy"))}</li>
        <li>Segregação: {esc(contract.get("segregation"))}</li>
        <li>JSON projetado: <code>admin/contract.json</code> e <code>admin/layer_registry.json</code></li>
      </ul>
    </section>
    <section class="panel">
      <h2>Candidatos de domínio ({len(tools)})</h2>
      <div class="table-wrap">
        <table class="inspect">
          <thead><tr><th>slug</th><th>nome</th><th>status</th><th>kind</th></tr></thead>
          <tbody>{"".join(tool_rows)}</tbody>
        </table>
      </div>
    </section>
    <section class="panel">
      <h2>Layer Registry ({len(layers)})</h2>
      <p>EXISTS ≠ POPULATED ≠ IMPLEMENTED ≠ ASSURED. Maturidade inicial: M0_REGISTERED.</p>
      <div class="table-wrap">
        <table class="inspect">
          <thead><tr><th>code</th><th>nome</th><th>maturidade</th><th>MD profile</th><th>REG profile</th></tr></thead>
          <tbody>{"".join(layer_rows)}</tbody>
        </table>
      </div>
    </section>
  </main>
  {footer}"""
    extra_head = f'<script type="application/json" id="admin-contract">{dumps_json(contract)}</script>'
    return _shell(
        "Admin — CKO",
        "Superfície administrativa read-only sobre registries GitHub.",
        body,
        css_href=None if inline_css else css_href,
        css_inline="file" if inline_css else None,
        extra_head=extra_head,
    )


def _emit_tree(dest: Path, tools: list[dict], *, inline_css: bool) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "tools").mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    if not inline_css:
        assets = dest / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ASSETS_DIR / "css" / "app.css", assets / "app.css")
        shutil.copy2(ASSETS_DIR / "js" / "calc-engine.js", assets / "calc-engine.js")
        written.extend([assets / "app.css", assets / "calc-engine.js"])
        css_href = "assets/app.css"
        page_css = "../assets/app.css"
        script_href = "../assets/calc-engine.js"
        home_from_tool = "../index.html"
        inspector_from_home = "inspector.html"
        home_from_home = "index.html"
    else:
        css_href = ""
        page_css = ""
        script_href = ""
        home_from_tool = "../index.html"
        inspector_from_home = "inspector.html"
        home_from_home = "index.html"

    from validators.clinical_completeness import evaluate_catalog

    completeness = evaluate_catalog()
    for tool in tools:
        page = generate_tool_page(
            tool,
            css_href=page_css,
            script_href=script_href,
            home_href=home_from_tool,
            inline_css=inline_css,
        )
        out = dest / "tools" / f"{tool['slug']}.html"
        out.write_text(page, encoding="utf-8")
        written.append(out)

    index = dest / "index.html"
    index.write_text(
        generate_index(
            tools,
            css_href=css_href,
            home_href=home_from_home,
            inline_css=inline_css,
            inspector_href=inspector_from_home,
        ),
        encoding="utf-8",
    )
    written.append(index)
    inspector = dest / "inspector.html"
    inspector.write_text(
        generate_inspector(
            tools,
            completeness,
            css_href=css_href,
            home_href=home_from_home,
            inline_css=inline_css,
        ),
        encoding="utf-8",
    )
    written.append(inspector)

    contract_path = ADMIN_DIR / "contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8")) if contract_path.exists() else {}
    layers = layer_records()
    admin = dest / "admin.html"
    admin.write_text(
        generate_admin(
            tools,
            completeness,
            layers,
            contract,
            css_href=css_href,
            home_href=home_from_home,
            inline_css=inline_css,
        ),
        encoding="utf-8",
    )
    written.append(admin)

    admin_dir = dest / "admin"
    admin_dir.mkdir(parents=True, exist_ok=True)
    if contract_path.exists():
        shutil.copy2(contract_path, admin_dir / "contract.json")
        written.append(admin_dir / "contract.json")
    if LAYER_REGISTRY_PATH.exists():
        shutil.copy2(LAYER_REGISTRY_PATH, admin_dir / "layer_registry.json")
        written.append(admin_dir / "layer_registry.json")
    return written


def build(tools_dir: Path | None = None) -> list[Path]:
    tools_dir = tools_dir or TOOLS_DIR
    written = list(write_registries())
    tools = [load_tool(path) for path in iter_tool_files(tools_dir)]
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    css = _read_css()
    (PUBLIC_DIR / "output.css").write_text(css, encoding="utf-8")
    (TEMPLATES_DIR / "design-tokens.css").write_text(css, encoding="utf-8")
    catalog = {
        "schemaVersion": "1.0.0",
        "application": "cko",
        "objects": [
            {
                "slug": tool.get("slug"),
                "kind": tool.get("kind"),
                "status": tool.get("status"),
                "name": (tool.get("overview") or {}).get("name"),
            }
            for tool in tools
        ],
    }
    (ROOT / "data" / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    written.extend([PUBLIC_DIR / "output.css", ROOT / "data" / "catalog.json"])
    written.extend(_emit_tree(FETCH_DIR, tools, inline_css=False))
    written.extend(_emit_tree(INLINE_DIR, tools, inline_css=True))
    return written
