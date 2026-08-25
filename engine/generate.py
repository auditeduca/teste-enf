"""Generate fetch and inline HTML from canonical JSON."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from .bootstrap import layer_records, write_registries
from .chrome import asset_prefix, ds_a11y_script, ds_header_footer
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

from .og_card import write_default_og_png

SITE_NAME = "CKO"
SITE_SUB = "Calculadoras de Enfermagem"
SITE_ORIGIN = "https://www.calculadorasdeenfermagem.com.br"
OG_IMAGE_ABS = f"{SITE_ORIGIN}/assets/img/og-default.png"


def _read_css() -> str:
    return (ASSETS_DIR / "css" / "app.css").read_text(encoding="utf-8")


def _social_head(*, title: str, description: str, home_href: str) -> str:
    prefix = asset_prefix(home_href)
    rel_img = f"{prefix}assets/img/og-default.png"
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{SITE_ORIGIN}/#organization",
                "name": "Audit Educa",
            },
            {
                "@type": "WebSite",
                "@id": f"{SITE_ORIGIN}/#website",
                "name": "Calculadoras de Enfermagem",
                "url": f"{SITE_ORIGIN}/",
                "inLanguage": "pt-BR",
                "publisher": {"@id": f"{SITE_ORIGIN}/#organization"},
            },
        ],
    }
    return f"""
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Calculadoras de Enfermagem">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:title" content="{attr(title)}">
  <meta property="og:description" content="{attr(description)}">
  <meta property="og:image" content="{attr(OG_IMAGE_ABS)}">
  <meta property="og:image:alt" content="Calculadoras de Enfermagem">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{attr(title)}">
  <meta name="twitter:description" content="{attr(description)}">
  <meta name="twitter:image" content="{attr(OG_IMAGE_ABS)}">
  <link rel="image_src" href="{attr(rel_img)}">
  <script type="application/ld+json">{dumps_json(graph)}</script>"""


def _shell(
    title: str,
    description: str,
    body: str,
    *,
    css_href: str | None,
    css_inline: str | None,
    extra_head: str = "",
    scripts: str = "",
    home_href: str = "index.html",
    social: bool = True,
) -> str:
    if css_inline:
        style = f"<style>\n{_read_css() if css_inline == 'file' else css_inline}\n</style>"
    else:
        style = f'<link rel="stylesheet" href="{attr(css_href)}">'
    a11y = ds_a11y_script(inline=bool(css_inline), prefix=asset_prefix(home_href))
    combined = "\n".join(part for part in (scripts, a11y) if part)
    social_head = _social_head(title=title, description=description, home_href=home_href) if social else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{attr(description)}">
  <meta name="theme-color" content="#1A3E74">
  {social_head}
  {style}
  {extra_head}
</head>
<body>
  <a class="skip-link" href="#conteudo" accesskey="C">Ir para o conteúdo</a>
  {body}
  {combined}
</body>
</html>
"""


def _header_footer(home_href: str) -> tuple[str, str]:
    return ds_header_footer(home_href)


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


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _lineage_html(tool: dict, *, home_href: str) -> str:
    slug = tool.get("slug")
    lineage = _load_json(ROOT / "cko_md" / "lineage_registry.json")
    works = _load_json(ROOT / "cko_md" / "work_registry.json")
    rights = _load_json(ROOT / "cko_reg" / "rights_profile.json")
    link = next((item for item in (lineage.get("links") or []) if item.get("slug") == slug), {})
    work = next((item for item in (works.get("works") or []) if item.get("slug") == slug), {})
    admin_monitoring = "admin/monitoring.html" if home_href in {"index.html", "./index.html"} else "../admin/monitoring.html"
    inspector = "inspector.html" if home_href in {"index.html", "./index.html"} else "../inspector.html"
    sha = (link.get("md_vault_sha256") or "EVIDENCE_PENDING")[:16]
    origin_sha = (link.get("origin_vault_sha256") or "EVIDENCE_PENDING")[:16]
    return f"""
    <section class="panel lineage-panel" id="rastreio" data-lineage-slug="{attr(slug)}">
      <h2>Rastreio da fonte</h2>
      <p class="hint">Cópia original inalterada no vault → CKO-MD → CKO-REG → esta página. Monitoramento informa drift para ajuste.</p>
      <dl class="lineage-dl">
        <div><dt>Obra</dt><dd>{esc(work.get("work_class") or "UNKNOWN")}</dd></div>
        <div><dt>Direitos</dt><dd>{esc(work.get("rights_status") or rights.get("gate") or "HOLD")} · {esc(work.get("cko_copyright_claim") or "não ASSURED")}</dd></div>
        <div><dt>Instrumento</dt><dd>{esc(link.get("instrument_ref") or "INS-LEI-9610-1998")}</dd></div>
        <div><dt>Máscara</dt><dd>{esc(link.get("mask_id") or "MASK-TOOL-WORK")}</dd></div>
        <div><dt>Vault MD</dt><dd><code>{esc(sha)}</code></dd></div>
        <div><dt>Vault origem</dt><dd><code>{esc(origin_sha)}</code></dd></div>
        <div><dt>URL origem</dt><dd>{esc(link.get("origin_url") or "EVIDENCE_PENDING")}</dd></div>
        <div><dt>Linha</dt><dd>{esc(link.get("status") or "HOLD")}</dd></div>
      </dl>
      <p class="meta"><a href="{attr(inspector)}">Inspector</a> · <a href="{attr(admin_monitoring)}">Monitoramento</a></p>
    </section>"""


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
    {_lineage_html(tool, home_href=home_href)}
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
        home_href=home_href,
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
    inv_path = ROOT / "cko_md" / "page_inventory.json"
    inventory = json.loads(inv_path.read_text(encoding="utf-8")) if inv_path.exists() else {}
    html_count = inventory.get("html_count") or "—"
    unique_stems = inventory.get("unique_stems") or "—"
    locales = json.loads((ROOT / "cko_md" / "locale_registry.json").read_text(encoding="utf-8")) if (ROOT / "cko_md" / "locale_registry.json").exists() else {}
    locale_n = locales.get("population") or "—"
    header, footer = _header_footer(home_href)
    body = f"""{header}
  <main id="conteudo" class="wrap">
    <section class="prod-hero" aria-label="Topo">
      <p class="eyebrow">Plataforma Clínica</p>
      <h1>Calculadoras de Enfermagem</h1>
      <p class="lede">Conhecimento baseado em evidências, escalas, protocolos, calculadoras clínicas e recursos digitais para apoiar a prática da enfermagem.</p>
      <p class="meta"><a href="admin.html">Abrir Admin</a> · <a href="biblioteca.html">Biblioteca de recursos</a> · <a href="{attr(inspector_href)}">Abrir Inspector</a> · <a href="admin/maturity.html">Maturidade</a></p>
    </section>
    <section class="observed-strip" aria-label="Contagens observadas">
      <article><p class="eyebrow">Pilotos CKO</p><h2>{len(tools)}</h2><p>Candidatos em data/tools. Não são golden records.</p></article>
      <article><p class="eyebrow">pages_full.zip</p><h2>{esc(html_count)}</h2><p>HTML SOURCE_DERIVED em quarentena. Não publicados.</p></article>
      <article><p class="eyebrow">Stems únicos</p><h2>{esc(unique_stems)}</h2><p>Inventário extraído. Promoção MD HOLD.</p></article>
      <article><p class="eyebrow">Locales Drive</p><h2>{esc(locale_n)}</h2><p>Códigos observados. Tradução HOLD.</p></article>
    </section>
    <section class="catalog" id="pilotos" aria-label="Pilotos">
      {"".join(cards)}
    </section>
    <section class="panel">
      <h2>Como este aplicativo funciona</h2>
      <p>Registries Day Zero vivem em <code>cko_core</code>, <code>cko_md</code>, <code>cko_reg</code> e <code>cko_assurance</code>. Candidatos de domínio vivem em <code>data/tools</code>. Agentes extraem para <code>cko_inbox</code>; não promovem HTML a ferramenta. O motor valida o contrato e gera duas projeções HTML semanticamente equivalentes, first-party, sem CDN e sem anúncios.</p>
      <p>O Admin não grava fórmula. O frontend não grava objeto canônico. KPIs de produção (+1500 páginas, +5 Mi acessos) permanecem DOCUMENT_CLAIM até IPE.</p>
    </section>
  </main>
  {footer}"""
    return _shell(
        "Calculadoras de Enfermagem, Simulados e Escalas Clínicas",
        "Calculadoras de enfermagem, escalas clínicas e dosagem de medicamentos. Lote piloto CKO com extração em quarentena.",
        body,
        css_href=None if inline_css else css_href,
        css_inline="file" if inline_css else None,
        home_href=home_href,
    )


def generate_inspector(tools: list[dict], completeness: dict, *, css_href: str, home_href: str, inline_css: bool) -> str:
    lineage = _load_json(ROOT / "cko_md" / "lineage_registry.json")
    works = _load_json(ROOT / "cko_md" / "work_registry.json")
    by_slug = {item.get("slug"): item for item in (lineage.get("links") or [])}
    work_by_slug = {item.get("slug"): item for item in (works.get("works") or [])}
    rows = []
    for tool in tools:
        overview = tool.get("overview") or {}
        slug = tool.get("slug")
        link = by_slug.get(slug) or {}
        work = work_by_slug.get(slug) or {}
        rows.append(
            f"<tr><td><a href=\"tools/{attr(slug)}.html\">{esc(slug)}</a></td>"
            f"<td>{esc(tool.get('kind'))}</td><td>{esc(tool.get('status'))}</td>"
            f"<td>{esc(overview.get('name'))}</td>"
            f"<td>{esc(work.get('work_class') or 'UNKNOWN')}</td>"
            f"<td>{esc(link.get('status') or 'HOLD')}</td>"
            f"<td><code>{esc((link.get('md_vault_sha256') or '')[:12] or '—')}</code></td></tr>"
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
        <thead><tr><th>Slug</th><th>Tipo</th><th>Status</th><th>Nome</th><th>Obra</th><th>Lineage</th><th>Vault</th></tr></thead>
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
        home_href=home_href,
    )


def     generate_biblioteca(*, css_href: str, home_href: str, inline_css: bool) -> str:
    lib = _load_json(ROOT / "cko_md" / "resource_library.json")
    curr = _load_json(ROOT / "cko_md" / "content_curriculum.json")
    agencies = _load_json(ROOT / "cko_md" / "agency_registry.json")
    alerts = _load_json(ROOT / "cko_assurance" / "freshness_alerts.json")
    adapters = _load_json(ROOT / "cko_md" / "api_adapter_registry.json")
    laws = _load_json(ROOT / "cko_md" / "legislation_instrument_registry.json")
    links = _load_json(ROOT / "cko_md" / "legislation_tool_links.json")
    types = _load_json(ROOT / "cko_inbox" / "extracted" / "congress_types.json")
    pgd = _load_json(ROOT / "cko_md" / "pgdados_program.json")
    libmap = _load_json(ROOT / "cko_md" / "library_api_map.json")
    concept = _load_json(ROOT / "cko_md" / "concept_renderer.json")
    pages_pend = _load_json(ROOT / "cko_md" / "pages_full_reg_pendencies.json")
    res_rows = []
    for item in lib.get("resources") or []:
        res_rows.append(
            "<tr>"
            f"<td><code>{esc(item.get('business_key'))}</code></td>"
            f"<td>{esc(item.get('title'))}</td>"
            f"<td>{esc(item.get('agency_key'))}</td>"
            f"<td>{esc(item.get('layer'))}</td>"
            f"<td>{esc(item.get('status'))}</td>"
            f"<td><code>{esc(item.get('md_ref'))}</code></td>"
            f"<td><code>{esc(item.get('reg_ref'))}</code></td>"
            "</tr>"
        )
    units_by_tool: dict[str, list] = {}
    for unit in curr.get("units") or []:
        units_by_tool.setdefault(unit.get("tool_slug") or "?", []).append(unit)
    curr_blocks = []
    for slug, units in units_by_tool.items():
        lis = "".join(
            f"<li><strong>{esc(u.get('level'))}</strong> · {esc(u.get('label'))} · "
            f"{esc((u.get('body') or {}).get('status'))} · MD {esc(u.get('tool_md_ref'))} · REG {esc(u.get('reg_ref'))}</li>"
            for u in units
        )
        curr_blocks.append(f"<article class='panel'><h3>{esc(slug)}</h3><ol>{lis}</ol></article>")
    pending = "".join(
        f"<li><strong>{esc(p.get('severity'))}</strong> — {esc(p.get('reason'))}</li>"
        for p in (curr.get("pending_high") or [])
    )
    alert_items = "".join(
        f"<li><strong>{esc(a.get('severity'))}</strong> {esc(a.get('kind'))}: {esc(a.get('message'))}</li>"
        for a in (alerts.get("alerts") or [])[:12]
    )
    api_rows = []
    for item in adapters.get("adapters") or []:
        api_rows.append(
            "<tr>"
            f"<td><code>{esc(item.get('business_key'))}</code></td>"
            f"<td>{esc(item.get('agency'))}</td>"
            f"<td>{esc(item.get('http_status'))}</td>"
            f"<td>{esc(item.get('base_url') or 'null')}</td>"
            f"<td>{esc(item.get('epistemic_status'))}</td>"
            "</tr>"
        )
    law_rows = []
    for item in laws.get("instruments") or []:
        law_rows.append(
            "<tr>"
            f"<td><code>{esc(item.get('business_key'))}</code></td>"
            f"<td>{esc(item.get('title'))}</td>"
            f"<td>{esc(item.get('tipo'))}</td>"
            f"<td>{esc('REVOKED' if item.get('revoked') else item.get('status'))}</td>"
            f"<td>{esc(', '.join(item.get('tool_slugs') or []) or '—')}</td>"
            f"<td><code>{esc(item.get('md_ref'))}</code></td>"
            f"<td><code>{esc(item.get('reg_ref'))}</code></td>"
            "</tr>"
        )
    link_n = links.get("population") or 0
    senado_block = types.get("senado_block")
    camara_block = types.get("camara_block")
    agency_n = agencies.get("population") or 0
    pgd_rows = []
    for item in (pgd.get("guia_parts") or []) + (pgd.get("cartilhas") or []):
        pgd_rows.append(
            "<tr>"
            f"<td><code>{esc(item.get('business_key'))}</code></td>"
            f"<td>{esc(item.get('title'))}</td>"
            f"<td>{esc(item.get('status'))}</td>"
            f"<td>{esc((item.get('url') or 'EVIDENCE_PENDING'))}</td>"
            "</tr>"
        )
    dim_txt = ", ".join(
        f"{d.get('n')} {d.get('name')}" for d in (pgd.get("quality_dimensions") or [])
    ) or "EVIDENCE_PENDING"
    scale_stems = "".join(
        f"<li><code>{esc(item.get('stem'))}</code> · {esc(item.get('gap'))} · data/tools={esc(item.get('in_data_tools'))}</li>"
        for item in (pages_pend.get("third_party_scale_stems") or [])
    )
    set_rows = []
    for item in libmap.get("observed_sets") or []:
        set_rows.append(
            "<tr>"
            f"<td><code>{esc(item.get('id'))}</code></td>"
            f"<td>{esc(item.get('count'))}</td>"
            f"<td>{esc(item.get('kind'))}</td>"
            f"<td>{esc(item.get('official_api') or item.get('official_api_status') or '—')}</td>"
            f"<td>{esc((item.get('note') or '')[:180])}</td>"
            "</tr>"
        )
    layer_api_rows = []
    for item in libmap.get("api_where_possible") or []:
        layer_api_rows.append(
            "<tr>"
            f"<td>{esc(item.get('layer'))}</td>"
            f"<td><code>{esc(item.get('adapter') or 'null')}</code></td>"
            f"<td>{esc(item.get('http_status') if item.get('http_status') is not None else 'null')}</td>"
            f"<td>{esc(item.get('epistemic_status'))}</td>"
            f"<td>{esc((item.get('note') or '')[:180])}</td>"
            "</tr>"
        )
    concept_lis = "".join(
        f"<li><code>{esc(p.get('id'))}</code> · {esc(p.get('layer'))} · {esc(p.get('source'))}</li>"
        for p in (concept.get("projections") or [])
    )
    header, footer = _header_footer(home_href)
    body = f"""{header}
  <main id="conteudo" class="wrap">
    <header class="page-hero">
      <p class="eyebrow">L60 Biblioteca · ambiente controlado</p>
      <h1>Biblioteca de recursos.</h1>
      <p class="lede">Catálogo canônico de fontes governamentais (ANVISA, MS, COFEN, COREN-SP HTML, SGD/PGDADOS), legislação federal do Congresso Nacional (incluindo decreto regulamentar numerado) e currículo documental básico→avançado. Cada objeto tem MD e REG. Publicação HOLD. HTML/PDF integral não é republicado. Projeto de lei complementar (PLP) é bloqueado. Portaria/resolução de órgão não entra no tubo federal. COREN sem API REST observada.</p>
      <p class="hold-banner">Agências {esc(agency_n)} · Recursos {esc(lib.get("population"))} · Unidades {esc(curr.get("population"))} · Leis {esc(laws.get("population"))} · Alertas ALTA {esc(alerts.get("alta_count"))} · APIs online {esc(adapters.get("adapters") and sum(1 for a in adapters.get("adapters") or [] if a.get("online")))} · 32 bibliotecas={esc(libmap.get("claimed_32_libraries") or "EVIDENCE_PENDING")} · release HOLD</p>
    </header>
    <section class="panel">
      <h2>L60 observado vs 32 reivindicadas</h2>
      <p>COMPARE Drive ({esc(libmap.get("business_key") or "MD-LIB-API-MAP-001")}). Sem unzip em <code>data/tools</code>. Sem copiar nanda-00046.json.</p>
      <div class="table-wrap"><table class="inspect"><thead><tr><th>conjunto</th><th>n</th><th>tipo</th><th>API</th><th>nota</th></tr></thead><tbody>{"".join(set_rows) or "<tr><td colspan='5'>EVIDENCE_PENDING</td></tr>"}</tbody></table></div>
      <div class="table-wrap"><table class="inspect"><thead><tr><th>camada</th><th>adapter</th><th>HTTP</th><th>estado</th><th>nota</th></tr></thead><tbody>{"".join(layer_api_rows) or "<tr><td colspan='5'>EVIDENCE_PENDING</td></tr>"}</tbody></table></div>
    </section>
    <section class="panel">
      <h2>Guia por conceito (L150/L160)</h2>
      <p>{esc(concept.get("rule") or "Um conceito → uma identidade → renderer.")} LLM canónico={esc((concept.get("renderer") or {}).get("llm_canonical") or "FORBIDDEN")}.</p>
      <ul>{concept_lis or "<li>MD-CONCEPT-RENDER-001 EVIDENCE_PENDING.</li>"}</ul>
    </section>
    <section class="panel">
      <h2>Fontes e APIs observadas</h2>
      <p>API REST só entra com <code>base_url</code> após HTTP 200. Sem 200 permanece null. Extração periódica {esc(alerts.get("frequency_hours") or 24)}h. Portal pode ficar offline.</p>
      <div class="table-wrap"><table class="inspect"><thead><tr><th>adapter</th><th>órgão</th><th>HTTP</th><th>base_url</th><th>estado</th></tr></thead><tbody>{"".join(api_rows) or "<tr><td colspan='5'>EVIDENCE_PENDING — rode extract com rede.</td></tr>"}</tbody></table></div>
    </section>
    <section id="legislacao" class="panel">
      <h2>Legislação federal (API do Congresso)</h2>
      <p>Fonte: Dados Abertos do Senado/Congresso (<code>legislacao/</code>). Órgão emite; a casa legislativa publica o corpus. PLP/PL/requerimento/parecer bloqueados. LCP promulgada tem força de lei. Decreto numerado (DEC-n) entra como regulamentar. DEC-sn/DEC-cl bloqueados. Norma revogada pode vincular ferramenta. Tipos Senado bloqueados {esc(senado_block)} · Câmara bloqueados {esc(camara_block)} · vínculos ferramenta {esc(link_n)}.</p>
      <div class="table-wrap"><table class="inspect"><thead><tr><th>id</th><th>norma</th><th>tipo</th><th>status</th><th>ferramentas</th><th>MD</th><th>REG</th></tr></thead><tbody>{"".join(law_rows) or "<tr><td colspan='7'>EVIDENCE_PENDING — rode extract com rede.</td></tr>"}</tbody></table></div>
    </section>
    <section id="pgdados" class="panel">
      <h2>PGDADOS e qualidade digital (SGD / MGI)</h2>
      <p>Referência operacional BR explícita: <a href="https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/governancadedados/pgdados">gov.br …/governancadedados/pgdados</a>. PDF catalogado por href <code>gov.br</code>. Texto do manual não vira regra de produto. Não substitui cláusula ISO 8000 licenciada. Parte 3 e volumes 4–5 sem PDF observado permanecem EVIDENCE_PENDING. PDF ABNT de terceiro no chrome do portal é ignorado. Dimensões observadas: {esc(dim_txt)}.</p>
      <div class="table-wrap"><table class="inspect"><thead><tr><th>id</th><th>material</th><th>status</th><th>url</th></tr></thead><tbody>{"".join(pgd_rows) or "<tr><td colspan='4'>EVIDENCE_PENDING — rode extract com rede.</td></tr>"}</tbody></table></div>
    </section>
    <section class="panel">
      <h2>Recursos catalogados</h2>
      <div class="table-wrap"><table class="inspect"><thead><tr><th>id</th><th>título</th><th>agência</th><th>camada</th><th>status</th><th>MD</th><th>REG</th></tr></thead><tbody>{"".join(res_rows) or "<tr><td colspan='7'>Biblioteca vazia até AG-LIBRARY-CATALOG.</td></tr>"}</tbody></table></div>
    </section>
    <section id="curriculo">
      <h2>Currículo documental (básico → avançado)</h2>
      <p>Texto extraído só dos campos já existentes em <code>data/tools</code>. LLM não autorou. Dimensionamento permanece HOLD.</p>
      {"".join(curr_blocks) or "<p>Currículo EVIDENCE_PENDING.</p>"}
    </section>
    <section class="panel">
      <h2>Pendências ALTA</h2>
      <ul>{pending or "<li>Nenhuma pendência registrada.</li>"}</ul>
    </section>
    <section class="panel">
      <h2>pages_full — catálogo de pendências REG</h2>
      <p>{esc(pages_pend.get("owner_override") or "Inventário demonstra pendências REG. Extração clínica em massa FORBIDDEN.")} HTML={esc(pages_pend.get("html_count"))} · stems={esc(pages_pend.get("unique_stems"))} · ref <code>{esc(pages_pend.get("business_key") or "MD-PAGES-REG-PEND-001")}</code>.</p>
      <ul>{scale_stems or "<li>Escalas de terceiros EVIDENCE_PENDING neste lote.</li>"}</ul>
    </section>
    <section class="panel">
      <h2>Alertas de frescura / offline</h2>
      <ul>{alert_items or "<li>Sem alertas neste lote.</li>"}</ul>
      <p class="meta"><a href="admin/library.html">Admin biblioteca</a> · <a href="admin/apis.html">Admin APIs</a> · <a href="admin/monitoring.html">Monitoramento</a></p>
    </section>
  </main>
  {footer}"""
    return _shell(
        "Biblioteca de recursos — Calculadoras de Enfermagem",
        "Biblioteca canônica de fontes ANVISA, MS, COFEN, legislação federal do Congresso e currículo básico a avançado. Publicação HOLD.",
        body,
        css_href=None if inline_css else css_href,
        css_inline="file" if inline_css else None,
        home_href=home_href,
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
    from validators.dual_render import check_parity
    from validators.release_gate import evaluate_release

    from .admin_site import page_dashboard, studio_map, token_registry
    from .bootstrap import evaluate_layer_registry

    parity = check_parity()
    ctx = {
        "tools": tools,
        "completeness": completeness,
        "layers": layers,
        "contract": contract,
        "parity": parity,
        "release": evaluate_release(completeness, parity),
        "layer_caat": evaluate_layer_registry(),
        "studio": studio_map(),
        "tokens": token_registry(),
    }
    return page_dashboard(ctx, css_href=css_href, home_href=home_href, inline_css=inline_css, nested=False)


def _emit_tree(dest: Path, tools: list[dict], *, inline_css: bool) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "tools").mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    img_dest = dest / "assets" / "img"
    img_dest.mkdir(parents=True, exist_ok=True)
    for name in (
        "logotipo-calculadoras-de-enfermagem.webp",
        "logotipo-footer.png",
        "icontopbar1-calculadoras-de-enfermagem.webp",
        "iconrodape1-80-calculadoras-de-enfermagem.webp",
        "og-default.png",
    ):
        src = ASSETS_DIR / "img" / name
        if name == "og-default.png" and not src.exists():
            write_default_og_png(src)
        if src.exists():
            shutil.copy2(src, img_dest / name)
            written.append(img_dest / name)
    fonts_src = ASSETS_DIR / "fonts"
    if fonts_src.exists():
        fonts_dest = dest / "assets" / "fonts"
        shutil.copytree(fonts_src, fonts_dest, dirs_exist_ok=True)
        written.extend(sorted(fonts_dest.rglob("*.woff2")))
    if not inline_css:
        assets = dest / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ASSETS_DIR / "css" / "app.css", assets / "app.css")
        shutil.copy2(ASSETS_DIR / "js" / "calc-engine.js", assets / "calc-engine.js")
        shutil.copy2(ASSETS_DIR / "js" / "admin-control.js", assets / "admin-control.js")
        shutil.copy2(ASSETS_DIR / "js" / "a11y.js", assets / "a11y.js")
        written.extend([assets / "app.css", assets / "calc-engine.js", assets / "admin-control.js", assets / "a11y.js"])
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
    biblioteca = dest / "biblioteca.html"
    biblioteca.write_text(
        generate_biblioteca(
            css_href=css_href,
            home_href=home_from_home,
            inline_css=inline_css,
        ),
        encoding="utf-8",
    )
    written.append(biblioteca)

    from .admin_site import emit_admin_pages, studio_map, token_registry
    from .bootstrap import evaluate_layer_registry

    contract_path = ADMIN_DIR / "contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8")) if contract_path.exists() else {}
    completeness = evaluate_catalog()
    ctx = {
        "tools": tools,
        "completeness": completeness,
        "layers": layer_records(),
        "contract": contract,
        "parity": {"status": "SEE_AUDIT", "pagesCompared": None},
        "release": {"status": completeness.get("status")},
        "layer_caat": evaluate_layer_registry(),
        "studio": studio_map(),
        "tokens": token_registry(),
    }
    written.extend(
        emit_admin_pages(
            dest,
            ctx,
            css_href=css_href,
            home_href=home_from_home,
            inline_css=inline_css,
        )
    )
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
