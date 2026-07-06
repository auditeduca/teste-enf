"""Protocol detail pages — POP institucional Calculadoras de Enfermagem."""
from __future__ import annotations

from datetime import datetime

from website_lib import (
    _svg_icon,
    esc,
    render_breadcrumbs,
    render_document,
    route_href,
    slugify,
)

TEMPLATES_CSS = "assets/css/templates.css"


def _format_date(iso: str | None) -> str:
    if not iso:
        return "2026"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        months = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
        return f"{dt.day} {months[dt.month - 1]}. {dt.year}"
    except ValueError:
        return iso[:10]


def protocol_slug(protocol: dict) -> str:
    return slugify(protocol.get("protocol_code", protocol.get("title", "protocol")))


def render_protocol_page(
    protocol: dict,
    *,
    depth: int,
    slug_map: dict[str, str],
    guideline: dict | None = None,
) -> str:
    slug = protocol_slug(protocol)
    title = protocol.get("title", "Protocolo")
    page_title = f"{title} | Protocolos"
    page_desc = f"Protocolo institucional — Calculadoras de Enfermagem 2026 — {title}."
    canon = f"/protocolos/{slug}"
    prefix = "../" * depth if depth else ""

    crumbs = [
        ("Protocolos", route_href("/protocolos", depth)),
        (title[:48] + ("…" if len(title) > 48 else ""), None),
    ]

    tools_html = ""
    for code in protocol.get("related_tool_codes") or []:
        if code in slug_map:
            href = route_href(f"/ferramentas/{slug_map[code]}", depth)
            tools_html += f'<li><a href="{esc(href)}">{esc(code.replace("TOOL.", ""))}</a></li>'

    evidence = ""
    if guideline:
        evidence = f"""
<section class="tpl-section">
  <h2>Evidência vinculada</h2>
  <div class="callout callout--tip">
    <strong>{esc(guideline.get("title", ""))}</strong> — {esc(guideline.get("source", "Calculadoras de Enfermagem"))} · {esc(str(guideline.get("year", "")))}
  </div>
</section>"""

    main = f"""
<div class="section-container tpl-breadcrumb">{render_breadcrumbs(crumbs, depth)}</div>
<article class="tpl-protocol section-container">
  <header class="tpl-protocol__header">
    <span class="badge-validated">Protocolo institucional</span>
    <h1>{esc(title)}</h1>
    <p class="tpl-protocol__meta">Código {esc(protocol.get("protocol_code", ""))} · Atualizado {_format_date(protocol.get("updated_at"))}</p>
  </header>
  <div class="tpl-protocol__grid">
    <div class="tpl-protocol__content">
      <section class="tpl-section">
        <h2>Objetivo</h2>
        <p>Padronizar a assistência de enfermagem relacionada a <strong>{esc(title.lower())}</strong>, alinhada às metas de segurança do paciente e diretrizes da plataforma 2026.</p>
      </section>
      <section class="tpl-section">
        <h2>Etapas principais</h2>
        <ol class="tpl-steps">
          <li>Identificar paciente e confirmar prescrição/indicação</li>
          <li>Verificar contraindicações e alertas clínicos</li>
          <li>Executar procedimento conforme POP institucional</li>
          <li>Registrar evolução e indicadores de qualidade</li>
          <li>Comunicar intercorrências via SBAR</li>
        </ol>
      </section>
      {evidence}
      <section class="tpl-section">
        <h2>Checklist rápido</h2>
        <ul class="article-checklist">
          <li><span class="article-check" aria-hidden="true">✓</span>Paciente identificado corretamente</li>
          <li><span class="article-check" aria-hidden="true">✓</span>Equipe informada e capacitada</li>
          <li><span class="article-check" aria-hidden="true">✓</span>Materiais e ambiente preparados</li>
          <li><span class="article-check" aria-hidden="true">✓</span>Registro documentado no prontuário</li>
        </ul>
      </section>
    </div>
    <aside class="tpl-protocol__aside card">
      <h2>Ferramentas relacionadas</h2>
      <ul class="tpl-link-list">{tools_html or "<li>Em breve</li>"}</ul>
      <a class="btn-primary-sm" href="{esc(route_href("/protocolos", depth))}">← Voltar aos protocolos</a>
    </aside>
  </div>
</article>"""

    return render_document(
        depth=depth,
        title=page_title,
        description=page_desc,
        canonical_path=canon,
        main_html=main,
        extra_css=[f"{prefix}{TEMPLATES_CSS}", f"{prefix}assets/css/article.css"],
        main_class="site-main tpl-main",
    )
