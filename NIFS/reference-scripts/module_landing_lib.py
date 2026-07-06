"""Module landing pages — hero, features, FAQ, related tools (React mockup parity)."""
from __future__ import annotations

import json
from typing import Any

from icons_lib import lucide_icon
from website_lib import _svg_icon, esc, render_breadcrumbs, render_document, route_href


def _css(depth: int) -> list[str]:
    prefix = "../" * depth if depth else ""
    return [f"{prefix}assets/css/templates.css", f"{prefix}assets/css/hub.css"]


def _crumbs(items: list[tuple[str, str | None]], depth: int) -> str:
    return f'<div class="section-container mod-breadcrumb">{render_breadcrumbs(items, depth)}</div>'


def _render_related_tools(tools: list[dict], depth: int) -> str:
    if not tools:
        return ""
    cards = []
    for tool in tools:
        href = tool.get("href", "#")
        if href.startswith("/"):
            href = route_href(href, depth)
        badge = tool.get("type", "ferramenta")
        cards.append(f"""
<article class="mod-related-card card">
  <span class="mod-related-card__badge">{esc(badge)}</span>
  <strong>{esc(tool["title"])}</strong>
  <p>{esc(tool.get("description", ""))}</p>
  <a href="{esc(href)}">Abrir →</a>
</article>""")
    return f"""
<section class="mod-section mod-related section-container" aria-labelledby="mod-related-title">
  <h2 id="mod-related-title">Ferramentas relacionadas</h2>
  <p class="mod-section__lead">Calculadoras, escalas e recursos integrados ao ecossistema Calculadoras de Enfermagem.</p>
  <div class="mod-related-grid">{"".join(cards)}</div>
</section>"""


def _render_hero(page: dict, depth: int) -> str:
    hero = page.get("hero", {})
    bullets = "".join(
        f'<li><span class="mod-hero__check" aria-hidden="true">{lucide_icon("check", size="14")}</span>{esc(b)}</li>'
        for b in hero.get("bullets", [])
    )
    cta_href = hero.get("cta_href", page.get("wizard_href", "#"))
    if cta_href.startswith("/"):
        cta_href = route_href(cta_href, depth)
    secondary_href = hero.get("secondary_href", "#")
    if secondary_href.startswith("/"):
        secondary_href = route_href(secondary_href, depth)
    preview = hero.get("preview_html", "")
    return f"""
<section class="mod-hero">
  <div class="mod-hero__inner section-container">
    <div class="mod-hero__content">
      <p class="mod-hero__eyebrow">{esc(hero.get("eyebrow", ""))}</p>
      <h1>{esc(hero.get("title", page["title"]))}</h1>
      <p class="mod-hero__subtitle">{esc(hero.get("subtitle", page.get("subtitle", "")))}</p>
      {f'<ul class="mod-hero__bullets">{bullets}</ul>' if bullets else ''}
      <div class="mod-hero__actions">
        <a class="btn-primary-sm" href="{esc(cta_href)}">{esc(hero.get("cta", "Iniciar"))}</a>
        {f'<a class="btn-outline mod-hero__secondary" href="{esc(secondary_href)}">{esc(hero.get("secondary_cta", ""))}</a>' if hero.get("secondary_cta") else ''}
      </div>
    </div>
    {f'<div class="mod-hero__preview">{preview}</div>' if preview else ''}
  </div>
</section>"""


def _render_steps(steps: list[dict]) -> str:
    if not steps:
        return ""
    items = "".join(
        f"""<article class="mod-step card">
  <span class="mod-step__num">{i}</span>
  <h3>{esc(s["title"])}</h3>
  <p>{esc(s.get("text", s.get("description", "")))}</p>
</article>"""
        for i, s in enumerate(steps, 1)
    )
    return f"""
<section class="mod-section mod-section--muted section-container">
  <header class="mod-section__head">
    <span class="mod-badge">Como funciona</span>
    <h2>Passo a passo</h2>
  </header>
  <div class="mod-steps-grid">{items}</div>
</section>"""


def _render_features(features: list[dict]) -> str:
    if not features:
        return ""
    items = "".join(
        f"""<article class="mod-feature card">
  <h3>{esc(f["title"])}</h3>
  <p>{esc(f.get("description", ""))}</p>
</article>"""
        for f in features
    )
    return f"""
<section class="mod-section section-container">
  <header class="mod-section__head">
    <span class="mod-badge">Funcionalidades</span>
    <h2>Recursos principais</h2>
  </header>
  <div class="mod-features-grid">{items}</div>
</section>"""


def _render_benefits(benefits: list[dict], stats: list[dict] | None = None) -> str:
    if not benefits and not stats:
        return ""
    benefit_items = "".join(
        f"""<div class="mod-benefit">
  <h3>{esc(b["title"])}</h3>
  <p>{esc(b.get("description", ""))}</p>
</div>"""
        for b in benefits
    )
    stats_html = ""
    if stats:
        bars = "".join(
            f"""<div class="mod-stat">
  <div class="mod-stat__head"><span class="mod-stat__value">{esc(str(s["value"]))}%</span><span>{esc(s["label"])}</span></div>
  <div class="mod-stat__bar"><div style="width:{min(100, int(s["value"]))}%"></div></div>
</div>"""
            for s in stats
        )
        stats_html = f'<div class="mod-stats-card card card-highlight"><h3>Impacto na prática</h3>{bars}</div>'
    return f"""
<section class="mod-section mod-section--muted section-container">
  <div class="mod-benefits-split">
    <div>
      <span class="mod-badge">Benefícios</span>
      <h2>Por que usar esta ferramenta?</h2>
      <div class="mod-benefits-list">{benefit_items}</div>
    </div>
    {stats_html}
  </div>
</section>"""


def _render_testimonials(testimonials: list[dict]) -> str:
    if not testimonials:
        return ""
    items = "".join(
        f"""<blockquote class="mod-testimonial card">
  <div class="mod-testimonial__stars" aria-label="{t.get("rating", 5)} estrelas">{"★" * int(t.get("rating", 5))}</div>
  <p>"{esc(t["text"])}"</p>
  <footer><strong>{esc(t["name"])}</strong><span>{esc(t.get("role", ""))}</span></footer>
</blockquote>"""
        for t in testimonials
    )
    return f"""
<section class="mod-section section-container">
  <header class="mod-section__head"><span class="mod-badge">Depoimentos</span><h2>O que os profissionais dizem</h2></header>
  <div class="mod-testimonials-grid">{items}</div>
</section>"""


def _render_faq(faqs: list[dict]) -> str:
    if not faqs:
        return ""
    items = "".join(
        f"""<details class="mod-faq card">
  <summary>{esc(f["question"])}</summary>
  <p>{esc(f["answer"])}</p>
</details>"""
        for f in faqs
    )
    return f"""
<section class="mod-section mod-section--muted section-container">
  <header class="mod-section__head"><span class="mod-badge">FAQ</span><h2>Perguntas frequentes</h2></header>
  <div class="mod-faq-list">{items}</div>
</section>"""


def _render_cta(page: dict, depth: int) -> str:
    cta = page.get("cta_block", {})
    if not cta:
        return ""
    href = cta.get("href", page.get("wizard_href", "#"))
    if href.startswith("/"):
        href = route_href(href, depth)
    return f"""
<section class="mod-cta section-container">
  <div class="mod-cta__inner card card-highlight">
    <h2>{esc(cta.get("title", "Pronto para começar?"))}</h2>
    <p>{esc(cta.get("text", ""))}</p>
    <a class="btn-primary-sm" href="{esc(href)}">{esc(cta.get("button", "Iniciar agora"))}</a>
  </div>
</section>"""


def _render_trail_cards(categories: list[dict], depth: int) -> str:
    if not categories:
        return ""
    cards = []
    for cat in categories:
        pct = cat.get("progress", 0)
        href = cat.get("href", "#trilhas-list")
        if href.startswith("/"):
            href = route_href(href, depth)
        status = "Concluída" if pct >= 100 else ("Em andamento" if pct > 0 else "Não iniciada")
        cards.append(f"""
<article class="mod-trail-card card" id="{esc(cat.get("id", ""))}">
  <div class="mod-trail-card__bar" style="--trail-progress:{pct}%"></div>
  <span class="mod-trail-card__num">{esc(cat.get("number", ""))}</span>
  <h3>{esc(cat["title"])}</h3>
  <p>{esc(cat.get("description", ""))}</p>
  <div class="mod-trail-card__meta">
    <span>{esc(str(cat.get("lessons", 0)))} aulas</span>
    <span>{esc(str(cat.get("hours", 0)))}h</span>
    <span class="hub-pill">{esc(cat.get("difficulty", ""))}</span>
  </div>
  <div class="mod-trail-card__foot">
    <span>{pct}% · {status}</span>
    <a class="btn-primary-sm" href="{esc(href)}">{esc(cat.get("action", "Iniciar trilha"))}</a>
  </div>
</article>""")
    return f"""
<section class="mod-section mod-section--muted section-container" id="trilhas-list">
  <header class="mod-section__head"><span class="mod-badge">Trilhas disponíveis</span><h2>Escolha sua trilha de conhecimento</h2></header>
  <div class="mod-trails-grid">{"".join(cards)}</div>
</section>"""


def _render_sbar_example(example: dict) -> str:
    if not example:
        return ""
    blocks = [
        ("S", "Situação", example.get("situation", ""), "blue"),
        ("B", "Background", example.get("background", ""), "green"),
        ("A", "Avaliação", example.get("assessment", ""), "orange"),
        ("R", "Recomendação", example.get("recommendation", ""), "purple"),
    ]
    items = "".join(
        f"""<div class="mod-sbar-example__row">
  <span class="mod-sbar-example__letter mod-sbar-example__letter--{color}">{letter}</span>
  <div class="mod-sbar-example__body mod-sbar-example__body--{color}">
    <strong>{esc(title)}</strong>
    <p>{esc(text)}</p>
  </div>
</div>"""
        for letter, title, text, color in blocks
    )
    return f"""
<section class="mod-section mod-section--muted section-container">
  <header class="mod-section__head"><span class="mod-badge">Exemplo prático</span><h2>Exemplo de SBAR preenchido</h2></header>
  <div class="mod-sbar-example card">{items}</div>
</section>"""


def _render_cv_preview() -> str:
    return """
<div class="mod-cv-preview card">
  <div class="mod-cv-preview__head">
    <span class="mod-cv-preview__avatar">MS</span>
    <div>
      <strong>Mariana Silva de Oliveira</strong>
      <span>Enfermeira</span>
      <small>(11) 99999-0000 · mariana.silva@email.com · São Paulo, SP</small>
    </div>
  </div>
  <div class="mod-cv-preview__section"><strong>Resumo</strong><p>Enfermeira com 5 anos em UTI e equipe cirúrgica. Especialista em cuidados críticos.</p></div>
  <div class="mod-cv-preview__section"><strong>Formação</strong><p>Bacharelado em Enfermagem — USP · 2018</p></div>
  <div class="mod-cv-preview__section"><strong>Experiência</strong><p>Hospital Santa Clara · UTI adulto · 2021–Atual</p></div>
  <div class="mod-cv-preview__tags"><span>SAE</span><span>COREN</span><span>UTI</span><span>PALS</span></div>
</div>"""


def _render_sbar_steps_card(blocks: list[dict]) -> str:
    items = "".join(
        f"""<div class="mod-sbar-steps__item">
  <span class="mod-sbar-steps__letter mod-sbar-steps__letter--{esc(b.get("color", "blue"))}">{esc(b["letter"])}</span>
  <div><strong>{esc(b["title"])}</strong><p>{esc(b.get("text", ""))}</p></div>
</div>"""
        for b in blocks
    )
    return f'<div class="mod-sbar-steps card">{items}</div>'


def render_module_landing(page: dict, *, depth: int, breadcrumb: list[tuple[str, str | None]] | None = None) -> str:
    """Full module landing (curriculo, sbar, trilhas, calculadoras trabalhistas)."""
    crumbs = breadcrumb or [(page["title"], None)]
    hero = dict(page.get("hero", {}))
    if page.get("route") == "/curriculo" and not hero.get("preview_html"):
        hero["preview_html"] = _render_cv_preview()
    if page.get("route") == "/sbar" and not hero.get("preview_html"):
        hero["preview_html"] = _render_sbar_steps_card(page.get("blocks", []))

    sections = [
        _crumbs(crumbs, depth),
        _render_hero({**page, "hero": hero}, depth),
    ]
    if page.get("example_sbar"):
        sections.append(_render_sbar_example(page["example_sbar"]))
    if page.get("trail_categories"):
        sections.append(_render_trail_cards(page["trail_categories"], depth))
    sections.extend([
        _render_steps(page.get("steps", [])),
        _render_features(page.get("features", [])),
        _render_benefits(page.get("benefits", []), page.get("stats")),
        _render_testimonials(page.get("testimonials", [])),
        _render_faq(page.get("faqs", [])),
        _render_related_tools(page.get("related_tools", []), depth),
        _render_cta(page, depth),
    ])
    main = "".join(sections)
    seo = page.get("seo", {})
    return render_document(
        depth=depth,
        title=seo.get("title", page["title"]),
        description=seo.get("description", page.get("subtitle", "")),
        canonical_path=page.get("route", "/"),
        main_html=main,
        extra_css=_css(depth),
        main_class="site-main mod-main",
    )
