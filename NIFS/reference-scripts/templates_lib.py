"""Specialized page templates — mockups Calculadoras de Enfermagem 2026 (sidebar, dashboard, scrape hubs)."""
from __future__ import annotations

import json
from typing import Any

from website_lib import SITE_NAME, brand_text, esc, render_breadcrumbs, render_document, route_href, slugify

TEMPLATES_CSS = "assets/css/templates.css"


def _css(depth: int, *extra: str) -> list[str]:
    prefix = "../" * depth if depth else ""
    files = [f"{prefix}{TEMPLATES_CSS}"]
    files.extend(f"{prefix}{e}" if not e.startswith("../") else e for e in extra)
    return files


def _crumbs(items: list[tuple[str, str | None]], depth: int) -> str:
    return f'<div class="section-container tpl-breadcrumb">{render_breadcrumbs(items, depth)}</div>'


def render_sidebar_tool_page(
    *,
    depth: int,
    title: str,
    description: str,
    canonical_path: str,
    breadcrumb: list[tuple[str, str | None]],
    sidebar_title: str,
    sidebar_links: list[tuple[str, str, bool]],
    main_html: str,
    hero_subtitle: str = "",
) -> str:
    nav = "".join(
        f'<a class="sidebar-nav__link{" is-active" if active else ""}" href="{esc(href)}">{esc(label)}</a>'
        for label, href, active in sidebar_links
    )
    main = f"""
{_crumbs(breadcrumb, depth)}
<div class="tpl-sidebar-page section-container">
  <header class="tpl-page-head">
    <h1>{esc(title)}</h1>
    {f"<p>{esc(hero_subtitle)}</p>" if hero_subtitle else ""}
  </header>
  <div class="tpl-sidebar-layout">
    <aside class="sidebar-nav card">
      <h2 class="sidebar-nav__title">{esc(sidebar_title)}</h2>
      <nav class="sidebar-nav__list">{nav}</nav>
    </aside>
    <div class="tpl-sidebar-main">{main_html}</div>
  </div>
</div>"""
    return render_document(
        depth=depth, title=title, description=description, canonical_path=canonical_path,
        main_html=main, extra_css=_css(depth, "assets/css/hub.css"), main_class="site-main tpl-main",
    )


_NNN_CONFIG = {
    "nanda": {
        "code_key": "nanda_code", "route": "/nanda",
        "noun": "diagnóstico", "noun_plural": "diagnósticos",
        "col": "Diagnóstico", "list_label": "Características definidoras",
        "title": "Biblioteca NANDA-I 2026", "framework": "NANDA-I 2026",
        "placeholder": "Buscar diagnóstico NANDA-I…",
    },
    "nic": {
        "code_key": "nic_code", "route": "/nic",
        "noun": "intervenção", "noun_plural": "intervenções",
        "col": "Intervenção", "list_label": "Atividades",
        "title": "Biblioteca NIC 2026", "framework": "NIC 2026",
        "placeholder": "Buscar intervenção NIC…",
    },
    "noc": {
        "code_key": "noc_code", "route": "/noc",
        "noun": "resultado", "noun_plural": "resultados",
        "col": "Resultado", "list_label": "Indicadores",
        "title": "Biblioteca NOC 2026", "framework": "NOC 2026",
        "placeholder": "Buscar resultado NOC…",
    },
}


def build_nnn_linkage_index(linkages: list[dict], nanda: list[dict],
                            nic: list[dict], noc: list[dict]) -> dict:
    """Cross-reference maps + display names so each taxonomy detail can link
    to its associated items via the NNN linkage table."""
    nanda_name = {d.get("nanda_code"): d.get("name_pt") or d.get("name") for d in nanda}
    nic_name = {i.get("nic_code"): i.get("name_pt") or i.get("name") for i in nic}
    noc_name = {o.get("noc_code"): o.get("name_pt") or o.get("name") for o in noc}
    dx2nic: dict[str, set] = {}
    dx2noc: dict[str, set] = {}
    nic2dx: dict[str, set] = {}
    noc2dx: dict[str, set] = {}
    for lk in linkages:
        dx = (lk.get("diagnosis_code") or "").replace("NANDA.", "")
        ic = (lk.get("intervention_code") or "").replace("NIC.", "")
        oc = (lk.get("outcome_code") or "").replace("NOC.", "")
        if dx and ic:
            dx2nic.setdefault(dx, set()).add(ic)
            nic2dx.setdefault(ic, set()).add(dx)
        if dx and oc:
            dx2noc.setdefault(dx, set()).add(oc)
            noc2dx.setdefault(oc, set()).add(dx)
    return {
        "names": {"nanda": nanda_name, "nic": nic_name, "noc": noc_name},
        "dx2nic": dx2nic, "dx2noc": dx2noc, "nic2dx": nic2dx, "noc2dx": noc2dx,
    }


def _nnn_links_for(kind: str, code: str, idx: dict, depth: int) -> list[dict]:
    if not idx:
        return []
    out = []
    if kind == "nanda":
        for ic in sorted(idx["dx2nic"].get(code, []))[:6]:
            out.append({"label": f"NIC {ic} — {idx['names']['nic'].get(ic, ic)}",
                        "href": route_href("/nic", depth) + f"?q={ic}"})
        for oc in sorted(idx["dx2noc"].get(code, []))[:6]:
            out.append({"label": f"NOC {oc} — {idx['names']['noc'].get(oc, oc)}",
                        "href": route_href("/noc", depth) + f"?q={oc}"})
    else:
        m = idx["nic2dx"] if kind == "nic" else idx["noc2dx"]
        for dx in sorted(m.get(code, []))[:8]:
            out.append({"label": f"NANDA {dx} — {idx['names']['nanda'].get(dx, dx)}",
                        "href": route_href("/nanda", depth) + f"?q={dx}"})
    return out


def render_nnn_library(records: list[dict], *, kind: str = "nanda", depth: int,
                       linkage_index: dict | None = None) -> str:
    cfg = _NNN_CONFIG[kind]
    code_key = cfg["code_key"]

    def domain_of(r: dict) -> str:
        return (r.get("domain_code", "").replace("NANDA.DOMAIN.", "")
                or r.get("domain", "") or "—")

    rows = []
    data = []
    for r in records:
        code = r.get(code_key) or r.get("diagnosis_code", "")
        name = r.get("name_pt") or r.get("name", "")
        rows.append(f"""
<tr data-nnn-row data-title="{esc((str(code) + ' ' + name).lower())}">
  <td><strong>{esc(code)}</strong></td>
  <td><a href="#" data-nnn-select="{esc(code)}">{esc(name)}</a></td>
  <td><span class="hub-pill">{esc(domain_of(r))}</span></td>
  <td><button type="button" class="hub-bookmark" aria-label="Favoritar">☆</button></td>
</tr>""")
        if kind == "nanda":
            related = r.get("related_factors", [])
            lst = r.get("defining_characteristics", [])
        elif kind == "nic":
            related = [r.get("domain", "")]
            lst = r.get("activities", [])
        else:
            related = [x for x in [r.get("domain", ""), r.get("scale_type", "")] if x]
            lst = r.get("indicators", [])
        data.append({
            "code": code, "name": name, "definition": r.get("definition", ""),
            "related": related, "chars": lst, "list": lst,
            "listLabel": cfg["list_label"],
            "links": _nnn_links_for(kind, str(code), linkage_index, depth),
        })

    sidebar_links = [
        ("Diagnósticos (NANDA)", route_href("/nanda", depth), kind == "nanda"),
        ("Intervenções (NIC)", route_href("/nic", depth), kind == "nic"),
        ("Resultados (NOC)", route_href("/noc", depth), kind == "noc"),
        ("Mapeamentos NNN", route_href("/nanda", depth), False),
        ("Favoritos", "#", False),
    ]

    main = f"""
<div class="search-bar">
  <label class="visually-hidden" for="nnn-search">Buscar {esc(cfg['noun_plural'])}</label>
  <input id="nnn-search" type="search" placeholder="{esc(cfg['placeholder'])}" data-nnn-filter>
</div>
<div class="tpl-nnn-grid">
  <div class="data-table-wrap card">
    <table class="data-table">
      <thead><tr><th>Código</th><th>{esc(cfg['col'])}</th><th>Domínio</th><th></th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
  </div>
  <aside class="card tpl-nnn-detail" data-nnn-detail>
    <h2>Detalhe do {esc(cfg['noun'])}</h2>
    <p class="tpl-nnn-detail__hint">Selecione um {esc(cfg['noun'])} na lista para ver definição, {esc(cfg['list_label'].lower())} e mapeamentos NNN relacionados.</p>
  </aside>
</div>
<script type="application/json" id="nnn-data">{json.dumps(data, ensure_ascii=False)}</script>"""
    return render_sidebar_tool_page(
        depth=depth,
        title=f"{cfg['title']} | {SITE_NAME}",
        description=brand_text(f"{len(records)} {cfg['noun_plural']} de enfermagem catalogados Calculadoras de Enfermagem 2026 ({cfg['framework']})."),
        canonical_path=cfg["route"],
        breadcrumb=[(cfg["framework"], None)],
        sidebar_title="Classificações",
        sidebar_links=sidebar_links,
        hero_subtitle="Diagnósticos, intervenções e resultados integrados ao processo de enfermagem.",
        main_html=main,
    )


def render_feature_split(page: dict, *, depth: int) -> str:
    steps = "".join(
        f"""<li class="feature-step">
  <span class="feature-step__num">{i}</span>
  <div><strong>{esc(s["title"])}</strong><p>{esc(s.get("text", ""))}</p></div>
</li>"""
        for i, s in enumerate(page.get("steps", []), 1)
    )
    blocks = "".join(
        f'<div class="feature-block feature-block--{esc(b.get("color", "blue"))}"><span class="feature-block__letter">{esc(b["letter"])}</span><strong>{esc(b["title"])}</strong><p>{esc(b.get("text", ""))}</p></div>'
        for b in page.get("blocks", [])
    )
    main = f"""
{_crumbs([(page["title"], None)], depth)}
<section class="tpl-feature-split section-container">
  <div class="tpl-feature-split__intro card card-highlight">
    <h1>{esc(page["title"])}</h1>
    <p>{esc(page.get("subtitle", ""))}</p>
    <a class="btn-primary-sm" href="{esc(route_href(page.get("cta_href", "/ferramentas"), depth))}">{esc(page.get("cta", "Iniciar"))}</a>
  </div>
  <div class="tpl-feature-split__body">
    {f'<ol class="feature-steps">{steps}</ol>' if steps else f'<div class="feature-blocks">{blocks}</div>'}
  </div>
</section>"""
    return render_document(
        depth=depth, title=page["seo"]["title"], description=page["seo"]["description"],
        canonical_path=page["route"], main_html=main, extra_css=_css(depth), main_class="site-main tpl-main",
    )


def render_metrics_dashboard(page: dict, *, depth: int) -> str:
    metrics = "".join(
        f"""<article class="metric-card">
  <span class="metric-card__label">{esc(m["label"])}</span>
  <span class="metric-card__value">{esc(m["value"])}</span>
  <span class="metric-card__trend metric-card__trend--{esc(m.get("trend_dir", "up"))}">{esc(m.get("trend", ""))}</span>
</article>"""
        for m in page.get("metrics", [])
    )
    cats = "".join(f'<li>{esc(c)}</li>' for c in page.get("categories", []))
    main = f"""
{_crumbs([(page["title"], None)], depth)}
<div class="section-container tpl-dashboard">
  <header class="tpl-page-head"><h1>{esc(page["title"])}</h1><p>{esc(page.get("subtitle", ""))}</p></header>
  <div class="dashboard-grid dashboard-grid--metrics">{metrics}</div>
  <div class="tpl-dashboard__lower">
    <div class="card"><h2>Evolução dos indicadores</h2><p class="tpl-chart-placeholder">Gráfico interativo — integração BI em desenvolvimento.</p></div>
    <div class="card"><h2>Categorias</h2><ul class="tpl-cat-list">{cats}</ul></div>
  </div>
</div>"""
    return render_document(
        depth=depth, title=page["seo"]["title"], description=page["seo"]["description"],
        canonical_path=page["route"], main_html=main, extra_css=_css(depth), main_class="site-main tpl-main",
    )


def render_vaccine_calendar(page: dict, *, depth: int) -> str:
    rows = "".join(
        f"<tr><td>{esc(r['age'])}</td><td>{esc(r['vaccine'])}</td><td>{esc(r['dose'])}</td><td>{esc(r['prevents'])}</td></tr>"
        for r in page.get("schedule", [])
    )
    main = f"""
<div class="search-bar">
  <label class="visually-hidden" for="vac-search">Buscar vacina</label>
  <input id="vac-search" type="search" placeholder="Buscar vacina…" aria-label="Buscar vacina">
  <label class="visually-hidden" for="vac-age">Faixa etária</label>
  <select id="vac-age" aria-label="Faixa etária"><option>Criança</option><option>Adolescente</option><option>Adulto</option><option>Gestante</option></select>
</div>
<div class="data-table-wrap card">
  <table class="data-table"><thead><tr><th>Idade</th><th>Vacina</th><th>Dose</th><th>Doença prevenida</th></tr></thead><tbody>{rows}</tbody></table>
</div>"""
    sidebar = page.get("sidebar", ["Criança", "Adolescente", "Adulto", "Gestante"])
    return render_sidebar_tool_page(
        depth=depth, title=page["seo"]["title"], description=page["seo"]["description"],
        canonical_path=page["route"], breadcrumb=[("Calendário Vacinal", None)],
        sidebar_title="Faixas etárias",
        sidebar_links=[(l, "#", i == 0) for i, l in enumerate(sidebar)],
        hero_subtitle=page.get("subtitle", ""),
        main_html=main,
    )


def build_flashcard_items(flashcards: list[dict], depth: int) -> list[dict]:
    decks: dict[str, int] = {}
    for fc in flashcards:
        decks[fc.get("deck_code", "GERAL")] = decks.get(fc.get("deck_code", "GERAL"), 0) + 1
    labels = {
        "DECK.NANDA": ("NANDA-I", "sae", "SAE / NANDA"),
        "DECK.NIC": ("Intervenções NIC", "meds", "Medicação"),
        "DECK.NOC": ("Resultados NOC", "sae", "SAE / NANDA"),
        "DECK.DRUG": ("Farmacologia", "meds", "Medicação"),
        "DECK.TOOLS": ("Ferramentas clínicas", "icu", "UTI / Críticos"),
        "DECK.GLOSSARY": ("Glossário", "evidence", "Evidências GRADE"),
    }
    items = []
    for i, (deck, count) in enumerate(decks.items()):
        cat_id, label, theme = labels.get(deck, ("all", deck, "Enfermagem Geral"))
        slug = slugify(deck)
        items.append({
            "id": slug, "title": label, "description": f"{count} cartões · revisão espaçada",
            "badge": "Popular" if i < 2 else "", "category": label, "category_id": cat_id, "theme": theme,
            "updated": "2026", "updated_sort": "2026", "href": route_href(f"/flashcards/{slug}", depth),
            "views": max(200, 900 - i * 80), "featured": True,
            "question_count": count, "duration_min": max(10, count // 5), "difficulty": "Médio", "action_label": "Estudar",
        })
    return items


def render_flashcard_study(deck_code: str, cards: list[dict], *, depth: int, deck_label: str) -> str:
    sample = cards[0] if cards else {"front_pt": "Pergunta", "back_pt": "Resposta"}
    data = json.dumps([{"front": c.get("front_pt", ""), "back": c.get("back_pt", "")} for c in cards[:50]], ensure_ascii=False)
    main = f"""
{_crumbs([("Flashcards", route_href("/flashcards", depth)), (deck_label, None)], depth)}
<div class="section-container tpl-flashcard" data-flashcard-deck>
  <div class="tpl-flashcard__stats">
    <span>{len(cards)} cartões</span><span>Taxa de acerto: —</span><span>Dias de estudo: —</span>
  </div>
  <div class="tpl-flashcard__card card" data-flashcard-card>
    <p class="tpl-flashcard__side-label">FRENTE</p>
    <p class="tpl-flashcard__text" data-flashcard-front>{esc(sample.get("front_pt", ""))}</p>
    <p class="tpl-flashcard__side-label is-hidden" data-flashcard-back-label>VERSO</p>
    <p class="tpl-flashcard__text is-hidden" data-flashcard-back>{esc(sample.get("back_pt", ""))}</p>
  </div>
  <div class="tpl-flashcard__controls">
    <button type="button" class="btn-outline" data-flashcard-flip>Virar cartão</button>
    <button type="button" class="tpl-flashcard__rate tpl-flashcard__rate--hard" data-flashcard-rate="hard">Difícil</button>
    <button type="button" class="tpl-flashcard__rate tpl-flashcard__rate--good" data-flashcard-rate="good">Bom</button>
    <button type="button" class="tpl-flashcard__rate tpl-flashcard__rate--easy" data-flashcard-rate="easy">Fácil</button>
  </div>
  <script type="application/json" id="flashcard-data">{data}</script>
</div>"""
    return render_document(
        depth=depth, title=f"{deck_label} | Flashcards", description=f"Deck {deck_label} — {len(cards)} cartões.",
        canonical_path=f"/flashcards/{slugify(deck_code)}", main_html=main,
        extra_css=_css(depth), main_class="site-main tpl-main",
    )


def render_mindmap_page(page: dict, *, depth: int) -> str:
    nodes = page.get("nodes", [])
    center = nodes[0] if nodes else {"title": "Tema central", "color": "navy"}
    branches = "".join(
        f"""<div class="mindmap-node mindmap-node--{esc(n.get("color", "blue"))}">
  <strong>{esc(n["title"])}</strong>
  <ul>{"".join(f"<li>{esc(s)}</li>" for s in n.get("items", []))}</ul>
</div>"""
        for n in nodes[1:]
    )
    main = f"""
{_crumbs([(page["title"], None)], depth)}
<div class="section-container tpl-mindmap">
  <header class="tpl-page-head"><h1>{esc(page["title"])}</h1><p>{esc(page.get("subtitle", ""))}</p></header>
  <div class="tpl-mindmap__canvas card">
    <div class="mindmap-center">{esc(center["title"])}</div>
    <div class="mindmap-branches">{branches}</div>
  </div>
</div>"""
    return render_document(
        depth=depth, title=page["seo"]["title"], description=page["seo"]["description"],
        canonical_path=page["route"], main_html=main, extra_css=_css(depth), main_class="site-main tpl-main",
    )


def render_scrape_hub(page: dict, items: list[dict], *, depth: int) -> str:
    cards = "".join(
        f"""<article class="scrape-card card" data-scrape-item data-title="{esc(item.get("title", "").lower())}">
  <h3><a href="{esc(item.get("href", "#"))}">{esc(item["title"])}</a></h3>
  <p>{esc(item.get("org", ""))} · {esc(item.get("location", ""))}</p>
  <div class="scrape-card__meta">
    {''.join(f'<span class="hub-pill">{esc(t)}</span>' for t in item.get("tags", []))}
    <span>{esc(item.get("posted", ""))}</span>
  </div>
</article>"""
        for item in items
    )
    filters = page.get("filters", [])
    filter_html = "".join(
        f'<label>{esc(f["label"])} <input type="{"search" if f.get("type") == "search" else "text"}" placeholder="{esc(f.get("placeholder", ""))}" aria-label="{esc(f["label"])}"></label>'
        for f in filters
    )
    main = f"""
{_crumbs([(page["title"], None)], depth)}
<section class="tpl-scrape-hero card card-highlight section-container">
  <h1>{esc(page["title"])}</h1>
  <p>{esc(page.get("hero_text", ""))}</p>
  <form class="search-bar tpl-scrape-search">{filter_html}<button type="submit" class="btn-primary-sm">{esc(page.get("search_btn", "Buscar"))}</button></form>
</section>
<div class="section-container tpl-scrape-results"><div class="scrape-grid">{cards}</div></div>"""
    return render_document(
        depth=depth, title=page["seo"]["title"], description=page["seo"]["description"],
        canonical_path=page["route"], main_html=main, extra_css=_css(depth, "assets/css/hub.css"), main_class="site-main tpl-main",
    )


def render_forum_hub(topics: list[dict], posts: list[dict], *, depth: int) -> str:
    posts_by_topic: dict[str, dict] = {}
    for p in posts:
        posts_by_topic.setdefault(p.get("forum_topic_code", ""), p)
    cards = ""
    for t in topics:
        seed = posts_by_topic.get(t.get("forum_topic_code", ""), {})
        pinned = '<span class="hub-pill">Fixado</span>' if t.get("is_pinned") else ""
        cards += f"""<article class="scrape-card card" data-scrape-item data-title="{esc(t.get("title_pt", "").lower())}">
  <div class="scrape-card__meta">{pinned}<span class="hub-pill">{esc(t.get("specialty", ""))}</span></div>
  <h3>{esc(t.get("title_pt", ""))}</h3>
  <p>{esc(seed.get("body_pt", "Participe da discussão clínica desta especialidade."))}</p>
  <div class="scrape-card__meta"><span>{esc(t.get("post_count", 0))} mensagens</span><span>Comunidade</span></div>
</article>"""
    main = f"""
{_crumbs([("Fórum", None)], depth)}
<section class="tpl-scrape-hero card card-highlight section-container">
  <h1>Fórum da Comunidade</h1>
  <p>Discussões por especialidade entre estudantes, profissionais e gestores de enfermagem. {len(topics)} tópicos ativos.</p>
  <form class="search-bar tpl-scrape-search"><label>Buscar tópico <input type="search" placeholder="Ex.: UTI, SAE, farmacologia" aria-label="Buscar tópico"></label><button type="submit" class="btn-primary-sm">Buscar</button></form>
</section>
<div class="section-container tpl-scrape-results"><div class="scrape-grid">{cards}</div></div>"""
    return render_document(
        depth=depth, title=f"Fórum da Comunidade | {SITE_NAME}",
        description="Fórum de enfermagem — discussões por especialidade.",
        canonical_path="/forum", main_html=main,
        extra_css=_css(depth, "assets/css/hub.css"), main_class="site-main tpl-main",
    )


def render_trails_dashboard(paths: list[dict], page: dict, *, depth: int) -> str:
    rows = "".join(
        f"""<li class="trail-row card">
  <span class="trail-row__icon">{i + 1}</span>
  <div class="trail-row__body">
    <strong>{esc(p.get("title_pt", p.get("title", "")))}</strong>
    <span>{esc(p.get("path_code", ""))}</span>
    <div class="progress-bar"><div class="progress-bar__fill" style="width:{min(100, 20 + i * 15)}%"></div></div>
  </div>
  <span class="trail-row__pct">{min(100, 20 + i * 15)}%</span>
</li>"""
        for i, p in enumerate(paths[:8])
    )
    main = f"""
{_crumbs([(page["title"], None)], depth)}
<div class="section-container">
  <header class="tpl-page-head"><h1>{esc(page["title"])}</h1><p>{esc(page.get("subtitle", ""))}</p></header>
  <ul class="trail-list">{rows}</ul>
</div>"""
    return render_document(
        depth=depth, title=page["seo"]["title"], description=page["seo"]["description"],
        canonical_path=page["route"], main_html=main, extra_css=_css(depth), main_class="site-main tpl-main",
    )


def render_self_tests(assessments: list[dict], page: dict, *, depth: int) -> str:
    cards = "".join(
        f"""<article class="card feature-card">
  <h3>{esc(a.get("title_pt", a.get("assessment_code", "")))}</h3>
  <p>{esc(a.get("assessment_type", "formativa"))} · nota mínima {esc(a.get("passing_score_pct", 70))}%</p>
  <button type="button" class="btn-primary-sm">Iniciar teste</button>
</article>"""
        for a in assessments[:6]
    )
    main = f"""
{_crumbs([(page["title"], None)], depth)}
<div class="section-container">
  <header class="tpl-page-head"><h1>{esc(page["title"])}</h1><p>{esc(page.get("subtitle", ""))}</p></header>
  <div class="feature-grid">{cards}</div>
</div>"""
    return render_document(
        depth=depth, title=page["seo"]["title"], description=page["seo"]["description"],
        canonical_path=page["route"], main_html=main, extra_css=_css(depth), main_class="site-main tpl-main",
    )


def _wizard_field_html(field: dict) -> str:
    fid = esc(field["id"])
    label = esc(field["label"])
    req = " required" if field.get("required") else ""
    if field.get("type") == "select":
        opts = "".join(
            f'<option value="{esc(o["value"])}"{" selected" if o["value"] == field.get("default") else ""}>{esc(o["label"])}</option>'
            for o in field.get("options", [])
        )
        return f'<label for="{fid}">{label}<select id="{fid}" name="{fid}" data-wizard-field>{opts}</select></label>'
    if field.get("type") == "checkbox":
        checked = " checked" if field.get("default") else ""
        return f'<label class="tpl-wizard-check"><input type="checkbox" id="{fid}" name="{fid}" data-wizard-field{checked}> {label}</label>'
    if field.get("type") == "textarea":
        return f'<label for="{fid}">{label}<textarea id="{fid}" name="{fid}" rows="4" data-wizard-field placeholder="{esc(field.get("placeholder", ""))}"{req}></textarea></label>'
    ftype = "email" if field.get("type") == "email" else ("tel" if field.get("type") == "tel" else "text")
    if field.get("type") == "number":
        ftype = "number"
    default = field.get("default", "")
    val = f' value="{esc(str(default))}"' if default != "" and default is not None else ""
    prefix = f'<span class="tpl-wizard-prefix">{esc(field["prefix"])}</span>' if field.get("prefix") else ""
    suffix = f'<span class="tpl-wizard-suffix">{esc(field["suffix"])}</span>' if field.get("suffix") else ""
    return f'<label for="{fid}">{label}<div class="tpl-wizard-input-wrap">{prefix}<input type="{ftype}" id="{fid}" name="{fid}" data-wizard-field placeholder="{esc(field.get("placeholder", ""))}"{val}{req}>{suffix}</div></label>'


def render_cv_wizard(*, depth: int) -> str:
    steps = [
        {"id": "personal", "label": "Dados Pessoais", "fields": [
            {"id": "fullName", "label": "Nome completo", "type": "text", "required": True, "placeholder": "Mariana Silva de Oliveira"},
            {"id": "professionalTitle", "label": "Título profissional", "type": "text", "required": True, "placeholder": "Enfermeira"},
            {"id": "email", "label": "E-mail", "type": "email", "required": True},
            {"id": "phone", "label": "Telefone", "type": "tel", "required": True},
            {"id": "city", "label": "Cidade", "type": "text", "required": True},
            {"id": "state", "label": "Estado (UF)", "type": "text", "required": True},
            {"id": "professionalSummary", "label": "Resumo profissional", "type": "textarea"},
        ]},
        {"id": "experience", "label": "Experiência & Formação", "fields": [
            {"id": "education", "label": "Formação acadêmica", "type": "textarea", "placeholder": "Bacharelado em Enfermagem — USP · 2018"},
            {"id": "experience", "label": "Experiência profissional", "type": "textarea", "placeholder": "Hospital Santa Clara · UTI · 2021–Atual"},
        ]},
        {"id": "skills", "label": "Competências & Certificações", "fields": [
            {"id": "coren", "label": "COREN (número/UF)", "type": "text", "placeholder": "123456/SP"},
            {"id": "certifications", "label": "Certificações", "type": "textarea", "placeholder": "ACLS, PALS, BLS"},
            {"id": "skills", "label": "Competências", "type": "textarea", "placeholder": "SAE, UTI, Liderança, Excel"},
        ]},
        {"id": "template", "label": "Modelo & Layout", "fields": [
            {"id": "templateId", "label": "Modelo", "type": "select", "options": [
                {"value": "classic", "label": "Clássico — ATS otimizado"},
                {"value": "modern", "label": "Moderno — destaque clínico"},
                {"value": "minimal", "label": "Minimalista — concursos"},
            ], "default": "classic"},
        ]},
        {"id": "export", "label": "Preview & Exportar", "fields": []},
    ]
    stepper = "".join(
        f'<button type="button" class="tpl-wizard-step{" is-active" if i == 0 else ""}" data-wizard-goto="{i}"><span>{i + 1}</span> {esc(s["label"])}</button>'
        for i, s in enumerate(steps)
    )
    panels = []
    for i, step in enumerate(steps):
        fields = "".join(_wizard_field_html(f) for f in step.get("fields", []))
        extra = ""
        if step["id"] == "export":
            extra = """
<div class="tpl-cv-live-preview card" data-cv-live-preview aria-live="polite">
  <p class="tpl-cv-live-preview__hint">Preencha os passos anteriores para visualizar o currículo.</p>
</div>
<div class="tpl-wizard-export-actions">
  <button type="button" class="btn-outline" data-cv-print>Imprimir / PDF</button>
  <button type="button" class="btn-primary-sm" data-cv-copy>Copiar texto</button>
</div>"""
        panels.append(f'<div class="tpl-wizard-panel{" is-active" if i == 0 else ""}" data-wizard-panel="{i}"><h2>{esc(step["label"])}</h2>{fields}{extra}</div>')
    main = f"""
{_crumbs([("Gerador de Currículo", route_href("/curriculo", depth)), ("Criar currículo", None)], depth)}
<div class="tpl-wizard section-container" data-cv-wizard>
  <header class="tpl-wizard__head card">
    <div><h1>Gerador de Currículo</h1><p data-wizard-progress>Etapa 1 de {len(steps)}</p></div>
    <button type="button" class="btn-outline" data-wizard-save>Salvar rascunho</button>
  </header>
  <nav class="tpl-wizard__steps" aria-label="Etapas">{stepper}</nav>
  <div class="tpl-wizard__body">{"".join(panels)}</div>
  <footer class="tpl-wizard__nav card">
    <button type="button" class="btn-outline" data-wizard-prev disabled>Anterior</button>
    <span data-wizard-saved class="tpl-wizard-saved"></span>
    <button type="button" class="btn-primary-sm" data-wizard-next>Próximo</button>
  </footer>
</div>"""
    return render_document(
        depth=depth, title=f"Criar Currículo | {SITE_NAME}", description="Wizard de currículo profissional para enfermeiros.",
        canonical_path="/curriculo/criar", main_html=main, extra_css=_css(depth), main_class="site-main tpl-main",
    )


def render_sbar_wizard(*, depth: int) -> str:
    sbar_steps = [
        {"id": "situation", "label": "Situação", "color": "blue", "fields": [
            {"id": "situation", "label": "Descreva a situação atual", "type": "textarea", "required": True},
            {"id": "situationType", "label": "Tipo", "type": "select", "options": [
                {"value": "urgente", "label": "Urgente"}, {"value": "rotina", "label": "Rotina"}, {"value": "transferencia", "label": "Transferência"},
            ], "default": "urgente"},
            {"id": "priority", "label": "Prioridade", "type": "select", "options": [
                {"value": "critical", "label": "Crítica"}, {"value": "high", "label": "Alta"}, {"value": "medium", "label": "Média"}, {"value": "low", "label": "Baixa"},
            ], "default": "high"},
        ]},
        {"id": "background", "label": "Background", "color": "green", "fields": [
            {"id": "background", "label": "Contexto e histórico relevante", "type": "textarea", "required": True},
        ]},
        {"id": "assessment", "label": "Avaliação", "color": "orange", "fields": [
            {"id": "assessment", "label": "Sua avaliação clínica", "type": "textarea", "required": True},
        ]},
        {"id": "recommendation", "label": "Recomendação", "color": "purple", "fields": [
            {"id": "recommendation", "label": "Ações ou orientações solicitadas", "type": "textarea", "required": True},
        ]},
    ]
    patient_fields = [
        {"id": "patientName", "label": "Nome completo", "type": "text", "required": True},
        {"id": "patientAge", "label": "Idade", "type": "number", "required": True},
        {"id": "medicalRecord", "label": "Prontuário", "type": "text", "required": True},
        {"id": "diagnosis", "label": "Diagnóstico de admissão", "type": "text"},
        {"id": "bed", "label": "Leito", "type": "text"},
        {"id": "unit", "label": "Unidade", "type": "text"},
    ]
    patient_form = "".join(_wizard_field_html(f) for f in patient_fields)
    stepper = "".join(
        f'<button type="button" class="tpl-wizard-step tpl-wizard-step--{esc(s["color"])}{" is-active" if i == 0 else ""}" data-sbar-goto="{i}"><span>{i + 1}</span> {esc(s["label"])}</button>'
        for i, s in enumerate(sbar_steps)
    )
    panels = []
    for i, step in enumerate(sbar_steps):
        fields = "".join(_wizard_field_html(f) for f in step.get("fields", []))
        panels.append(f'<div class="tpl-wizard-panel{" is-active" if i == 0 else ""}" data-sbar-panel="{i}"><h2>{esc(step["label"])}</h2>{fields}</div>')
    main = f"""
{_crumbs([("SBAR", route_href("/sbar", depth)), ("Nova comunicação", None)], depth)}
<div class="tpl-wizard section-container" data-sbar-wizard>
  <header class="tpl-wizard__head card">
    <div><h1>SBAR — Comunicação Efetiva</h1><p data-sbar-patient-info>Identifique o paciente para iniciar.</p></div>
    <button type="button" class="btn-outline" data-sbar-save>Salvar rascunho</button>
  </header>
  <section class="tpl-wizard-panel is-active card" data-sbar-patient-form>
    <h2>Identificação do Paciente</h2>
    <form class="tpl-wizard-form" data-sbar-patient>{patient_form}<button type="submit" class="btn-primary-sm">Iniciar comunicação SBAR</button></form>
  </section>
  <div class="tpl-sbar-flow is-hidden" data-sbar-flow>
    <nav class="tpl-wizard__steps" aria-label="Etapas SBAR">{stepper}</nav>
    <div class="tpl-wizard__body">{"".join(panels)}</div>
    <div class="tpl-wizard-panel is-hidden card" data-sbar-summary></div>
    <footer class="tpl-wizard__nav card">
      <button type="button" class="btn-outline" data-sbar-prev disabled>Anterior</button>
      <button type="button" class="btn-primary-sm" data-sbar-next>Próximo</button>
    </footer>
  </div>
</div>"""
    return render_document(
        depth=depth, title=f"Novo SBAR | {SITE_NAME}", description="Wizard SBAR para comunicação clínica estruturada.",
        canonical_path="/sbar/novo", main_html=main, extra_css=_css(depth), main_class="site-main tpl-main",
    )


def render_labor_calculator_page(calc: dict, *, depth: int) -> str:
    sections_html = []
    for sec in calc.get("sections", []):
        fields = "".join(_wizard_field_html(f) for f in sec.get("fields", []))
        sections_html.append(f'<fieldset class="tpl-labor-section card"><legend>{esc(sec["title"])}</legend>{fields}</fieldset>')
    refs = "".join(f"<li>{esc(r)}</li>" for r in calc.get("references", []))
    config_json = json.dumps({"id": calc["id"], "title": calc["title"]}, ensure_ascii=False)
    main = f"""
{_crumbs([("Calculadoras Trabalhistas", route_href("/calculadoras-trabalhistas", depth)), (calc["title"], None)], depth)}
<div class="section-container tpl-labor-calc" data-labor-calc>
  <header class="tpl-page-head"><h1>{esc(calc["title"])}</h1><p>{esc(calc.get("description", ""))}</p></header>
  <form class="tpl-labor-form" data-labor-form>
    {"".join(sections_html)}
    <div class="tpl-labor-actions">
      <button type="button" class="btn-primary-sm" data-labor-calculate>Calcular</button>
      <button type="reset" class="btn-outline">Limpar</button>
    </div>
  </form>
  <section class="tpl-labor-results card is-hidden" data-labor-results aria-live="polite">
    <h2>Resultado</h2>
    <dl class="tpl-labor-results__list" data-labor-results-list></dl>
  </section>
  {f'<aside class="card tpl-labor-refs"><h2>Referências</h2><ul>{refs}</ul></aside>' if refs else ''}
  <script type="application/json" id="labor-calc-config">{config_json}</script>
</div>"""
    return render_document(
        depth=depth,
        title=f'{calc["title"]} | Calculadoras Trabalhistas',
        description=calc.get("description", ""),
        canonical_path=f'/calculadoras-trabalhistas/{calc["slug"]}',
        main_html=main, extra_css=_css(depth), main_class="site-main tpl-main",
    )


def render_labor_calculators_hub(hub: dict, calculators: list[dict], *, depth: int) -> str:
    from module_landing_lib import _crumbs, _render_benefits, _render_cta, _render_features, _render_hero, _render_related_tools

    cards = []
    for calc in calculators:
        href = route_href(f'/calculadoras-trabalhistas/{calc["slug"]}', depth)
        feats = "".join(f"<li>{esc(f)}</li>" for f in calc.get("features", [])[:4])
        pop = '<span class="hub-pill">Popular</span>' if calc.get("popular") else ""
        cards.append(f"""
<article class="mod-calc-card card mod-calc-card--{esc(calc.get("color", "teal"))}" data-calc-card>
  {pop}
  <h3><a href="{esc(href)}">{esc(calc["title"])}</a></h3>
  <p>{esc(calc.get("description", ""))}</p>
  <ul>{feats}</ul>
  <a class="btn-primary-sm" href="{esc(href)}">Calcular</a>
</article>""")
    calc_grid = f"""
<section class="mod-section section-container" id="calc-list">
  <header class="mod-section__head"><span class="mod-badge">Calculadoras</span><h2>Escolha a calculadora</h2></header>
  <div class="mod-calc-grid">{"".join(cards)}</div>
</section>"""
    page = {**hub, "route": hub.get("route", "/calculadoras-trabalhistas")}
    main = "".join([
        _crumbs([(hub["title"], None)], depth),
        _render_hero(page, depth),
        calc_grid,
        _render_features(hub.get("features", [])),
        _render_benefits([], hub.get("stats")),
        _render_related_tools(hub.get("related_tools", []), depth),
        _render_cta({"cta_block": {"title": "Confira seu holerite", "text": "Ferramentas gratuitas com legislação 2026.", "button": "Ver todas", "href": "#calc-list"}}, depth),
    ])
    seo = hub.get("seo", {})
    return render_document(
        depth=depth, title=seo.get("title", hub["title"]), description=seo.get("description", ""),
        canonical_path=hub.get("route", "/calculadoras-trabalhistas"),
        main_html=main, extra_css=_css(depth, "assets/css/hub.css"), main_class="site-main mod-main",
    )
