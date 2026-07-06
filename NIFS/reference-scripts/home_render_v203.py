"""Home page renderer — schema 2026.3.0."""
from __future__ import annotations

import json
from typing import Any

from website_lib import (
    _category_icon,
    _module_slug_from_href,
    _render_home_global_section,
    _render_home_pillar,
    esc,
    image_href,
    rel_prefix,
    render_document,
    route_href,
    tool_page_href,
)

PROFILE_SELECT_KEYS = {
    "estudante": "estudante",
    "profissional": "profissional",
    "enfermeiro_assistencial": "profissional",
    "enfermeiro_urgencia": "profissional",
    "gestor": "gestor",
    "docente": "academico",
    "academico": "academico",
    "instituicao": "gestor",
}


def _render_clinical_feed_card(config: dict, *, depth: int) -> str:
    badge = esc(config.get("badge") or config.get("title", "Atualizações clínicas"))
    more_label = esc(config.get("more_label") or config.get("view_all_label", "Ver mais"))
    more_href = esc(route_href(config.get("more_href") or config.get("view_all_href", "/dicas"), depth))
    return f"""
<aside class="home-daily-tip home-clinical-feed" data-daily-tip data-clinical-feed aria-labelledby="home-clinical-feed-title">
  <div class="home-daily-tip__head">
    <span class="home-daily-tip__badge">{badge}</span>
    <time class="home-daily-tip__date" data-daily-tip-date datetime=""></time>
  </div>
  <div class="home-daily-tip__body">
    <div class="home-daily-tip__icon" data-daily-tip-icon aria-hidden="true"></div>
    <div>
      <h2 id="home-clinical-feed-title" class="home-daily-tip__title" data-daily-tip-title></h2>
      <p class="home-daily-tip__text" data-daily-tip-text></p>
    </div>
  </div>
  <a class="home-daily-tip__link" href="{more_href}" data-daily-tip-more>{more_label} →</a>
</aside>"""


def _render_hero_section(home: dict, *, depth: int, feed_html: str) -> str:
    hero = home["hero"]
    hero_img = image_href(depth, hero.get("image", "homepage-hero.webp"))
    hero_alt = esc(hero.get("image_alt", "Profissional de enfermagem em ambiente clínico"))
    bg = hero.get("background") or {}
    hero_style = ""
    if bg:
        cs = esc(bg.get("color_start", "#002d62"))
        cm = esc(bg.get("color_mid", "#0a1628"))
        ce = esc(bg.get("color_end", "#334e68"))
        hero_style = f' style="--home-hero-bg-start:{cs};--home-hero-bg-mid:{cm};--home-hero-bg-end:{ce};"'

    title_html = esc(hero["title"])
    if hero.get("title_accent"):
        title_html += f' <span class="home-hero__title-accent">{esc(hero["title_accent"])}</span>'

    stats_html = "".join(
        f'<div class="home-stat"><div class="home-stat__value">{esc(s["value"])}</div>'
        f'<div class="home-stat__label">{esc(s["label"])}</div></div>'
        for s in hero.get("stats", [])
    )

    cta_primary = hero.get("cta_primary", {})
    cta_secondary = hero.get("cta_secondary", {})
    actions_html = ""
    if cta_primary:
        actions_html += (
            f'<a class="btn-primary-lg" href="{esc(route_href(cta_primary.get("href", "/ferramentas"), depth))}">'
            f'{esc(cta_primary.get("label", "Explorar"))} →</a>'
        )
    if cta_secondary:
        actions_html += (
            f'<a class="btn-outline-lg" href="{esc(route_href(cta_secondary.get("href", "/sobre"), depth))}">'
            f'{esc(cta_secondary.get("label", "Conhecer"))}</a>'
        )

    return f"""
<section class="home-hero"{hero_style} aria-labelledby="home-hero-title">
  <div class="section-container home-hero__grid">
    <div class="home-hero__content">
      <h1 id="home-hero-title" class="home-hero__title">{title_html}</h1>
      <p class="home-hero__subtitle" data-ce-profile-hero-subtitle>{esc(hero["subtitle"])}</p>
      <div class="home-hero__stats">{stats_html}</div>
      {f'<div class="home-hero__actions">{actions_html}</div>' if actions_html else ''}
    </div>
    <div class="home-hero__media">
      {feed_html}
      <img src="{esc(hero_img)}" alt="{hero_alt}" width="480" height="420" loading="eager" decoding="async">
    </div>
  </div>
</section>"""


def _render_search_section(home: dict, *, depth: int) -> str:
    search = home["search"]
    return f"""
<div class="home-search-wrap">
  <div class="section-container">
    <form class="home-search" role="search" data-home-search>
      <label class="home-search__label" for="home-search-input" data-ce-profile-search-label>{esc(search["label"])}</label>
      <div class="home-search__row">
        <div class="home-search__input-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input id="home-search-input" type="search" name="q" placeholder="{esc(search["placeholder"])}" autocomplete="off" data-home-search-input data-ce-profile-search-input>
        </div>
        <button type="submit" class="home-search__btn">{esc(search["button"])}</button>
      </div>
      <div class="home-search__results" data-home-search-results aria-live="polite"></div>
    </form>
    <div class="ce-profile-strip" data-ce-profile-strip hidden>
      <span data-ce-profile-strip-label></span>
      <div class="ce-profile-strip__links" data-ce-profile-quick-links></div>
      <button type="button" class="ce-profile-strip__change" data-profile-change>Alterar perfil</button>
    </div>
  </div>
</div>"""


def _render_profile_selector(section: dict, *, depth: int) -> str:
    cards = ""
    for item in section.get("items", []):
        code = item.get("code", "")
        select_key = PROFILE_SELECT_KEYS.get(code, code)
        cards += f"""
<button type="button" class="home-profile-card" data-profile-select="{esc(select_key)}" data-home-profile-card>
  <span class="home-profile-card__icon">{_category_icon(item.get("icon", "user"))}</span>
  <span class="home-profile-card__label">{esc(item["label"])}</span>
  <span class="home-profile-card__desc">{esc(item.get("description", ""))}</span>
</button>"""
    if not cards:
        return ""
    return f"""
<section class="home-profile-selector" data-ce-profile-section="profile" aria-labelledby="home-profile-title">
  <div class="section-container">
    <div class="home-section-header">
      <h2 id="home-profile-title">{esc(section.get("title", ""))}</h2>
      <p>{esc(section.get("subtitle", ""))}</p>
    </div>
    <div class="home-profile-selector__grid">{cards}</div>
  </div>
</section>"""


def _render_featured_section(home: dict, *, depth: int, slug_map: dict[str, str]) -> str:
    featured = home.get("featured", {})
    featured_cards = ""
    for item in featured.get("items", []):
        if item.get("tool_code") and item["tool_code"] in slug_map:
            href = tool_page_href(slug_map[item["tool_code"]], "root")
        else:
            href = route_href(item.get("href", "/ferramentas"), depth)
        code_attr = f' data-ce-tool-code="{esc(item["tool_code"])}"' if item.get("tool_code") else ""
        featured_cards += f"""
<article class="home-tool-card"{code_attr}>
  <h3>{esc(item["title"])}</h3>
  <p>{esc(item["description"])}</p>
  <a class="home-tool-card__action" href="{esc(href)}">{esc(item["action_label"])}</a>
</article>"""
    return f"""
<section class="home-section" data-ce-profile-section="featured" aria-labelledby="home-featured-title">
  <div class="section-container">
    <div class="home-featured-header">
      <h2 id="home-featured-title">{esc(featured.get("title", "Mais utilizadas"))}</h2>
      <a href="{esc(route_href(featured.get("view_all_href", "/ferramentas"), depth))}">{esc(featured.get("view_all_label", "Ver todas"))} →</a>
    </div>
    <div class="home-featured-grid">{featured_cards}</div>
  </div>
</section>"""


def _render_nursing_os_map(section: dict, *, depth: int) -> str:
    nodes = ""
    for node in section.get("orbit_nodes", []):
        pos = esc(node.get("position", "right"))
        href = route_href(node.get("href", "/ferramentas"), depth)
        nodes += f"""
<a class="home-os-map__node home-os-map__node--{pos}" href="{esc(href)}" data-ce-profile-module="{esc(_module_slug_from_href(node.get("href", "")))}">
  <span class="home-os-map__node-icon">{_category_icon(node.get("icon", "calculator"))}</span>
  <strong>{esc(node["label"])}</strong>
  <span>{esc(node.get("description", ""))}</span>
</a>"""
    center = section.get("center_node") or {}
    cta = section.get("cta") or {}
    return f"""
<section class="home-os-map" data-ce-profile-section="ecosystem" aria-labelledby="home-os-map-title">
  <div class="section-container">
    <div class="home-section-header">
      <h2 id="home-os-map-title">{esc(section.get("title", ""))}</h2>
      <p>{esc(section.get("subtitle", ""))}</p>
    </div>
    <div class="home-os-map__orbital">
      <div class="home-os-map__center">
        <span class="home-os-map__center-icon">{_category_icon(center.get("icon", "network"))}</span>
        <strong>{esc(center.get("label", "Nursing OS"))}</strong>
      </div>
      {nodes}
    </div>
    <div class="home-os-map__cta">
      <a class="btn-primary-lg" href="{esc(route_href(cta.get("href", "/ferramentas"), depth))}">{esc(cta.get("label", "Explorar"))} →</a>
    </div>
  </div>
</section>"""


def _render_knowledge_hub(section: dict, *, depth: int) -> str:
    flow = "".join(
        f'<li class="home-knowledge__step"><span class="home-knowledge__step-num">{step.get("step", "")}</span>'
        f'<span class="home-knowledge__step-icon">{_category_icon(step.get("icon", "document"))}</span>'
        f'<span>{esc(step["label"])}</span></li>'
        for step in section.get("flow", [])
    )
    items = ""
    for item in section.get("items", []):
        href = route_href(item.get("href", "/educacao"), depth)
        items += f"""
<a class="home-knowledge__item" href="{esc(href)}" data-ce-profile-module="{esc(_module_slug_from_href(item.get("href", "")))}">
  <span class="home-knowledge__item-icon">{_category_icon(item.get("icon", "document"))}</span>
  <span>{esc(item["title"])}</span>
</a>"""
    cta = section.get("cta") or {}
    badge = section.get("badge") or {}
    badge_html = ""
    if badge:
        badge_href = route_href(badge.get("href", "/simulados"), depth)
        badge_html = f"""
<div class="home-knowledge__badge">
  <strong>{esc(badge.get("title", ""))}</strong>
  <a class="btn-primary-sm" href="{esc(badge_href)}">{esc(badge.get("button_label", "Acessar"))}</a>
</div>"""
    img_html = ""
    if section.get("image"):
        img = image_href(depth, section["image"])
        alt = esc(section.get("image_alt", ""))
        img_html = f'<img class="home-knowledge__photo" src="{esc(img)}" alt="{alt}" width="280" height="220" loading="lazy">'
    return f"""
<section class="home-knowledge" data-ce-profile-section="education" aria-labelledby="home-knowledge-title">
  <div class="section-container home-knowledge__grid">
    <div class="home-knowledge__main">
      <h2 id="home-knowledge-title">{esc(section.get("title", ""))}</h2>
      <p class="home-knowledge__subtitle">{esc(section.get("subtitle", ""))}</p>
      <ol class="home-knowledge__flow">{flow}</ol>
      <div class="home-knowledge__items">{items}</div>
      <a class="home-knowledge__cta" href="{esc(route_href(cta.get("href", "/educacao"), depth))}">{esc(cta.get("label", "Iniciar"))} →</a>
    </div>
    <div class="home-knowledge__aside">
      {img_html}
      {badge_html}
    </div>
  </div>
</section>"""


def _render_card_grid_section(
    section: dict,
    *,
    depth: int,
    section_class: str,
    profile_section: str,
    title_id: str,
    with_desc: bool = False,
) -> str:
    cards = ""
    for item in section.get("items", []):
        href = route_href(item.get("href", "/"), depth)
        desc = f'<p>{esc(item.get("description", ""))}</p>' if with_desc and item.get("description") else ""
        cards += f"""
<article class="home-card-grid__item">
  <a href="{esc(href)}" data-ce-profile-module="{esc(_module_slug_from_href(item.get("href", "")))}">
    <span class="home-card-grid__icon">{_category_icon(item.get("icon", "document"))}</span>
    <h3>{esc(item["title"])}</h3>
    {desc}
  </a>
</article>"""
    if not cards:
        return ""
    view_all = ""
    if section.get("view_all_href"):
        view_all = (
            f'<a class="home-section-header__link" href="{esc(route_href(section["view_all_href"], depth))}">'
            f'{esc(section.get("view_all_label", "Ver todos"))} →</a>'
        )
    cta = section.get("cta") or {}
    cta_html = ""
    if cta.get("href"):
        cta_html = f'<a class="home-card-grid__cta" href="{esc(route_href(cta["href"], depth))}">{esc(cta.get("label", ""))} →</a>'
    return f"""
<section class="home-card-grid {section_class}" data-ce-profile-section="{profile_section}" aria-labelledby="{title_id}">
  <div class="section-container">
    <div class="home-section-header home-section-header--split">
      <div>
        <h2 id="{title_id}">{esc(section.get("title", ""))}</h2>
        <p>{esc(section.get("subtitle", ""))}</p>
      </div>
      {view_all}
    </div>
    <div class="home-card-grid__items">{cards}</div>
    {cta_html}
  </div>
</section>"""


def _render_competency_track(section: dict, *, depth: int) -> str:
    tracks = "".join(
        f'<span class="home-competency__track">{_category_icon(t.get("icon", "tool"))}{esc(t["label"])}</span>'
        for t in section.get("tracks", [])
    )
    init = section.get("initial_assessment") or {}
    cta = section.get("cta") or {}
    return f"""
<section class="home-competency" data-ce-profile-section="competency" aria-labelledby="home-competency-title">
  <div class="section-container">
    <div class="home-section-header">
      <h2 id="home-competency-title">{esc(section.get("title", ""))}</h2>
      <p>{esc(section.get("subtitle", ""))}</p>
    </div>
    <div class="home-competency__tracks">{tracks}</div>
    <div class="home-competency__actions">
      <a class="btn-outline-lg" href="{esc(route_href(init.get("href", "/trilhas"), depth))}">{esc(init.get("label", ""))}</a>
      <a class="btn-primary-lg" href="{esc(route_href(cta.get("href", "/trilhas"), depth))}">{esc(cta.get("label", ""))} →</a>
    </div>
  </div>
</section>"""


def _render_ai_assistant(section: dict, *, depth: int) -> str:
    caps = "".join(
        f'<li><span>{_category_icon(c.get("icon", "sparkles"))}</span>{esc(c["label"])}</li>'
        for c in section.get("capabilities", [])
    )
    cta = section.get("cta") or {}
    return f"""
<section class="home-ai" aria-labelledby="home-ai-title">
  <div class="section-container home-ai__grid">
    <div>
      <h2 id="home-ai-title">{esc(section.get("title", ""))}</h2>
      <p>{esc(section.get("subtitle", ""))}</p>
      <ul class="home-ai__capabilities">{caps}</ul>
      <p class="home-ai__disclaimer">{esc(section.get("disclaimer", ""))}</p>
      <a class="btn-primary-lg" href="{esc(route_href(cta.get("href", "/ferramentas"), depth))}">{esc(cta.get("label", ""))} →</a>
    </div>
  </div>
</section>"""


def _render_metrics_section(section: dict, *, depth: int, section_class: str, title_id: str) -> str:
    metrics = ""
    for m in section.get("metrics", []):
        val = m.get("value", "—")
        suffix = esc(m.get("suffix", ""))
        metrics += f"""
<div class="home-metrics__item" data-metric-binding="{esc(m.get("binding", ""))}">
  <span class="home-metrics__icon">{_category_icon(m.get("icon", "chart"))}</span>
  <strong class="home-metrics__value">{esc(val)}{suffix}</strong>
  <span class="home-metrics__label">{esc(m["label"])}</span>
</div>"""
    cta = section.get("cta") or {}
    cta_html = ""
    if cta.get("href"):
        cta_html = f'<a class="home-metrics__cta" href="{esc(route_href(cta["href"], depth))}">{esc(cta.get("label", ""))} →</a>'
    return f"""
<section class="home-metrics {section_class}" aria-labelledby="{title_id}">
  <div class="section-container">
    <div class="home-section-header">
      <h2 id="{title_id}">{esc(section.get("title", ""))}</h2>
      <p>{esc(section.get("subtitle", ""))}</p>
    </div>
    <div class="home-metrics__grid">{metrics}</div>
    {cta_html}
  </div>
</section>"""


def _render_governance_center(section: dict, *, depth: int) -> str:
    items = ""
    for item in section.get("items", []):
        href = route_href(item.get("href", "/privacidade"), depth)
        items += f"""
<a class="home-governance__item" href="{esc(href)}">
  <span>{_category_icon(item.get("icon", "shield"))}</span>
  <span>{esc(item["title"])}</span>
</a>"""
    sci = section.get("scientific_credibility") or {}
    sci_items = ""
    for item in sci.get("items", []):
        href = route_href(item.get("href", "/sobre"), depth)
        sci_items += f'<li><a href="{esc(href)}">{esc(item["title"])}</a></li>'
    partners = sci.get("partners") or {}
    cats = "".join(f"<li>{esc(c)}</li>" for c in partners.get("categories", []))
    cta = section.get("cta") or {}
    return f"""
<section class="home-governance" aria-labelledby="home-governance-title">
  <div class="section-container">
    <div class="home-section-header">
      <h2 id="home-governance-title">{esc(section.get("title", ""))}</h2>
      <p>{esc(section.get("subtitle", ""))}</p>
    </div>
    <div class="home-governance__items">{items}</div>
    <div class="home-governance__science">
      <h3>{esc(sci.get("title", ""))}</h3>
      <p>{esc(sci.get("subtitle", ""))}</p>
      <ul>{sci_items}</ul>
      <div class="home-governance__partners">
        <strong>{esc(partners.get("title", ""))}</strong>
        <ul>{cats}</ul>
      </div>
    </div>
    <a class="home-governance__cta" href="{esc(route_href(cta.get("href", "/privacidade"), depth))}">{esc(cta.get("label", ""))} →</a>
  </div>
</section>"""


def _render_cta_final(section: dict, *, depth: int) -> str:
    primary = section.get("cta_primary") or {}
    secondary = section.get("cta_secondary") or {}
    return f"""
<section class="home-cta-final" aria-labelledby="home-cta-final-title">
  <div class="section-container home-cta-final__inner">
    <h2 id="home-cta-final-title">{esc(section.get("title", ""))}</h2>
    <p>{esc(section.get("subtitle", ""))}</p>
    <div class="home-cta-final__actions">
      <a class="btn-primary-lg" href="{esc(route_href(primary.get("href", "/login"), depth))}">{esc(primary.get("label", ""))} →</a>
      <a class="btn-outline-lg" href="{esc(route_href(secondary.get("href", "/ferramentas"), depth))}">{esc(secondary.get("label", ""))}</a>
    </div>
  </div>
</section>"""


def _render_management_block(home: dict, *, depth: int) -> str:
    mgmt = home.get("management_block")
    if not mgmt:
        return ""
    return f"""
<section class="home-pillars home-pillars--solo" aria-label="Gestão">
  <div class="section-container home-pillars__grid">{_render_home_pillar(mgmt, depth=depth, variant="management")}</div>
</section>"""


def _section_html(
    key: str,
    home: dict,
    *,
    depth: int,
    slug_map: dict[str, str],
    feed_html: str,
) -> str:
    if key == "hero":
        return _render_hero_section(home, depth=depth, feed_html=feed_html)
    if key == "search":
        return _render_search_section(home, depth=depth)
    if key == "profile_selector":
        return _render_profile_selector(home.get("profile_selector") or {}, depth=depth)
    if key == "featured":
        return _render_featured_section(home, depth=depth, slug_map=slug_map)
    if key == "nursing_os_map":
        return _render_nursing_os_map(home.get("nursing_os_map") or {}, depth=depth)
    if key == "knowledge_hub":
        return _render_knowledge_hub(home.get("knowledge_hub") or {}, depth=depth)
    if key == "clinical_cases":
        sec = home.get("clinical_cases") or {}
        return _render_card_grid_section(
            sec, depth=depth, section_class="home-clinical-cases",
            profile_section="cases", title_id="home-clinical-cases-title",
        )
    if key == "competency_track":
        return _render_competency_track(home.get("competency_track") or {}, depth=depth)
    if key == "ai_assistant":
        return _render_ai_assistant(home.get("ai_assistant") or {}, depth=depth)
    if key == "management_block":
        return _render_management_block(home, depth=depth)
    if key == "patient_safety_center":
        sec = home.get("patient_safety_center") or {}
        return _render_card_grid_section(
            sec, depth=depth, section_class="home-safety",
            profile_section="safety", title_id="home-safety-title",
        )
    if key == "occupational_health":
        sec = home.get("occupational_health") or {}
        return _render_card_grid_section(
            sec, depth=depth, section_class="home-occupational",
            profile_section="occupational", title_id="home-occupational-title", with_desc=True,
        )
    if key == "impact_dashboard":
        sec = home.get("impact_dashboard") or {}
        return _render_metrics_section(sec, depth=depth, section_class="home-impact", title_id="home-impact-title")
    if key == "global_platform":
        if home.get("global_platform"):
            return _render_home_global_section(home["global_platform"], depth=depth)
        return ""
    if key == "sustainability_block":
        sec = home.get("sustainability_block") or {}
        return _render_metrics_section(sec, depth=depth, section_class="home-sustainability", title_id="home-sustainability-title")
    if key == "governance_center":
        return _render_governance_center(home.get("governance_center") or {}, depth=depth)
    if key == "cta_final":
        return _render_cta_final(home.get("cta_final") or {}, depth=depth)
    return ""


def render_home_page_v203(
    home: dict,
    *,
    depth: int,
    title: str,
    description: str,
    slug_map: dict[str, str],
    daily_tips: dict | None = None,
    canonical_path: str = "/",
) -> str:
    feed_cfg = home.get("clinical_feed") or home.get("daily_tip") or {}
    feed_html = _render_clinical_feed_card(feed_cfg, depth=depth) if (daily_tips or feed_cfg) else ""

    order = home.get("page_sections_order") or [
        "hero", "search", "profile_selector", "featured", "nursing_os_map",
        "knowledge_hub", "clinical_cases", "competency_track", "ai_assistant",
        "management_block", "patient_safety_center", "occupational_health",
        "impact_dashboard", "global_platform", "sustainability_block",
        "governance_center", "cta_final",
    ]

    parts = [_section_html(key, home, depth=depth, slug_map=slug_map, feed_html=feed_html) for key in order]
    main = "".join(p for p in parts if p)

    tips_payload: dict[str, Any] = {"tips": [], "slug_map": slug_map}
    if daily_tips:
        tips_list = []
        for tip in daily_tips.get("tips", []):
            entry = dict(tip)
            code = entry.pop("tool_code", None)
            if code and code in slug_map:
                entry["tool_slug"] = slug_map[code]
            tips_list.append(entry)
        tips_payload = {
            "tips": tips_list,
            "more_link": daily_tips.get("more_link") or {},
            "slug_map": slug_map,
        }
    tips_json = json.dumps(tips_payload, ensure_ascii=False).replace("<", "\\u003c")
    main += f'\n<script type="application/json" id="daily-tips-data">{tips_json}</script>'

    prefix = rel_prefix(depth)
    return render_document(
        depth=depth,
        title=title,
        description=description,
        canonical_path=canonical_path,
        main_html=main,
        extra_css=[f"{prefix}assets/css/home.css", f"{prefix}assets/css/institutional.css"],
        main_class="site-main home-main home-main--v203",
    )
