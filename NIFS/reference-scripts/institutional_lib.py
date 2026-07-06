"""Institutional center pages — Privacy, Sustainability & modular institutional pages."""
from __future__ import annotations

from website_lib import (
    esc,
    image_href,
    render_breadcrumbs,
    render_document,
    route_href,
    slugify,
)


def _meta_hashtags(tags: list[str]) -> str:
    if not tags:
        return ""
    return f'<meta name="ce-hashtags" content="{esc(",".join(tags))}">'


def _inst_icon(name: str) -> str:
    icons = {
        "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
        "scale": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>',
        "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>',
        "handshake": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/></svg>',
        "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
        "support": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
        "content": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>',
        "partnership": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    }
    return icons.get(name, icons["shield"])


def _render_inst_hero(hero: dict, *, depth: int, variant: str = "default") -> str:
    img = image_href(depth, hero.get("image", "hero-privacy-center.png"))
    accent = hero.get("accent", "")
    desc = hero.get("description", hero.get("subtitle", ""))
    if variant == "sustainability":
        title_html = f'{esc(hero["title"])} <span class="center-hero__accent">{esc(accent)}</span>' if accent else esc(hero["title"])
        accent_block = ""
    else:
        title_html = esc(hero["title"])
        accent_block = f'<p class="center-hero__accent">{esc(accent)}</p>' if accent else ""
    return f"""
<section class="center-hero center-hero--{esc(variant)}" aria-labelledby="inst-hero-title">
  <div class="section-container center-hero__grid">
    <div>
      <h1 id="inst-hero-title" class="center-hero__title">{title_html}</h1>
      {accent_block}
      {f'<p class="center-hero__desc">{esc(desc)}</p>' if desc else ""}
    </div>
    <div class="center-hero__media"><img src="{esc(img)}" alt="" width="480" height="400" loading="eager"></div>
  </div>
</section>"""


def _inst_document(
    *,
    depth: int,
    title: str,
    description: str,
    canonical_path: str,
    main_html: str,
    hashtags: list[str] | None = None,
) -> str:
    prefix = "../" * depth if depth else ""
    return render_document(
        depth=depth,
        title=title,
        description=description,
        canonical_path=canonical_path,
        main_html=main_html,
        extra_css=[f"{prefix}assets/css/institutional.css"],
        main_class="site-main center-main inst-main",
        extra_head=_meta_hashtags(hashtags or []),
    )


def _tab_icon(name: str) -> str:
    icons = {
        "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        "cookie": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 12h.01M12 12h.01M16 12h.01"/></svg>',
        "document": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>',
        "warning": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/></svg>',
        "leaf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/></svg>',
        "bolt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>',
        "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="M18 17V9M13 17V5M8 17v-3"/></svg>',
    }
    return icons.get(name, icons["document"])


def _render_tab_bar(tabs: list[dict], group: str) -> str:
    buttons = []
    for i, tab in enumerate(tabs):
        active = " is-active" if i == 0 else ""
        buttons.append(
            f'<button type="button" class="center-tab{active}" role="tab" '
            f'aria-selected="{"true" if i == 0 else "false"}" '
            f'data-inst-tab="{esc(tab["id"])}" data-inst-group="{esc(group)}">'
            f'{_tab_icon(tab.get("icon", "document"))}{esc(tab["label"])}</button>'
        )
    return f'<div class="center-tabs-wrap"><div class="section-container"><div class="center-tabs" role="tablist">{"".join(buttons)}</div></div></div>'


def _render_sidebar(cards: list[dict], depth: int) -> str:
    items = []
    for card in cards:
        if card.get("tab"):
            href_attr = f'href="#panel-{esc(card["tab"])}" data-inst-tab-link="{esc(card["tab"])}" data-inst-group="privacy"'
        else:
            href_attr = f'href="{esc(route_href(card.get("href", "/contato"), depth))}"'
        items.append(f"""
<aside class="sidebar-card">
  <h4>{esc(card["title"])}</h4>
  <p>{esc(card["text"])}</p>
  <a {href_attr}>{esc(card["link_label"])} →</a>
</aside>""")
    return f'<div class="center-sidebar">{"".join(items)}</div>'


def _render_panel_content(panel: dict) -> str:
    sections = []
    for i, sec in enumerate(panel.get("sections", []), 1):
        lis = ""
        if sec.get("list"):
            lis = "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in sec["list"]) + "</ul>"
        sections.append(f"""
<div class="center-section">
  <h3><span class="center-section__num">{i}</span>{esc(sec["title"])}</h3>
  <p>{esc(sec["body"])}</p>{lis}
</div>""")
    updated = ""
    if panel.get("updated"):
        updated = f'<p class="center-updated">Última atualização: {esc(panel["updated"])}</p>'
    return f'<div class="center-content"><h2>{esc(panel["title"])}</h2>{"".join(sections)}{updated}</div>'


def render_privacy_center(content: dict, *, depth: int, title: str, description: str) -> str:
    hero = content["hero"]
    img = image_href(depth, hero.get("image", "hero-privacy-center.png"))

    panels_html = ""
    for i, tab in enumerate(content["tabs"]):
        panel = content["panels"][tab["id"]]
        active = " is-active" if i == 0 else ""
        panels_html += f"""
<div id="panel-{esc(tab["id"])}" class="center-panel{active}" role="tabpanel" data-inst-panel="{esc(tab["id"])}" data-inst-group="privacy">
  <div class="section-container center-layout">
    {_render_panel_content(panel)}
    {_render_sidebar(panel.get("sidebar", []), depth)}
  </div>
</div>"""

    legal = content.get("legal_notice") or {}
    legal_html = ""
    if legal:
        legal_html = f"""
<div class="section-container">
  <aside class="inst-legal-notice" role="note" aria-labelledby="legal-notice-title">
    <h2 id="legal-notice-title">{esc(legal.get("title", "Notificação Legal"))}</h2>
    <p>{esc(legal.get("text", ""))}</p>
    {f'<p class="inst-legal-notice__ref"><strong>{esc(legal.get("law_reference", ""))}</strong></p>' if legal.get("law_reference") else ""}
    {f'<p class="center-updated">Atualizado: {esc(legal.get("updated", ""))}</p>' if legal.get("updated") else ""}
  </aside>
</div>"""

    main = f"""
<section class="center-hero" aria-labelledby="center-hero-title">
  <div class="section-container center-hero__grid">
    <div>
      <h1 id="center-hero-title" class="center-hero__title">{esc(hero["title"])}</h1>
      <p class="center-hero__accent">{esc(hero["accent"])}</p>
      <p class="center-hero__desc">{esc(hero["description"])}</p>
    </div>
    <div class="center-hero__media"><img src="{esc(img)}" alt="" width="480" height="400" loading="eager"></div>
  </div>
</section>
{legal_html}
{_render_tab_bar(content["tabs"], "privacy")}
{panels_html}"""

    prefix = "../" * depth if depth else ""
    tags = ["#privacidade", "#lgpd", "#cookies", "#termos", "#institucional"]
    return render_document(
        depth=depth,
        title=title,
        description=description,
        canonical_path="/privacidade",
        main_html=main,
        extra_css=[f"{prefix}assets/css/institutional.css"],
        main_class="site-main center-main",
        extra_head=_meta_hashtags(tags),
    )


def _sus_cards(cards: list[dict]) -> str:
    return "".join(
        f'<div class="sus-card"><h4>{esc(c["title"])}</h4><p>{esc(c["text"])}</p></div>'
        for c in cards
    )


def render_sustainability_center(content: dict, *, depth: int, title: str, description: str) -> str:
    hero = content["hero"]
    img = image_href(depth, hero.get("image", "hero-sustainability.png"))
    cta1 = hero.get("cta_primary", {})
    cta2 = hero.get("cta_secondary", {})

    panel_sus = f"""
<div id="panel-sustentabilidade" class="center-panel is-active" role="tabpanel" data-inst-panel="sustentabilidade" data-inst-group="sustainability">
  <div class="section-container sus-block">
    <h2 class="sus-block__title">Sustentabilidade Digital</h2>
    <p class="sus-block__subtitle">Tecnologia a serviço de um futuro mais sustentável.</p>
    <div class="sus-cards">{_sus_cards(content["cards_sustentabilidade"])}</div>
  </div>
  <div class="section-container sus-block sus-block--alt">
    <h2 class="sus-block__title">Nossa Estratégia ESG Digital</h2>
    <p class="sus-block__subtitle">2025 → 2030</p>
    <div class="sus-timeline">{"".join(
        f'<div class="sus-timeline__item"><div class="sus-timeline__year">{esc(t["year"])}</div>'
        f'<div class="sus-timeline__title">{esc(t["title"])}</div>'
        f'<p class="sus-timeline__text">{esc(t["text"])}</p></div>'
        for t in content["timeline_esg"]
    )}</div>
  </div>
</div>"""

    panel_tech = f"""
<div id="panel-tecnologia-verde" class="center-panel" role="tabpanel" data-inst-panel="tecnologia-verde" data-inst-group="sustainability">
  <div class="section-container sus-block">
    <h2 class="sus-block__title">Tecnologia Verde</h2>
    <p class="sus-block__subtitle">Infraestrutura eficiente e monitoramento em tempo real.</p>
    <div class="sus-cards">{_sus_cards(content["cards_tecnologia_verde"])}</div>
  </div>
</div>"""

    panel_report = f"""
<div id="panel-relatorio" class="center-panel" role="tabpanel" data-inst-panel="relatorio" data-inst-group="sustainability">
  <div class="section-container sus-block">
    <h2 class="sus-block__title">Relatório de Impacto</h2>
    <p class="sus-block__subtitle">Indicadores públicos — transparência mensal Calculadoras de Enfermagem 2026.</p>
    <div class="sus-metrics">{"".join(
        f'<div class="sus-metric"><div class="sus-metric__value">{esc(m["value"])}</div>'
        f'<div class="sus-metric__label">{esc(m["label"])}</div></div>'
        for m in content["metrics"]
    )}</div>
  </div>
</div>"""

    panel_gov = f"""
<div id="panel-governanca" class="center-panel" role="tabpanel" data-inst-panel="governanca" data-inst-group="sustainability">
  <div class="section-container sus-block">
    <h2 class="sus-block__title">Nossos Compromissos Públicos</h2>
    <div class="sus-compromissos">{"".join(
        f'<div class="sus-compromisso"><h4>{esc(c["title"])}</h4><p>{esc(c["text"])}</p></div>'
        for c in content["compromissos"]
    )}</div>
  </div>
  <div class="section-container sus-block sus-block--alt">
    <h2 class="sus-block__title">Transparência</h2>
    <div class="sus-docs">{"".join(
        f'<div class="sus-doc"><h4>{esc(d["title"])}</h4><p>{esc(d["text"])}</p>'
        f'<div class="sus-doc__actions">'
        f'<a href="{esc(route_href(d["href"], depth))}">Ler documento</a>'
        f'<a href="{esc(route_href(d["href"], depth))}">Baixar PDF</a></div></div>'
        for d in content["transparencia_docs"]
    )}</div>
  </div>
  <div class="section-container sus-block">
    <h2 class="sus-block__title">Certificações e Boas Práticas</h2>
    <div class="sus-certs">{"".join(
        f'<div class="sus-cert"><div class="sus-cert__icon">{esc(c["code"])}</div><span>{esc(c["label"])}</span></div>'
        for c in content["certificacoes"]
    )}</div>
  </div>
  <div class="section-container sus-block sus-block--alt">
    <h2 class="sus-block__title">Nosso Roadmap Sustentável</h2>
    <div class="sus-roadmap">{"".join(
        f'<div class="sus-roadmap__item"><div class="sus-roadmap__year">{esc(r["year"])}</div>'
        f'<div class="sus-roadmap__text">{esc(r["text"])}</div></div>'
        for r in content["roadmap"]
    )}</div>
  </div>
</div>"""

    cta = content["cta_final"]
    cta_block = f"""
<section class="center-cta">
  <div class="section-container">
    <h2>{esc(cta["title"])}</h2>
    <p>{esc(cta["text"])}</p>
    <div class="center-cta__actions">
      <a class="btn-primary-lg" href="{esc(route_href(cta["primary"]["href"], depth))}">{esc(cta["primary"]["label"])}</a>
      <a class="btn-outline-lg" href="{esc(cta["secondary"]["href"])}">{esc(cta["secondary"]["label"])}</a>
    </div>
  </div>
</section>"""

    main = f"""
<section class="center-hero center-hero--sustainability" aria-labelledby="sus-hero-title">
  <div class="section-container center-hero__grid">
    <div>
      <h1 id="sus-hero-title" class="center-hero__title">{esc(hero["title"])} <span class="center-hero__accent">{esc(hero["accent"])}</span></h1>
      <p class="center-hero__subtitle">{esc(hero["subtitle"])}</p>
      <div class="center-hero__actions">
        <a class="btn-primary-lg" href="{esc(cta1.get("href", "#panel-sustentabilidade"))}">{esc(cta1.get("label", "Estratégia"))}</a>
        <a class="btn-outline-lg" href="{esc(cta2.get("href", "#panel-relatorio"))}">{esc(cta2.get("label", "Relatório"))}</a>
      </div>
    </div>
    <div class="center-hero__media"><img src="{esc(img)}" alt="Sustentabilidade digital em enfermagem" width="480" height="400" loading="eager"></div>
  </div>
</section>
{_render_tab_bar(content["tabs"], "sustainability")}
{panel_sus}{panel_tech}{panel_report}{panel_gov}
{cta_block}"""

    prefix = "../" * depth if depth else ""
    tags = ["#sustentabilidade", "#esg", "#tecnologia-verde", "#institucional"]
    return render_document(
        depth=depth,
        title=title,
        description=description,
        canonical_path="/sustentabilidade",
        main_html=main,
        extra_css=[f"{prefix}assets/css/institutional.css"],
        main_class="site-main center-main",
        extra_head=_meta_hashtags(tags),
    )


def render_mission_page(page: dict, *, depth: int) -> str:
    seo = page.get("seo", {})
    hero = page["hero"]
    values_html = "".join(
        f"""<article class="inst-value-card">
  <div class="inst-value-card__icon">{_inst_icon(v.get("icon", "shield"))}</div>
  <h3>{esc(v["title"])}</h3>
  <p>{esc(v["text"])}</p>
</article>"""
        for v in page.get("values", [])
    )
    refs_html = "".join(f'<li>{esc(r)}</li>' for r in page.get("references", []))
    crumbs = render_breadcrumbs([("Institucional", route_href("/sobre", depth)), ("Missão, Visão e Valores", None)], depth)
    main = f"""
{_render_inst_hero(hero, depth=depth, variant="mission")}
<div class="section-container inst-body">
  {crumbs}
  <section class="inst-block" aria-labelledby="sec-missao">
    <h2 id="sec-missao">{esc(page["mission"]["title"])}</h2>
    <div class="inst-card">{esc(page["mission"]["text"])}</div>
  </section>
  <section class="inst-block inst-block--vision" aria-labelledby="sec-visao">
    <h2 id="sec-visao">{esc(page["vision"]["title"])}</h2>
    <div class="inst-card inst-card--dark">{esc(page["vision"]["text"])}</div>
  </section>
  <section class="inst-block" aria-labelledby="sec-valores">
    <h2 id="sec-valores">Valores</h2>
    <div class="inst-values-grid">{values_html}</div>
  </section>
  {f'<section class="inst-block inst-references" aria-labelledby="sec-refs"><h2 id="sec-refs">Referências Bibliográficas</h2><ul>{refs_html}</ul></section>' if refs_html else ""}
</div>"""
    return _inst_document(
        depth=depth,
        title=seo.get("title", "Missão | Calculadoras de Enfermagem"),
        description=seo.get("description", ""),
        canonical_path="/missao",
        main_html=main,
        hashtags=page.get("hashtags"),
    )


def render_objective_page(page: dict, *, depth: int) -> str:
    seo = page.get("seo", {})
    sections_html = "".join(
        f"""<article class="inst-obj-card">
  <h3>{esc(s["title"])}</h3>
  <p>{esc(s["text"])}</p>
</article>"""
        for s in page.get("sections", [])
    )
    stats_html = "".join(
        f"""<div class="inst-stat"><strong>{esc(g["value"])}</strong><span>{esc(g["label"])}</span></div>"""
        for g in page.get("goals", [])
    )
    crumbs = render_breadcrumbs([("Institucional", route_href("/sobre", depth)), ("Objetivo do Site", None)], depth)
    main = f"""
{_render_inst_hero(page["hero"], depth=depth, variant="objective")}
<div class="section-container inst-body">
  {crumbs}
  <div class="inst-goals">{stats_html}</div>
  <section class="inst-block" aria-labelledby="obj-sections">
    <h2 id="obj-sections">Propósitos da plataforma</h2>
    <div class="inst-obj-grid">{sections_html}</div>
  </section>
</div>"""
    return _inst_document(
        depth=depth,
        title=seo.get("title", "Objetivo do Site"),
        description=seo.get("description", ""),
        canonical_path="/objetivo",
        main_html=main,
        hashtags=page.get("hashtags"),
    )


def render_accessibility_center(page: dict, *, depth: int) -> str:
    seo = page.get("seo", {})
    cards_html = "".join(
        f"""<article class="inst-a11y-card">
  <h3>{esc(c["title"])}</h3>
  <p>{esc(c["text"])}</p>
</article>"""
        for c in page.get("commitments", [])
    )
    features_html = "".join(f"<li>{esc(f)}</li>" for f in page.get("features", []))
    cta = page.get("cta", {})
    cta_href = route_href(cta.get("href", "/fale-conosco"), depth)
    crumbs = render_breadcrumbs([("Institucional", route_href("/sobre", depth)), ("Acessibilidade", None)], depth)
    main = f"""
{_render_inst_hero(page["hero"], depth=depth, variant="accessibility")}
<div class="section-container inst-body">
  {crumbs}
  <div class="inst-wcag-badge" aria-label="Conformidade WCAG">{esc(page.get("wcag_badge", "WCAG 2.2 AA"))}</div>
  <section class="inst-block" aria-labelledby="a11y-commitments">
    <h2 id="a11y-commitments">Nossos compromissos</h2>
    <div class="inst-a11y-grid">{cards_html}</div>
  </section>
  {f'<section class="inst-block"><h2>Recursos disponíveis</h2><ul class="inst-features-list">{features_html}</ul></section>' if features_html else ""}
  <aside class="inst-cta-card">
    <h2>{esc(cta.get("title", ""))}</h2>
    <p>{esc(cta.get("text", ""))}</p>
    <a class="btn-primary-lg" href="{esc(cta_href)}">{esc(cta.get("btn_label", "Contato"))}</a>
  </aside>
</div>"""
    return _inst_document(
        depth=depth,
        title=seo.get("title", "Acessibilidade"),
        description=seo.get("description", ""),
        canonical_path="/acessibilidade",
        main_html=main,
        hashtags=page.get("hashtags"),
    )


def render_contact_page(page: dict, *, depth: int, canonical_path: str = "/contato") -> str:
    seo = page.get("seo", {})
    form = page.get("form", {})
    info_html = "".join(
        f"""<article class="inst-contact-card">
  <div class="inst-contact-card__icon">{_inst_icon(item.get("icon", "support"))}</div>
  <h3>{esc(item["title"])}</h3>
  <p>{esc(item["text"])}</p>
  <a href="mailto:{esc(item.get("email", "contato@calculadorasdeenfermagem.com.br"))}">{esc(item.get("email", ""))}</a>
</article>"""
        for item in page.get("info", [])
    )
    options = "".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in form.get("subjects", []))
    crumbs = render_breadcrumbs([("Institucional", route_href("/sobre", depth)), ("Fale conosco", None)], depth)
    main = f"""
{_render_inst_hero(page["hero"], depth=depth, variant="contact")}
<div class="section-container inst-body inst-body--contact">
  {crumbs}
  <div class="inst-contact-grid">
    <div class="inst-contact-info">{info_html}</div>
    <form class="inst-contact-form" data-contact-form novalidate>
      <h2>Envie sua mensagem</h2>
      <p class="inst-contact-form__hint">{esc(form.get("response_time", ""))}</p>
      <label class="inst-field"><span>Nome completo</span><input type="text" name="nome" required autocomplete="name" placeholder="Seu nome"></label>
      <label class="inst-field"><span>E-mail</span><input type="email" name="email" required autocomplete="email" placeholder="seu@email.com"></label>
      <label class="inst-field"><span>Assunto</span><select name="assunto" required>{options}</select></label>
      <label class="inst-field"><span>Mensagem</span><textarea name="mensagem" rows="5" required placeholder="Escreva sua mensagem…"></textarea></label>
      <button type="submit" class="btn-primary-lg">{esc(form.get("submit_label", "Enviar"))}</button>
      <p class="inst-contact-form__status" data-contact-status role="status" aria-live="polite" hidden></p>
    </form>
  </div>
</div>"""
    return _inst_document(
        depth=depth,
        title=seo.get("title", "Fale Conosco"),
        description=seo.get("description", ""),
        canonical_path=canonical_path,
        main_html=main,
        hashtags=page.get("hashtags"),
    )


def render_sitemap_page(page: dict, *, depth: int, extra_links: list[tuple[str, str]] | None = None) -> str:
    seo = page.get("seo", {})
    columns_html = ""
    for col in page.get("columns", []):
        links = "".join(
            f'<li><a href="{esc(route_href(link["href"], depth))}">{esc(link["label"])}</a></li>'
            for link in col.get("links", [])
        )
        columns_html += f"""<div class="inst-sitemap-col">
  <h3>{esc(col["title"])}</h3>
  <ul>{links}</ul>
</div>"""
    cta = page.get("search_cta", {})
    crumbs = render_breadcrumbs([("Mapa do site", None)], depth)
    extra_html = ""
    if extra_links:
        items = ""
        for label, href in extra_links[:120]:
            if href.startswith("/") or href.startswith("http"):
                link_href = route_href(href, depth)
            else:
                link_href = route_href(f"/{href.replace('index.html', '').rstrip('/')}", depth) if "/" in href else route_href(f"/{href}", depth)
            items += f'<li><a href="{esc(link_href)}">{esc(label)}</a></li>'
        extra_html = f"""<section class="inst-block" aria-labelledby="map-all-pages">
  <h2 id="map-all-pages">Todas as páginas geradas</h2>
  <ul class="inst-sitemap-all">{items}</ul>
</section>"""
    main = f"""
{_render_inst_hero(page["hero"], depth=depth, variant="sitemap")}
<div class="section-container inst-body">
  {crumbs}
  <div class="inst-sitemap-grid">{columns_html}</div>
  {extra_html}
  <aside class="inst-search-cta">
    <h2>{esc(cta.get("title", ""))}</h2>
    <p>{esc(cta.get("text", ""))}</p>
    <form class="inst-search-cta__form" action="{esc(route_href(cta.get("search_href", "/busca"), depth))}" method="get" role="search">
      <input type="search" name="q" placeholder="{esc(cta.get("placeholder", "Buscar…"))}" aria-label="Buscar na plataforma">
      <button type="submit" class="btn-primary-sm">{esc(cta.get("btn_search", "Buscar"))}</button>
    </form>
    <a class="inst-search-cta__link" href="{esc(route_href(cta.get("contact_href", "/fale-conosco"), depth))}">{esc(cta.get("btn_contact", "Contato"))} →</a>
  </aside>
</div>"""
    return _inst_document(
        depth=depth,
        title=seo.get("title", "Mapa do Site"),
        description=seo.get("description", ""),
        canonical_path="/mapa-site",
        main_html=main,
        hashtags=page.get("hashtags"),
    )


def render_search_page(page: dict, *, depth: int) -> str:
    seo = page.get("seo", {})
    tags = page.get("popular_tags", [])
    tags_html = "".join(
        f'<button type="button" class="search-tag" data-search-tag="{esc(t.lstrip("#"))}">{esc(t)}</button>'
        for t in tags
    )
    crumbs = render_breadcrumbs([("Busca", None)], depth)
    main = f"""
{_render_inst_hero(page["hero"], depth=depth, variant="search")}
<div class="section-container inst-body">
  {crumbs}
  <form class="search-page-form" role="search" data-search-page>
    <label class="visually-hidden" for="search-page-input">Buscar na plataforma</label>
    <div class="search-page-form__row">
      <input id="search-page-input" type="search" name="q" placeholder="{esc(page.get("placeholder", "Buscar…"))}" autocomplete="off" data-search-page-input>
      <button type="submit" class="btn-primary-lg">Buscar</button>
    </div>
    <div class="search-page-tags" role="group" aria-label="Hashtags populares">
      <span class="search-page-tags__label">Filtrar por hashtag:</span>
      {tags_html}
    </div>
    <div class="search-page-results" data-search-page-results aria-live="polite"></div>
  </form>
</div>"""
    return _inst_document(
        depth=depth,
        title=seo.get("title", "Busca"),
        description=seo.get("description", ""),
        canonical_path="/busca",
        main_html=main,
        hashtags=page.get("hashtags"),
    )


def render_about_page(page: dict, *, depth: int) -> str:
    seo = page.get("seo", {})
    hero = page["hero"]
    intro = page.get("intro", {})
    commitment = page.get("commitment", {})
    creator = page.get("creator", {})

    bio_paragraphs = creator.get("bio", [])
    if isinstance(bio_paragraphs, str):
        bio_paragraphs = [bio_paragraphs]
    bio_html = "".join(f"<p>{esc(p)}</p>" for p in bio_paragraphs)

    highlights = creator.get("highlights", [])
    highlights_html = ""
    if highlights:
        items = "".join(f"<li>{esc(h)}</li>" for h in highlights)
        highlights_html = f'<ul class="inst-creator__highlights">{items}</ul>'

    creator_img = image_href(depth, creator.get("image", "about_creator.webp"))
    cta_primary = creator.get("cta_primary", {})
    cta_secondary = creator.get("cta_secondary", {})
    cta_html = ""
    if cta_primary or cta_secondary:
        links = []
        if cta_primary:
            links.append(
                f'<a class="btn-primary-sm" href="{esc(route_href(cta_primary.get("href", "/missao"), depth))}">'
                f'{esc(cta_primary.get("label", "Missão"))}</a>'
            )
        if cta_secondary:
            links.append(
                f'<a class="btn-outline" href="{esc(route_href(cta_secondary.get("href", "/fale-conosco"), depth))}">'
                f'{esc(cta_secondary.get("label", "Fale conosco"))}</a>'
            )
        cta_html = f'<div class="inst-creator__cta">{"".join(links)}</div>'

    creator_html = ""
    if creator:
        creator_html = f"""
  <section class="inst-block inst-creator" aria-labelledby="sec-criador">
    <h2 id="sec-criador">{esc(creator.get("section_title", "Quem idealizou a plataforma"))}</h2>
    <div class="inst-creator__grid">
      <figure class="inst-creator__media">
        <img src="{esc(creator_img)}" alt="{esc(creator.get("image_alt", creator.get("name", "")))}" width="320" height="400" loading="lazy">
      </figure>
      <div class="inst-creator__body">
        <p class="inst-creator__role">{esc(creator.get("role", ""))}</p>
        <h3 class="inst-creator__name">{esc(creator.get("name", ""))}</h3>
        {bio_html}
        {highlights_html}
        {cta_html}
      </div>
    </div>
  </section>"""

    crumbs = render_breadcrumbs([("Sobre Nós", None)], depth)
    main = f"""
{_render_inst_hero(hero, depth=depth, variant="about")}
<div class="section-container inst-body">
  {crumbs}
  <section class="inst-block" aria-labelledby="sec-quem-somos">
    <h2 id="sec-quem-somos">{esc(intro.get("title", "Quem somos"))}</h2>
    <div class="inst-card">{esc(intro.get("text", ""))}</div>
  </section>
  <section class="inst-block inst-block--vision" aria-labelledby="sec-compromisso">
    <h2 id="sec-compromisso">{esc(commitment.get("title", "Compromisso"))}</h2>
    <div class="inst-card inst-card--dark">{esc(commitment.get("text", ""))}</div>
  </section>
  {creator_html}
</div>"""
    return _inst_document(
        depth=depth,
        title=seo.get("title", "Sobre Nós | Calculadoras de Enfermagem"),
        description=seo.get("description", ""),
        canonical_path="/sobre",
        main_html=main,
        hashtags=page.get("hashtags"),
    )
