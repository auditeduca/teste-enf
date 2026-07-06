"""Hub pages — Protocolos, Ferramentas (search + filters + featured sections)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from website_lib import (
    _category_icon,
    _svg_icon,
    esc,
    image_href,
    render_breadcrumbs,
    render_document,
    route_href,
    slugify,
    tool_page_href,
)

from tool_lib import build_tool_resource_index

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent


def _load_library_visual_assets() -> dict:
    path = ROOT / "datasets" / "content" / "library" / "library_visual_assets.json"
    if not path.is_file():
        return {}
    import json
    return json.loads(path.read_text(encoding="utf-8"))


def _library_thumbnail(guideline_code: str, assets: dict) -> str | None:
    code = (guideline_code or "").lower().replace(".", "-")
    for rec in assets.get("records", []):
        if rec.get("guideline_code") and rec.get("guideline_code", "").lower().replace(".", "-") == code:
            if rec.get("status") == "downloaded" and rec.get("local_path"):
                lp = rec["local_path"].replace("website/assets/", "")
                return lp
    return None

HUB_ICONS = {
    "grid": "calculator",
    "shield": "shield",
    "pill": "calculator",
    "heart": "chart",
    "bandage": "document",
    "clipboard": "clipboard",
    "calculator": "calculator",
    "brain": "brain",
    "alert": "shield",
    "virus": "leaf",
    "book": "book",
    "users": "users",
}

COLOR_CLASS = {
    "teal": "hub-color-teal",
    "blue": "hub-color-blue",
    "purple": "hub-color-purple",
    "red": "hub-color-red",
    "orange": "hub-color-orange",
    "green": "hub-color-green",
    "navy": "hub-color-navy",
    "pink": "hub-color-pink",
}


def _hub_icon(name: str) -> str:
    return _category_icon(HUB_ICONS.get(name, name))


def _format_date(iso: str | None) -> str:
    if not iso:
        return "2026"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        months = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
        return f"{dt.day} {months[dt.month - 1]}. {dt.year}"
    except ValueError:
        return iso[:10]


def _protocol_category(protocol: dict) -> tuple[str, str]:
    code = (protocol.get("protocol_code") or "").upper()
    title = (protocol.get("title") or "").lower()
    if any(x in code or x in title for x in ("MED", "MEDIC", "DOSE")):
        return "meds", "Administração de Medicamentos"
    if any(x in code or x in title for x in ("FALL", "QUEDA", "PRESS", "BRADEN", "WOUND", "FERID")):
        return "wounds", "Lesões e Feridas"
    if any(x in code or x in title for x in ("SEP", "ICU", "RASS", "CAM", "CRIT")):
        return "icu", "Cuidados Intensivos"
    if any(x in code or x in title for x in ("SAE", "NANDA", "PROCESS")):
        return "sae", "SAE / Processo de Enfermagem"
    return "safety", "Segurança do Paciente"


def _protocol_theme(protocol: dict) -> str:
    _, label = _protocol_category(protocol)
    if "Medicamentos" in label:
        return "Medicação"
    if "Intensivos" in label:
        return "UTI / Críticos"
    if "SAE" in label:
        return "SAE / NANDA"
    if "Lesões" in label:
        return "Sepse"
    return "Segurança do Paciente"


def _protocol_description(protocol: dict) -> str:
    title = protocol.get("title", "Protocolo")
    tools = protocol.get("related_tool_codes") or []
    if tools:
        return f"Protocolo institucional — integrado a {len(tools)} ferramentas clínicas relacionadas."
    return f"Protocolo institucional — {title}."


def _protocol_href(protocol: dict, slug_map: dict[str, str], depth: int) -> str:
    from protocol_lib import protocol_slug

    return route_href(f"/protocolos/{protocol_slug(protocol)}", depth)


def build_protocol_items(protocols: list[dict], slug_map: dict[str, str], depth: int) -> list[dict]:
    items = []
    for i, p in enumerate(protocols):
        cat_id, cat_label = _protocol_category(p)
        updated = p.get("updated_at") or p.get("created_at")
        badge = "Novo" if i < 3 else ("Atualizado" if i < 8 else "")
        items.append({
            "id": slugify(p.get("protocol_code", f"p-{i}")),
            "title": p.get("title", p.get("protocol_code", "")),
            "description": _protocol_description(p),
            "badge": badge,
            "category": cat_label,
            "category_id": cat_id,
            "theme": _protocol_theme(p),
            "filter_tags": [cat_label, _protocol_theme(p)],
            "updated": _format_date(updated),
            "updated_sort": updated or "",
            "href": _protocol_href(p, slug_map, depth),
            "views": max(120, 890 - i * 37),
            "featured": i < 4,
            "tool_codes": list(p.get("related_tool_codes") or []),
            "resource_type": "protocol",
        })
    return items


def _tool_category_id(tool: dict) -> tuple[str, str]:
    ttype = (tool.get("tool_type") or "").lower()
    cat = (tool.get("category") or "").lower()
    domain = (tool.get("domain") or "").lower()
    if ttype == "score" or "scale" in cat or "escala" in cat:
        return "score", "Escalas e Scores"
    if "fluid" in cat or "dose" in cat or "med" in domain:
        return "fluid", "Fluidos e Medicação"
    if "neuro" in domain or "neuro" in cat:
        return "neuro", "Neurologia"
    if ttype == "calculator" or "calc" in ttype:
        return "calc", "Calculadoras"
    return "score", "Escalas e Scores"


def _tool_theme(tool: dict) -> str:
    domain = (tool.get("domain") or tool.get("category") or "").lower()
    if "neuro" in domain:
        return "Neurologia"
    if "ped" in domain:
        return "Pediatria"
    if "icu" in domain or "crit" in domain:
        return "UTI / Críticos"
    if "risk" in domain or "safety" in domain:
        return "Risco e Segurança"
    ttype = (tool.get("tool_type") or "").lower()
    if ttype == "calculator":
        return "Medicação e Doses"
    return "Escalas de Avaliação"


def build_tool_items(
    tools: list[dict],
    slug_map: dict[str, str],
    *,
    hub: str = "ferramentas",
) -> list[dict]:
    items = []
    for i, t in enumerate(tools):
        cat_id, cat_label = _tool_category_id(t)
        slug = slug_map[t["tool_code"]]
        badge = "Novo" if i >= len(tools) - 3 else ("Atualizado" if i < 6 else "")
        items.append({
            "id": slug,
            "title": t["name"],
            "description": f"{t.get('tool_type', 'clinical')} · {t.get('domain', t.get('category', ''))}",
            "badge": badge,
            "category": cat_label,
            "category_id": cat_id,
            "theme": _tool_theme(t),
            "filter_tags": _tool_filter_tags(t),
            "updated": _format_date(t.get("updated_at") or t.get("created_at")),
            "updated_sort": t.get("updated_at") or t.get("created_at") or "",
            "href": tool_page_href(slug, hub),
            "views": max(200, 2400 - i * 18),
            "featured": i < 4,
            "tool_code": t["tool_code"],
            "resource_type": "tool",
        })
    return items


def _library_category(source: str, guideline: dict) -> tuple[str, str]:
    src = (source or "").upper()
    if src == "WHO":
        return "who", "OMS / WHO"
    if src in ("COFEN", "MS_BR", "ANA", "SBC", "SBPT"):
        return "cofen", "Brasil / COFEN"
    if src == "JBI":
        return "jbi", "JBI / Evidências"
    if guideline.get("ipsg_goal_code"):
        return "ipsg", "Metas IPSG"
    title = (guideline.get("title") or "").lower()
    if any(x in title for x in ("queda", "segur", "identif", "cirurg")):
        return "safety", "Segurança do Paciente"
    return "guidelines", "Diretrizes Clínicas"


def _library_theme(guideline: dict) -> str:
    title = (guideline.get("title") or "").lower()
    src = (guideline.get("source") or "").upper()
    if guideline.get("ipsg_goal_code"):
        return "Segurança do Paciente"
    if any(x in title for x in ("medic", "dose", "prescri")):
        return "Medicação e Prescrição"
    if any(x in title for x in ("infec", "higien", "sepse")):
        return "Prevenção de Infecção"
    if any(x in title for x in ("uti", "crit", "ventil")):
        return "UTI / Críticos"
    if any(x in title for x in ("sae", "nanda", "processo")):
        return "Processo de Enfermagem"
    if src == "JBI":
        return "Evidências GRADE"
    return "Segurança do Paciente"


def _library_href(guideline: dict, depth: int) -> str:
    q = slugify(guideline.get("title", guideline.get("guideline_code", "")))
    return route_href("/biblioteca", depth) + f"?q={q}"


def build_library_items(guidelines: list[dict], depth: int) -> list[dict]:
    items = []
    assets_doc = _load_library_visual_assets()
    for i, g in enumerate(guidelines):
        cat_id, cat_label = _library_category(g.get("source", ""), g)
        updated = g.get("updated_at") or g.get("created_at")
        source = g.get("source", "Calculadoras de Enfermagem")
        year = g.get("year", "")
        badge = "IPSG" if g.get("ipsg_goal_code") else ("Novo" if i < 4 else ("Atualizado" if i < 12 else ""))
        thumb = _library_thumbnail(g.get("guideline_code", ""), assets_doc)
        item = {
            "id": slugify(g.get("guideline_code", f"g-{i}")),
            "title": g.get("title", g.get("guideline_code", "")),
            "description": f"{source} · {year} · diretriz clínica",
            "badge": badge,
            "category": cat_label,
            "category_id": cat_id,
            "theme": _library_theme(g),
            "filter_tags": [cat_label, _library_theme(g), source],
            "updated": _format_date(updated),
            "updated_sort": updated or "",
            "href": _library_href(g, depth),
            "views": max(150, 1800 - i * 9),
            "featured": i < 4 or bool(g.get("ipsg_goal_code")),
        }
        if thumb:
            item["thumbnail"] = image_href(thumb, depth)
        items.append(item)
    return items


PATTERN_LABELS = {
    "coren": ("coren", "COREN / Prova", "Enfermagem Geral"),
    "residencia": ("residencia", "Residência", "Enfermagem Geral"),
    "concurso": ("coren", "Concurso", "Enfermagem Geral"),
    "uti": ("uti", "UTI / Críticos", "UTI / Críticos"),
    "sae": ("sae", "SAE / Processo", "SAE / NANDA"),
    "farmaco": ("mixed", "Farmacologia", "Medicação"),
    "pediatria": ("mixed", "Pediatria", "Pediatria"),
    "geriatria": ("mixed", "Geriatria", "Enfermagem Geral"),
    "emerg": ("mixed", "Emergência", "Emergência"),
    "gestao": ("mixed", "Gestão", "Gestão"),
    "mixed": ("mixed", "Temas mistos", "Enfermagem Geral"),
}


def _simulation_difficulty(exam: dict) -> str:
    pct = exam.get("passing_score_pct", 70)
    qs = exam.get("question_count", 20)
    if pct >= 70 and qs >= 45:
        return "Difícil"
    if pct <= 60 or qs <= 25:
        return "Fácil"
    return "Médio"


def build_simulado_items(exams: list[dict], depth: int) -> list[dict]:
    items = []
    for i, exam in enumerate(exams):
        pattern = exam.get("exam_pattern", "mixed")
        cat_id, cat_label, theme = PATTERN_LABELS.get(pattern, PATTERN_LABELS["mixed"])
        slug = slugify(exam.get("exam_code", exam.get("title_pt", f"exam-{i}")))
        updated = exam.get("updated_at") or exam.get("created_at")
        difficulty = _simulation_difficulty(exam)
        qs = exam.get("question_count", 20)
        duration = exam.get("duration_min", 30)
        badge = "Novo" if i < 3 else ("Popular" if i < 6 else "")
        items.append({
            "id": slug,
            "title": exam.get("title_pt", exam.get("title", slug)),
            "description": f"{qs} questões · {difficulty} · {duration} min · nota mínima {exam.get('passing_score_pct', 60)}%",
            "badge": badge,
            "category": cat_label,
            "category_id": cat_id,
            "theme": theme,
            "filter_tags": [cat_label, difficulty, theme],
            "updated": _format_date(updated),
            "updated_sort": updated or "",
            "href": route_href(f"/simulados/{slug}", depth),
            "views": max(80, 1200 - i * 45),
            "featured": i < 4,
            "question_count": qs,
            "duration_min": duration,
            "difficulty": difficulty,
            "action_label": "Iniciar",
        })
    return items


def build_article_items(articles: list[dict], depth: int) -> list[dict]:
    items = []
    for i, article in enumerate(articles):
        slug = article.get("slug", slugify(article.get("title", f"art-{i}")))
        updated = article.get("updated_at") or article.get("published_at")
        read_min = article.get("read_minutes", 5)
        items.append({
            "id": slug,
            "title": article["title"],
            "description": f"{article.get('content_type', 'Artigo')} · {read_min} min · {article.get('subtitle', '')[:80]}",
            "badge": "Destaque" if article.get("featured") else ("Novo" if i < 2 else ""),
            "category": article.get("category", "Artigos"),
            "category_id": article.get("category_id", "safety"),
            "theme": article.get("theme", article.get("category", "Artigos")),
            "filter_tags": [article.get("category", "Artigos"), article.get("content_type", "Artigo")],
            "updated": _format_date(updated),
            "updated_sort": updated or "",
            "href": route_href(f"/artigos/{slug}", depth),
            "views": max(100, 1500 - i * 80),
            "featured": article.get("featured", i < 3),
            "read_minutes": read_min,
            "content_type": article.get("content_type", "Artigo"),
        })
    return items


def _render_hub_hero(hub: dict, depth: int, hero_image: str | None) -> str:
    hero = hub["hero"]
    examples = hero.get("examples", [])
    examples_html = ""
    if examples:
        links = "".join(
            f'<button type="button" class="hub-example" data-hub-example="{esc(ex)}">{esc(ex)}</button>'
            for ex in examples[:6]
        )
        examples_html = f'<div class="hub-examples"><span>Exemplos:</span>{links}</div>'

    media = ""
    if hero_image:
        media = f"""
<div class="hub-hero__media">
  <img src="{esc(image_href(depth, hero_image))}" alt="" width="360" height="280" loading="lazy">
</div>"""

    return f"""
<section class="hub-hero" aria-labelledby="hub-hero-title">
  <div class="section-container hub-hero__grid">
    <div class="hub-hero__content">
      <h1 id="hub-hero-title" class="hub-hero__title" data-hub-hero-title data-hub-hero-default="{esc(hero["title"])}">{esc(hero["title"])}</h1>
      <p class="hub-hero__subtitle" data-ce-profile-hero-subtitle data-hub-hero-subtitle data-hub-hero-subtitle-default="{esc(hero["subtitle"])}">{esc(hero["subtitle"])}</p>
    </div>
    {media}
  </div>
</section>
<div class="hub-search-wrap">
  <div class="section-container">
    <form class="hub-search" role="search" data-hub-search-form>
      <label class="visually-hidden" for="hub-search-input">{esc(hero.get("search_label", "Buscar"))}</label>
      <div class="hub-search__row">
        <input id="hub-search-input" type="search" name="q" placeholder="{esc(hero["search_placeholder"])}" autocomplete="off" data-hub-search-input data-ce-profile-search-input>
        <button type="submit" class="hub-search__btn" aria-label="Buscar">{_svg_icon("search")}</button>
      </div>
      {examples_html}
    </form>
  </div>
</div>"""


def _render_category_carousel(categories: list[dict], total: int) -> str:
    cards = []
    for cat in categories:
        active = " is-active" if cat.get("active") else ""
        count = cat.get("count")
        if cat.get("id") == "all":
            count = total
        count_html = f'<span class="hub-cat-card__count">{count} {"protocolos" if count == 1 else "itens"}</span>' if count is not None else ""
        color = COLOR_CLASS.get(cat.get("color", "teal"), "hub-color-teal")
        cards.append(f"""
<button type="button" class="hub-cat-card{active}" data-hub-category="{esc(cat.get('id', 'all'))}" aria-pressed="{str(bool(cat.get('active'))).lower()}">
  <span class="hub-cat-card__icon {color}">{_hub_icon(cat.get('icon', 'grid'))}</span>
  <span class="hub-cat-card__title">{esc(cat["title"])}</span>
  {count_html}
</button>""")
    return f"""
<section class="hub-categories" aria-label="Categorias">
  <div class="section-container hub-categories__inner">
    <div class="hub-categories__track" data-hub-carousel>{"".join(cards)}</div>
    <button type="button" class="hub-categories__next" data-hub-carousel-next aria-label="Próximas categorias">→</button>
  </div>
</section>"""


def _render_hub_profile_strip() -> str:
    return """
<div class="section-container">
  <div class="ce-profile-strip hub-profile-strip" data-ce-profile-strip hidden>
    <span data-ce-profile-strip-label></span>
    <div class="ce-profile-strip__links" data-ce-profile-quick-links></div>
    <button type="button" class="ce-profile-strip__change" data-profile-change>Alterar perfil</button>
  </div>
</div>"""


def _render_hub_concepts(concepts: list[dict], depth: int, *, active_id: str = "") -> str:
    cards = []
    for concept in concepts:
        cid = concept.get("id", "")
        active = " is-active" if cid == active_id else ""
        color = COLOR_CLASS.get(concept.get("color", "teal"), "hub-color-teal")
        kind = concept.get("kind_label", concept.get("subtitle", ""))
        cards.append(f"""
<button type="button" class="hub-concept-card{active}" data-hub-concept="{esc(cid)}" data-hub-concept-slug="{esc(concept.get('slug', ''))}" data-ce-profile-module="{esc(concept.get('slug', cid))}" aria-pressed="{str(cid == active_id).lower()}">
  <span class="hub-concept-card__icon {color}">{_hub_icon(concept.get("icon", "calculator"))}</span>
  <span class="hub-concept-card__body">
    <strong>{esc(concept["title"])}</strong>
    <small>{esc(kind)}</small>
  </span>
  <span class="hub-concept-card__count">{int(concept.get("resource_count", 0))}</span>
</button>""")
    return f"""
<section class="hub-concepts" aria-label="Conceitos clínicos" data-hub-concepts>
  <div class="section-container">
    <div class="hub-concepts__header">
      <h2>Conceitos clínicos</h2>
      <p>Cada conceito é uma <strong>Calculadora</strong> ou <strong>Escala Clínica</strong> — clique para ver todo o conteúdo relacionado no site.</p>
    </div>
    <div class="hub-concepts__search-wrap">
      <label class="visually-hidden" for="hub-concept-filter">Filtrar calculadoras e escalas</label>
      <input id="hub-concept-filter" type="search" class="hub-concepts__search" placeholder="Buscar conceito (ex.: APGAR, Braden, GCS…)" data-hub-concept-filter autocomplete="off">
    </div>
    <div class="hub-concepts__track-wrap">
      <div class="hub-concepts__track" data-hub-concept-track>{"".join(cards)}</div>
      <button type="button" class="hub-concepts__next" data-hub-concept-next aria-label="Próximos conceitos">→</button>
    </div>
  </div>
</section>
<div class="hub-concept-banner section-container" data-hub-concept-banner hidden>
  <div class="hub-concept-banner__inner">
    <span data-hub-concept-banner-label></span>
    <button type="button" class="hub-concept-banner__clear" data-hub-concept-clear>Limpar conceito</button>
  </div>
</div>"""


def _render_hub_sidebar_extras() -> str:
    return """
    <div class="hub-prefs-card hub-prefs-card--profile" data-hub-profile-prefs>
      <div class="hub-prefs-card__head">
        <span class="hub-prefs-card__icon" aria-hidden="true">{icon}</span>
        <strong>Seu perfil</strong>
      </div>
      <p class="hub-prefs-profile__current" data-prefs-profile-current>Personalize conforme seu papel.</p>
    </div>
    <div class="hub-prefs-card hub-prefs-card--downloads">
      <div class="hub-prefs-card__head">
        <span class="hub-prefs-card__icon" aria-hidden="true">{dl_icon}</span>
        <strong>Cesta de downloads</strong>
      </div>
      <ul class="hub-prefs-downloads__list" data-hub-downloads-list></ul>
      <p class="hub-prefs-hint" data-hub-downloads-empty hidden>Nenhum item salvo.</p>
    </div>
    <div class="hub-prefs-card hub-prefs-card--offline">
      <div class="hub-prefs-card__head">
        <span class="hub-prefs-card__icon" aria-hidden="true">{off_icon}</span>
        <strong>Conteúdo offline</strong>
      </div>
      <ul class="hub-prefs-offline__list" data-hub-offline-list></ul>
      <p class="hub-prefs-hint" data-hub-offline-empty hidden>Nenhum conteúdo offline.</p>
    </div>""".format(
        icon=_svg_icon("shield"),
        dl_icon=_svg_icon("bookmark"),
        off_icon=_svg_icon("monitor"),
    )


def _render_filters(filters: list[dict], *, show_extras: bool = True) -> str:
    groups = []
    for group in filters:
        opts = []
        for opt in group.get("options", []):
            checked = ' checked' if opt.get("checked") else ""
            opts.append(f"""
<label class="hub-filter__option">
  <input type="checkbox" data-hub-filter-group="{esc(group['title'])}" value="{esc(opt['label'])}" aria-label="{esc(opt['label'])}"{checked}>
  <span>{esc(opt["label"])}</span>
  <span class="hub-filter__count">{esc(opt.get("count", ""))}</span>
</label>""")
        groups.append(f"""
<details class="hub-filter-group" open>
  <summary>{esc(group["title"])}</summary>
  <div class="hub-filter-group__body">{"".join(opts)}</div>
</details>""")
    return f"""
<aside class="hub-sidebar" aria-label="Filtros">
  <div class="hub-filters">
    <div class="hub-filters__head">
      <h2>Filtros</h2>
      <button type="button" class="hub-filters__clear" data-hub-clear-filters>Limpar todos</button>
    </div>
    {"".join(groups)}
    <div class="hub-prefs-card" data-hub-prefs>
      <div class="hub-prefs-card__head">
        <span class="hub-prefs-card__icon" aria-hidden="true">{_svg_icon("settings")}</span>
        <strong>Preferências</strong>
      </div>
      <fieldset class="hub-prefs-fieldset">
        <legend>Visualização</legend>
        <div class="hub-prefs-segment" role="group" aria-label="Modo de visualização">
          <button type="button" class="hub-prefs-segment__btn is-active" data-hub-view="grid" aria-pressed="true">Grade</button>
          <button type="button" class="hub-prefs-segment__btn" data-hub-view="list" aria-pressed="false">Lista</button>
          <button type="button" class="hub-prefs-segment__btn" data-hub-view="compact" aria-pressed="false">Compacto</button>
        </div>
      </fieldset>
      <fieldset class="hub-prefs-fieldset">
        <legend>Classificar</legend>
        <label class="visually-hidden" for="hub-sort-select">Ordenação</label>
        <select id="hub-sort-select" class="hub-prefs-select" data-hub-sort aria-label="Ordenação">
          <option value="az">A → Z</option>
          <option value="za">Z → A</option>
          <option value="recent">Mais recentes</option>
          <option value="popular">Mais populares</option>
        </select>
      </fieldset>
      <p class="hub-prefs-hint">Preferências salvas localmente neste dispositivo.</p>
    </div>
    {_render_hub_sidebar_extras() if show_extras else ""}
  </div>
</aside>"""


def _item_attrs(item: dict) -> str:
    tags = ",".join(str(t).lower() for t in item.get("filter_tags", []))
    tool_codes = item.get("tool_codes") or ([item["tool_code"]] if item.get("tool_code") else [])
    concept = item.get("concept_id") or (tool_codes[0] if tool_codes else "")
    cat_id = item.get("resource_type") or item.get("category_id", "")
    extra = ""
    if tool_codes:
        extra += f' data-tool-concept="{esc(",".join(tool_codes))}"'
    if concept:
        extra += f' data-hub-concept="{esc(concept)}"'
    rtype = item.get("resource_type", "")
    if rtype:
        extra += f' data-hub-resource-type="{esc(rtype)}"'
    return (
        f'data-hub-item data-hub-category-id="{esc(cat_id)}" '
        f'data-hub-theme="{esc(item["theme"])}" data-hub-title="{esc(item["title"].lower())}" '
        f'data-hub-views="{int(item.get("views", 0))}" '
        f'data-hub-updated="{esc(item.get("updated_sort", ""))}" '
        f'data-hub-filter-tags="{esc(tags)}"{extra}'
    )


def _tool_filter_tags(tool: dict) -> list[str]:
    tags: list[str] = []
    ttype = (tool.get("tool_type") or "").lower()
    domain = (tool.get("domain") or tool.get("category") or "").lower()
    if ttype == "score" or "scale" in (tool.get("category") or "").lower():
        tags.append("Escalas (score)")
    if ttype == "calculator" or "calc" in ttype:
        tags.append("Calculadoras")
    if "fluid" in domain or "dose" in domain:
        tags.append("Balanço hídrico")
    for label, needle in (
        ("Neurologia", "neuro"), ("Cardiologia", "cardio"), ("UTI", "icu"),
        ("Pediatria", "ped"), ("Emergência", "emerg"),
    ):
        if needle in domain or needle in (tool.get("category") or "").lower():
            tags.append(label)
    return tags


def _render_featured(items: list[dict], title: str, *, card_style: str = "default") -> str:
    featured = [i for i in items if i.get("featured")][:4]
    if len(featured) < 4:
        featured = items[:4]
    cards = []
    for item in featured:
        if card_style == "simulation":
            diff_class = {"Fácil": "easy", "Médio": "medium", "Difícil": "hard"}.get(item.get("difficulty", "Médio"), "medium")
            cards.append(f"""
<article class="hub-sim-card" {_item_attrs(item)}>
  <div class="hub-sim-card__count">{esc(item.get("question_count", 0))} questões</div>
  <h3><a href="{esc(item['href'])}">{esc(item["title"])}</a></h3>
  <p>{esc(item["description"])}</p>
  <div class="hub-sim-card__meta">
    <span class="hub-sim-card__difficulty hub-sim-card__difficulty--{diff_class}">{esc(item.get("difficulty", "Médio"))}</span>
    <span>{esc(item.get("duration_min", 30))} min</span>
  </div>
  <a class="btn-primary-sm hub-sim-card__btn" href="{esc(item['href'])}">{esc(item.get("action_label", "Iniciar"))}</a>
</article>""")
            continue
        if card_style == "article":
            badge = f'<span class="hub-badge">{esc(item["badge"])}</span>' if item.get("badge") else ""
            cards.append(f"""
<article class="hub-article-card" {_item_attrs(item)}>
  <div class="hub-article-card__top">
    <span class="hub-article-card__type">{esc(item.get("content_type", "Artigo"))}</span>
    {badge}
  </div>
  <h3><a href="{esc(item['href'])}">{esc(item["title"])}</a></h3>
  <p>{esc(item["description"])}</p>
  <div class="hub-article-card__meta">
    <span class="hub-pill">{esc(item["category"])}</span>
    <span>{esc(item.get("read_minutes", 5))} min</span>
    <time>{esc(item["updated"])}</time>
  </div>
</article>""")
            continue
        badge = f'<span class="hub-badge">{esc(item["badge"])}</span>' if item.get("badge") else ""
        cards.append(f"""
<article class="hub-featured-card" {_item_attrs(item)}>
  <div class="hub-featured-card__top">
    <span class="hub-featured-card__icon">{_hub_icon("clipboard")}</span>
    {badge}
    <button type="button" class="hub-bookmark" data-hub-save-item data-save-title="{esc(item['title'])}" data-save-href="{esc(item['href'])}" aria-label="Salvar {esc(item['title'])}">☆</button>
  </div>
  <h3><a href="{esc(item['href'])}">{esc(item["title"])}</a></h3>
  <p>{esc(item["description"])}</p>
  <div class="hub-featured-card__meta">
    <span class="hub-pill">{esc(item["category"])}</span>
    <time>{esc(item["updated"])}</time>
  </div>
</article>""")
    grid_class = "hub-featured-grid"
    if card_style == "simulation":
        grid_class = "hub-sim-grid"
    elif card_style == "article":
        grid_class = "hub-article-grid"
    return f"""
<section class="hub-section" aria-labelledby="hub-featured-title">
  <div class="hub-section__head">
    <h2 id="hub-featured-title">{esc(title)}</h2>
    <a class="hub-section__more" href="#hub-all-items">Ver todos →</a>
  </div>
  <div class="{grid_class}">{"".join(cards)}</div>
</section>"""


def _render_recent(items: list[dict], title: str) -> str:
    recent = sorted(items, key=lambda x: x.get("updated_sort", ""), reverse=True)[:5]
    rows = []
    for item in recent:
        rows.append(f"""
<li class="hub-recent-row" {_item_attrs(item)}>
  <span class="hub-recent-row__icon">{_hub_icon("document")}</span>
  <div class="hub-recent-row__body">
    <a href="{esc(item['href'])}">{esc(item["title"])}</a>
    <span class="hub-pill">{esc(item["category"])}</span>
  </div>
  <time>{esc(item["updated"])}</time>
  <button type="button" class="hub-bookmark" data-hub-save-item data-save-title="{esc(item['title'])}" data-save-href="{esc(item['href'])}" aria-label="Salvar">☆</button>
</li>""")
    return f"""
<section class="hub-section" aria-labelledby="hub-recent-title">
  <div class="hub-section__head">
    <h2 id="hub-recent-title">{esc(title)}</h2>
  </div>
  <ul class="hub-recent-list">{"".join(rows)}</ul>
</section>"""


def _render_themes(themes: list[dict], title: str) -> str:
    cards = []
    for theme in themes:
        color = COLOR_CLASS.get(theme.get("color", "teal"), "hub-color-teal")
        cards.append(f"""
<a class="hub-theme-card" href="#" data-hub-theme-filter="{esc(theme['title'])}">
  <span class="hub-theme-card__icon {color}">{_hub_icon(theme.get("icon", "clipboard"))}</span>
  <span class="hub-theme-card__title">{esc(theme["title"])}</span>
  <span class="hub-theme-card__count">{esc(theme.get("count", 0))}</span>
</a>""")
    return f"""
<section class="hub-section" aria-labelledby="hub-themes-title">
  <div class="hub-section__head">
    <h2 id="hub-themes-title">{esc(title)}</h2>
  </div>
  <div class="hub-themes-grid">{"".join(cards)}</div>
</section>"""


def _render_popular(items: list[dict], title: str) -> str:
    popular = sorted(items, key=lambda x: x.get("views", 0), reverse=True)[:5]
    rows = []
    for rank, item in enumerate(popular, 1):
        rows.append(f"""
<li class="hub-popular-row" {_item_attrs(item)}>
  <span class="hub-popular-row__rank">{rank}</span>
  <a href="{esc(item['href'])}">{esc(item["title"])}</a>
  <span class="hub-pill">{esc(item["category"])}</span>
  <span class="hub-popular-row__views" aria-label="{esc(item.get('views', 0))} visualizações">👁 {esc(item.get('views', 0))}</span>
</li>""")
    return f"""
<section class="hub-section" id="hub-all-items" aria-labelledby="hub-popular-title">
  <div class="hub-section__head">
    <h2 id="hub-popular-title">{esc(title)}</h2>
  </div>
  <ol class="hub-popular-list">{"".join(rows)}</ol>
</section>"""


def _render_cta(cta: dict, depth: int, hero_image: str | None) -> str:
    img = ""
    if hero_image:
        img = f'<img src="{esc(image_href(depth, hero_image))}" alt="" width="280" height="220" loading="lazy">'
    return f"""
<section class="hub-cta" aria-labelledby="hub-cta-title">
  <div class="section-container hub-cta__grid">
    <div class="hub-cta__content">
      <h2 id="hub-cta-title">{esc(cta["title"])}</h2>
      <p>{esc(cta["text"])}</p>
      <a class="btn-primary-lg" href="{esc(route_href(cta.get('href', '/contato'), depth))}">{esc(cta["button"])} →</a>
    </div>
    <div class="hub-cta__media">{img}</div>
  </div>
</section>"""


def build_quiz_items(quizzes: list[dict], depth: int) -> list[dict]:
    items = []
    for i, q in enumerate(quizzes):
        diff = q.get("difficulty", "Médio")
        cat_id = "basic" if diff == "basic" else ("advanced" if diff in ("advanced", "hard") else "intermediate")
        items.append({
            "id": slugify(q.get("quiz_code", f"q-{i}")),
            "title": q.get("title_pt", q.get("title", "")),
            "description": q.get("description_pt", q.get("description", "Quiz clínico de enfermagem")),
            "badge": "Novo" if i < 3 else "",
            "category": diff.title() if diff else "Quiz",
            "category_id": cat_id,
            "theme": q.get("topic", "Enfermagem Geral"),
            "filter_tags": [diff.title() if diff else "Complementar", q.get("topic", "Enfermagem Geral")],
            "updated": "2026",
            "updated_sort": "2026",
            "href": route_href("/quiz", depth) + f"?q={slugify(q.get('title_pt', q.get('title', '')))}",
            "views": max(100, 800 - i * 12),
            "featured": i < 4,
            "tool_code": q.get("linked_tool_code", ""),
            "resource_type": "quiz",
        })
    return items


def build_glossary_items(glossary: list[dict], depth: int) -> list[dict]:
    def letter_group(ch: str) -> str:
        c = ch.lower()
        if c in "abcdef":
            return "a-f"
        if c in "ghijklm":
            return "g-m"
        return "n-z"

    items = []
    for i, g in enumerate(glossary):
        term = g.get("term_pt", g.get("term", ""))
        letter = term[0].upper() if term else "A"
        domain = g.get("domain", "Enfermagem Geral")
        items.append({
            "id": slugify(g.get("term_code", f"t-{i}")),
            "title": term,
            "description": (g.get("definition_pt", g.get("definition", "")) or "")[:120],
            "badge": "",
            "category": f"Letra {letter}",
            "category_id": letter_group(letter),
            "theme": domain,
            "filter_tags": [domain, f"Letra {letter}"],
            "updated": "2026",
            "updated_sort": term.lower(),
            "href": route_href("/glossario", depth) + f"?q={slugify(term)}",
            "views": max(50, 500 - i),
            "featured": i < 4,
        })
    return items


def build_competency_items(competencies: list[dict], depth: int) -> list[dict]:
    items = []
    for i, c in enumerate(competencies):
        title = c.get("title_pt", c.get("title", ""))
        domain = c.get("domain", "Enfermagem Geral")
        level = c.get("level", "Profissional")
        level_label = f"Nível {level}" if isinstance(level, int) else str(level)
        items.append({
            "id": slugify(c.get("competency_code", f"c-{i}")),
            "title": title,
            "description": c.get("description_pt", c.get("description", f"Competência {c.get('competency_code', '')}")),
            "badge": level_label,
            "category": domain,
            "category_id": slugify(domain)[:20],
            "theme": domain,
            "filter_tags": [domain, level_label],
            "updated": "2026",
            "updated_sort": title.lower(),
            "href": route_href("/competencias", depth) + f"?q={slugify(title)}",
            "views": max(80, 600 - i * 3),
            "featured": i < 4,
        })
    return items


def build_education_hub_items(
    *,
    quizzes: list,
    flashcards: list,
    paths: list,
    exams: list,
    depth: int,
) -> list[dict]:
    modules = [
        ("Quiz Clínico", f"{len(quizzes)} quizzes", "quiz", "/quiz", len(quizzes)),
        ("Flashcards", f"{len(flashcards)} cartões", "flashcards", "/flashcards", len(flashcards)),
        ("Trilhas", f"{len(paths)} trilhas", "trilhas", "/trilhas", len(paths)),
        ("Simulados", f"{len(exams)} simulados", "simulados", "/simulados", len(exams)),
        ("Artigos", "Conteúdos científicos", "artigos", "/artigos", 5),
        ("Biblioteca", "Diretrizes e evidências", "biblioteca", "/biblioteca", 20),
    ]
    items = []
    for i, (title, desc, cat_id, route, count) in enumerate(modules):
        items.append({
            "id": cat_id,
            "title": title,
            "description": desc,
            "badge": "Popular" if i < 2 else "",
            "category": "Educação",
            "category_id": cat_id,
            "theme": "Formação Continuada",
            "filter_tags": ["Educação", title],
            "updated": "2026",
            "updated_sort": "2026",
            "href": route_href(route, depth),
            "views": count * 10,
            "featured": True,
        })
    return items


def _tool_kind_label(tool: dict) -> tuple[str, str]:
    """Return (kind_id, kind_label) — calculadora or escala clínica."""
    ttype = (tool.get("tool_type") or "").lower()
    template = (tool.get("template_code") or "").upper()
    name = (tool.get("name") or "").lower()
    if (
        ttype == "score"
        or template == "TPL.SCALE_FORM"
        or " score" in name
        or name.endswith(" score")
        or "escala" in name
    ):
        return "escala", "Escala Clínica"
    return "calculadora", "Calculadora Clínica"


def _tool_concept_icon(tool: dict) -> str:
    kind, _ = _tool_kind_label(tool)
    return "clipboard" if kind == "escala" else "calculator"


def _tool_concept_color(tool: dict) -> str:
    domain = (tool.get("domain") or "").lower()
    if "neuro" in domain:
        return "navy"
    if "ped" in domain:
        return "orange"
    if "icu" in domain or "crit" in domain:
        return "red"
    if "wound" in domain:
        return "purple"
    if "fluid" in domain or "med" in domain:
        return "green"
    return "teal"


def _eco_item(
    *,
    tool_code: str,
    resource_type: str,
    title: str,
    description: str,
    href: str,
    badge: str = "",
    views: int = 200,
    featured: bool = False,
    filter_tags: list[str] | None = None,
) -> dict:
    tag_label = badge or resource_type.title()
    return {
        "id": slugify(f"{tool_code}-{resource_type}-{title}")[:40],
        "title": title,
        "description": description,
        "badge": tag_label,
        "category": tag_label,
        "category_id": resource_type,
        "theme": tag_label,
        "filter_tags": filter_tags or [tag_label],
        "updated": "2026",
        "updated_sort": "2026",
        "href": href,
        "views": views,
        "featured": featured,
        "tool_code": tool_code,
        "tool_codes": [tool_code],
        "concept_id": tool_code,
        "resource_type": resource_type,
    }


# Keyword hints linking free-text resources (courses, jobs, guidelines) to tools.
_TOPIC_TOOL_HINTS: dict[str, list[str]] = {
    "lesão por pressão": ["TOOL.BRADEN", "TOOL.NORTON", "TOOL.WATERLOW"],
    "lesao por pressao": ["TOOL.BRADEN", "TOOL.NORTON", "TOOL.WATERLOW"],
    "prevenção de lesão": ["TOOL.BRADEN", "TOOL.NORTON"],
    "queda": ["TOOL.MORSE"],
    "medicação": ["TOOL.INFUSION", "TOOL.INSULIN", "TOOL.DILUTION"],
    "medicamento": ["TOOL.INFUSION", "TOOL.INSULIN", "TOOL.DILUTION"],
    "cálculo e diluição": ["TOOL.INFUSION", "TOOL.DILUTION", "TOOL.MCG_KG_MIN"],
    "gotejamento": ["TOOL.INFUSION"],
    "gasometria": ["TOOL.BICARB"],
    "sepse": ["TOOL.SOFA", "TOOL.qSOFA", "TOOL.NEWS2"],
    "uti": ["TOOL.RASS", "TOOL.CAM-ICU", "TOOL.SOFA", "TOOL.APACHE2"],
    "ventilação": ["TOOL.SOFA", "TOOL.APACHE2"],
    "ventilacao": ["TOOL.SOFA", "TOOL.APACHE2"],
    "neurologia": ["TOOL.GCS", "TOOL.RASS"],
    "pediatria": ["TOOL.APGAR", "TOOL.BALLARD"],
    "obstetr": ["TOOL.APGAR"],
    "sae": ["TOOL.BRADEN", "TOOL.GCS"],
    "nanda": ["TOOL.BRADEN", "TOOL.GCS"],
    "ecg": ["TOOL.HEART"],
    "curativos": ["TOOL.BRADEN"],
    "feridas": ["TOOL.BRADEN"],
}

_DRUG_TOOL_HINTS: dict[str, list[str]] = {
    "insulin": ["TOOL.INSULIN"],
    "insulina": ["TOOL.INSULIN"],
    "heparin": ["TOOL.HEPARIN"],
    "heparina": ["TOOL.HEPARIN"],
    "morphine": ["TOOL.INFUSION", "TOOL.DILUTION"],
    "morfina": ["TOOL.INFUSION", "TOOL.DILUTION"],
    "norepinephrine": ["TOOL.INFUSION"],
    "noradrenalina": ["TOOL.INFUSION"],
    "norepinefrina": ["TOOL.INFUSION"],
    "vasopressor": ["TOOL.INFUSION"],
    "anticoagul": ["TOOL.HEPARIN"],
}

_LAB_TOOL_HINTS: dict[str, list[str]] = {
    "glicemia": ["TOOL.INSULIN", "TOOL.BMI"],
    "glucose": ["TOOL.INSULIN"],
    "hemoglobina glicada": ["TOOL.INSULIN"],
    "hba1c": ["TOOL.INSULIN"],
    "gasometria": ["TOOL.BICARB"],
    "bicarbonato": ["TOOL.BICARB"],
    "potassio": ["TOOL.BICARB"],
    "sodio": ["TOOL.BICARB"],
    "creatinina": ["TOOL.RENAL_CG", "TOOL.CRCL_CG"],
    "hemoglobina": ["TOOL.BMI"],
    "hematocrito": ["TOOL.BMI"],
    "plaquetas": ["TOOL.SOFA"],
    "lactato": ["TOOL.SOFA", "TOOL.qSOFA"],
    "pcr": ["TOOL.SOFA", "TOOL.NEWS2"],
}

_CONTENT_BUCKET_MAP: dict[str, tuple[str, str]] = {
    "article": ("articles", "Artigo"),
    "guideline": ("guidelines", "Biblioteca"),
    "drug": ("drugs", "Medicamento"),
    "lab_reference": ("labs", "Laboratório"),
    "safety_rule": ("safety", "Segurança"),
    "flashcard": ("flashcards_extra", "Flashcard"),
}

_CONTENT_SKIP_TYPES = frozenset({
    "quiz", "clinical_tool", "competency", "protocol", "simulated_exam", "learning_path",
    "nursing_diagnosis", "nursing_intervention", "nursing_outcome", "nnn_linkage",
})


def _build_nanda_to_tools(
    diagnoses: list[dict],
    entity_relations: list[dict] | None = None,
) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for d in diagnoses:
        dc = d.get("diagnosis_code", "")
        for tc in d.get("related_tool_codes") or []:
            if tc not in index.setdefault(dc, []):
                index[dc].append(tc)
    for rel in entity_relations or []:
        if rel.get("source_entity_type") != "ClinicalTool":
            continue
        if rel.get("target_entity_type") != "NursingDiagnosis":
            continue
        tc, dc = rel.get("source_code", ""), rel.get("target_code", "")
        if tc and dc and tc not in index.setdefault(dc, []):
            index[dc].append(tc)
    return index


def _build_content_lookups(
    *,
    quizzes: list[dict],
    flashcards: list[dict],
    protocols: list[dict],
    competencies: list[dict],
    exams: list[dict],
    interventions: list[dict],
    nnn_linkages: list[dict],
    nanda_to_tools: dict[str, list[str]],
) -> dict[str, Any]:
    quiz_to_tool = {
        q["quiz_code"]: q["linked_tool_code"]
        for q in quizzes if q.get("quiz_code") and q.get("linked_tool_code")
    }
    flashcard_to_tools: dict[str, list[str]] = {}
    for fc in flashcards:
        fc_code = fc.get("flashcard_code", "")
        entity = fc.get("linked_entity_code", "")
        if entity.startswith("TOOL."):
            flashcard_to_tools[fc_code] = [entity]
        elif entity.startswith("NANDA."):
            flashcard_to_tools[fc_code] = list(nanda_to_tools.get(entity, []))

    nic_to_tools = {
        i.get("intervention_code", ""): list(dict.fromkeys(i.get("related_tool_codes") or []))
        for i in interventions if i.get("intervention_code")
    }
    noc_to_tools: dict[str, list[str]] = {}
    for link in nnn_linkages:
        oc = link.get("outcome_code", "")
        for tc in nanda_to_tools.get(link.get("diagnosis_code", ""), []):
            if tc not in noc_to_tools.setdefault(oc, []):
                noc_to_tools[oc].append(tc)

    return {
        "quiz_to_tool": quiz_to_tool,
        "flashcard_to_tools": flashcard_to_tools,
        "nanda_to_tools": nanda_to_tools,
        "nic_to_tools": nic_to_tools,
        "noc_to_tools": noc_to_tools,
        "protocol_to_tools": {
            p.get("protocol_code", ""): list(p.get("related_tool_codes") or [])
            for p in protocols if p.get("protocol_code")
        },
        "competency_to_tools": {
            c.get("competency_code", ""): list(c.get("linked_tool_codes") or [])
            for c in competencies if c.get("competency_code")
        },
        "exam_to_tools": {
            e.get("exam_code", ""): list(dict.fromkeys(
                quiz_to_tool[qc]
                for qc in (e.get("linked_quiz_codes") or [])
                if qc in quiz_to_tool
            ))
            for e in exams if e.get("exam_code")
        },
    }


def _drug_to_tools(title: str, drug_code: str, tools: list[dict], slug_map: dict[str, str]) -> list[str]:
    linked = _text_links_tools(title, tools, slug_map)
    lower = f"{title} {drug_code}".lower()
    for hint, codes in _DRUG_TOOL_HINTS.items():
        if hint in lower:
            linked.extend(codes)
    return list(dict.fromkeys(linked))


def _lab_to_tools(title: str, lab_code: str, tools: list[dict], slug_map: dict[str, str]) -> list[str]:
    linked = _text_links_tools(title, tools, slug_map)
    lower = f"{title} {lab_code}".lower()
    for hint, codes in _LAB_TOOL_HINTS.items():
        if hint in lower:
            linked.extend(codes)
    return list(dict.fromkeys(linked))


def _resolve_content_tools(
    content: dict,
    lookups: dict[str, Any],
    tools: list[dict],
    slug_map: dict[str, str],
) -> list[str]:
    sc = content.get("source_code", "")
    se = content.get("source_entity", "")
    title = content.get("title_pt", "")

    if sc.startswith("TOOL."):
        return [sc]
    if se == "Quiz":
        t = lookups["quiz_to_tool"].get(sc)
        return [t] if t else []
    if se == "Flashcard":
        return lookups["flashcard_to_tools"].get(sc, [])
    if se == "NursingDiagnosis":
        return lookups["nanda_to_tools"].get(sc, [])
    if se == "NursingIntervention":
        return lookups["nic_to_tools"].get(sc, [])
    if se == "NursingOutcome":
        return lookups["noc_to_tools"].get(sc, [])
    if se == "NNNLinkage":
        parts = sc.split(".")
        if len(parts) >= 3 and parts[0] == "NNN" and parts[1] == "NANDA":
            return lookups["nanda_to_tools"].get(f"{parts[1]}.{parts[2]}", [])
    if se == "InstitutionalProtocol":
        return lookups["protocol_to_tools"].get(sc, [])
    if se == "Competency":
        return lookups["competency_to_tools"].get(sc, [])
    if se == "SimulatedExam":
        return lookups["exam_to_tools"].get(sc, [])
    if se == "DrugReference":
        return _drug_to_tools(title, sc, tools, slug_map)
    if se == "LabReferenceValue":
        return _lab_to_tools(title, sc, tools, slug_map)
    return _text_links_tools(title, tools, slug_map)


def _apply_content_records(
    index: dict[str, dict[str, list]],
    contents: list[dict],
    tools: list[dict],
    slug_map: dict[str, str],
    lookups: dict[str, Any],
    add,
) -> None:
    """Index contents.json records into tool ecosystems (structured FK resolution)."""
    _DESC = {
        "drugs": "Fármaco · biblioteca de medicamentos",
        "labs": "Valor de referência laboratorial",
        "safety": "Regra de segurança do paciente",
        "flashcards_extra": "Cartão de revisão",
    }
    for content in contents:
        ct = content.get("content_type", "")
        if ct in _CONTENT_SKIP_TYPES:
            continue
        bucket_info = _CONTENT_BUCKET_MAP.get(ct)
        if not bucket_info:
            continue
        bucket, badge = bucket_info
        tool_codes = _resolve_content_tools(content, lookups, tools, slug_map)
        if not tool_codes:
            continue
        href = content.get("route_path") or "/"
        if not href.startswith("/"):
            href = f"/{href}"
        title = (content.get("title_pt") or content.get("content_code", ""))[:100]
        payload = {
            "title": title,
            "description": _DESC.get(bucket, badge)[:120],
            "href": href,
            "badge": badge,
        }
        for tc in tool_codes:
            add(tc, bucket, payload)


def _slug_to_tool_code(href: str, slug_to_code: dict[str, str]) -> str | None:
    if not href:
        return None
    clean = href.split("?")[0].rstrip("/")
    if "/ferramentas/" in clean:
        slug = clean.split("/ferramentas/")[-1].split("/")[0]
        return slug_to_code.get(slug)
    slug = clean.strip("/").split("/")[-1]
    return slug_to_code.get(slug)


def _tool_match_terms(tool: dict, slug: str) -> list[str]:
    terms = [
        (tool.get("acronym") or "").lower(),
        (tool.get("name") or "").lower(),
        slug.lower(),
        (tool.get("domain") or "").lower(),
        (tool.get("category") or "").lower(),
        (tool.get("tool_code") or "").replace("TOOL.", "").lower(),
    ]
    return [t for t in terms if len(t) >= 2]


def _text_links_tools(text: str, tools: list[dict], slug_map: dict[str, str]) -> list[str]:
    """Return tool_codes whose terms appear in text."""
    if not text:
        return []
    lower = text.lower()
    linked: list[str] = []
    for tool in tools:
        slug = slug_map.get(tool["tool_code"], "")
        if any(term in lower for term in _tool_match_terms(tool, slug)):
            linked.append(tool["tool_code"])
    for hint, codes in _TOPIC_TOOL_HINTS.items():
        if hint in lower:
            linked.extend(codes)
    return list(dict.fromkeys(linked))


def _eco_link_bucket() -> dict[str, list]:
    return {
        "articles": [], "simulados": [], "concursos": [], "guidelines": [],
        "nanda": [], "courses": [], "jobs": [], "casos": [], "mindmaps": [],
        "nic": [], "noc": [], "nnn": [], "drugs": [], "labs": [], "safety": [],
        "reassessment": [], "flashcards_extra": [], "glossary": [],
        "forum": [], "career": [],
    }


def build_extended_ecosystem_index(
    tools: list[dict],
    *,
    slug_map: dict[str, str],
    quizzes: list[dict],
    exams: list[dict],
    articles: list[dict],
    guidelines: list[dict],
    diagnoses: list[dict],
    definitions: dict[str, dict],
    courses: list[dict],
    jobs: list[dict],
    template_pages: dict,
    contents: list[dict] | None = None,
    interventions: list[dict] | None = None,
    outcomes: list[dict] | None = None,
    nnn_linkages: list[dict] | None = None,
    entity_relations: list[dict] | None = None,
    reassessment_rules: list[dict] | None = None,
    competencies: list[dict] | None = None,
    protocols: list[dict] | None = None,
    flashcards: list[dict] | None = None,
    glossary: list[dict] | None = None,
    forum_topics: list[dict] | None = None,
    career_paths: list[dict] | None = None,
) -> dict[str, dict[str, list]]:
    """Reverse index: tool_code → linked resources across the whole site."""
    slug_to_code = {v: k for k, v in slug_map.items()}
    index: dict[str, dict[str, list]] = {t["tool_code"]: _eco_link_bucket() for t in tools}
    quiz_to_tool = {
        q["quiz_code"]: q["linked_tool_code"]
        for q in quizzes if q.get("linked_tool_code") and q.get("quiz_code")
    }

    def add(tool_code: str, bucket: str, payload: dict) -> None:
        if tool_code not in index:
            return
        href = payload.get("href", "")
        if any(x.get("href") == href for x in index[tool_code][bucket]):
            return
        index[tool_code][bucket].append(payload)

    for article in articles:
        slug = article.get("slug", slugify(article.get("title", "")))
        for rt in article.get("related_tools") or []:
            tc = _slug_to_tool_code(rt.get("href", ""), slug_to_code)
            if tc:
                add(tc, "articles", {
                    "title": article["title"],
                    "description": article.get("subtitle", article.get("content_type", "Artigo"))[:120],
                    "href": f"/artigos/{slug}",
                    "badge": "Artigo",
                })
        for tc in _text_links_tools(
            f"{article.get('title', '')} {article.get('theme', '')} {' '.join(article.get('tags', []))}",
            tools, slug_map,
        ):
            add(tc, "articles", {
                "title": article["title"],
                "description": article.get("subtitle", "Artigo científico")[:120],
                "href": f"/artigos/{slug}",
                "badge": "Artigo",
            })

    for exam in exams:
        exam_tools: set[str] = set()
        for qc in exam.get("linked_quiz_codes") or []:
            tc = quiz_to_tool.get(qc)
            if tc:
                exam_tools.add(tc)
        if not exam_tools:
            exam_tools.update(_text_links_tools(exam.get("title_pt", exam.get("title", "")), tools, slug_map))
        eslug = slugify(exam.get("exam_code", exam.get("title_pt", "exam")))
        pattern = (exam.get("exam_pattern") or "").lower()
        is_concurso = pattern in ("concurso", "coren", "concurso_publico")
        for tc in exam_tools:
            add(tc, "simulados", {
                "title": exam.get("title_pt", exam.get("title", "Simulado")),
                "description": f"{exam.get('question_count', 0)} questões · {exam.get('duration_min', 30)} min",
                "href": f"/simulados/{eslug}",
                "badge": "Simulado",
            })
            if is_concurso:
                add(tc, "concursos", {
                    "title": exam.get("title_pt", exam.get("title", "Concurso")),
                    "description": f"Prova formativa · {exam.get('question_count', 0)} questões",
                    "href": f"/simulados/{eslug}",
                    "badge": "Concurso",
                })

    for g in guidelines:
        text = f"{g.get('title', '')} {g.get('guideline_code', '')}"
        for tc in _text_links_tools(text, tools, slug_map):
            add(tc, "guidelines", {
                "title": g.get("title", g.get("guideline_code", "")),
                "description": f"{g.get('source', 'Diretriz')} · {g.get('year', '2026')}",
                "href": f"/biblioteca?q={slugify(g.get('title', ''))}",
                "badge": "Biblioteca",
            })

    for d in diagnoses:
        for tc in d.get("related_tool_codes") or []:
            label = d.get("name_pt") or d.get("name") or d.get("diagnosis_code", "")
            add(tc, "nanda", {
                "title": label,
                "description": "Diagnóstico NANDA-I · SAE",
                "href": f"/nanda?q={slugify(label)}",
                "badge": "SAE / NANDA",
            })

    for tool in tools:
        tc = tool["tool_code"]
        defn = definitions.get(tc) or {}
        for dc in defn.get("related_diagnosis_codes") or []:
            diag = next((x for x in diagnoses if x.get("diagnosis_code") == dc), None)
            if diag:
                label = diag.get("name_pt") or diag.get("name") or dc
                add(tc, "nanda", {
                    "title": label,
                    "description": "Diagnóstico NANDA-I vinculado à ferramenta",
                    "href": f"/nanda?q={slugify(label)}",
                    "badge": "SAE / NANDA",
                })
        if defn.get("related_diagnosis_codes") or "SAE" in (tool.get("taxonomy_code") or ""):
            add(tc, "nanda", {
                "title": "SAE — Processo de Enfermagem",
                "description": "Sistematização integrada NANDA · NIC · NOC",
                "href": "/sae",
                "badge": "SAE",
            })

    for course in courses:
        for tc in _text_links_tools(course.get("title_pt", course.get("title", "")), tools, slug_map):
            add(tc, "courses", {
                "title": course.get("title_pt", course.get("title", "Curso")),
                "description": f"{course.get('provider', 'NKOS')} · {course.get('modality', 'online')} · {course.get('ceu_hours', 0)}h",
                "href": "/cursos",
                "badge": "Curso",
            })

    for job in jobs:
        for tc in _text_links_tools(job.get("title_pt", job.get("title", "")), tools, slug_map):
            add(tc, "jobs", {
                "title": job.get("title_pt", job.get("title", "Vaga")),
                "description": f"{job.get('region_pt', 'Brasil')} · {job.get('employment_type', 'CLT')}",
                "href": "/empregos",
                "badge": "Vaga",
            })

    mm = (template_pages.get("pages") or {}).get("mapas_mentais") or {}
    mm_text = " ".join(
        [mm.get("title", ""), mm.get("subtitle", "")]
        + [n.get("title", "") for n in mm.get("nodes", [])]
        + [item for n in mm.get("nodes", []) for item in n.get("items", [])]
    )
    mm_tools = set(_text_links_tools(mm_text, tools, slug_map))
    for tool in tools:
        tc = tool["tool_code"]
        slug = slug_map[tc]
        if tc not in mm_tools:
            continue
        add(tc, "mindmaps", {
            "title": f"Mapas Mentais — {tool.get('acronym', slug)}",
            "description": "Visualização de conceitos clínicos e metas IPSG",
            "href": f"/mapas-mentais?q={slugify(tool.get('acronym', slug))}",
            "badge": "Mapa Mental",
        })

    nanda_to_tools = _build_nanda_to_tools(diagnoses, entity_relations)
    lookups = _build_content_lookups(
        quizzes=quizzes,
        flashcards=flashcards or [],
        protocols=protocols or [],
        competencies=competencies or [],
        exams=exams,
        interventions=interventions or [],
        nnn_linkages=nnn_linkages or [],
        nanda_to_tools=nanda_to_tools,
    )

    for interv in interventions or []:
        ic = interv.get("intervention_code", "")
        label = interv.get("name_pt") or interv.get("name") or ic
        for tc in interv.get("related_tool_codes") or []:
            add(tc, "nic", {
                "title": label,
                "description": "Intervenção NIC · SAE",
                "href": f"/nic?q={slugify(label)}",
                "badge": "NIC",
            })

    for link in nnn_linkages or []:
        dc = link.get("diagnosis_code", "")
        ic = link.get("intervention_code", "")
        oc = link.get("outcome_code", "")
        title = f"NNN {dc.replace('NANDA.', '')} · {ic} · {oc}"
        for tc in nanda_to_tools.get(dc, []):
            add(tc, "nnn", {
                "title": title,
                "description": f"Ligação NNN · {link.get('strength', 'moderate')}",
                "href": f"/nanda?q={slugify(dc)}",
                "badge": "NNN",
            })

    for outcome in outcomes or []:
        oc = outcome.get("outcome_code", "")
        label = outcome.get("name_pt") or outcome.get("name") or oc
        for tc in lookups["noc_to_tools"].get(oc, []):
            add(tc, "noc", {
                "title": label,
                "description": "Desfecho NOC · SAE",
                "href": f"/noc?q={slugify(label)}",
                "badge": "NOC",
            })

    for rule in reassessment_rules or []:
        tc = rule.get("tool_code")
        if not tc or tc not in index:
            continue
        slug = slug_map.get(tc, slugify(tc.replace("TOOL.", "")))
        add(tc, "reassessment", {
            "title": f"Reavaliação · {rule.get('interval_hours', '—')}h",
            "description": (rule.get("condition_pt") or "Regra de reavaliação clínica")[:120],
            "href": f"/ferramentas/{slug}",
            "badge": "Reavaliação",
        })

    if contents:
        _apply_content_records(index, contents, tools, slug_map, lookups, add)

    for entry in glossary or []:
        lc = entry.get("linked_code", "")
        if not lc.startswith("NANDA."):
            continue
        label = entry.get("term_pt") or entry.get("term_en") or entry.get("entry_code", "")
        for tc in nanda_to_tools.get(lc, []):
            add(tc, "glossary", {
                "title": label[:100],
                "description": f"Glossário · {entry.get('category', 'termo clínico')}",
                "href": f"/glossario?q={slugify(label)}",
                "badge": "Glossário",
            })

    for topic in forum_topics or []:
        title = topic.get("title_pt", topic.get("forum_topic_code", "Fórum"))
        slug = topic.get("slug", slugify(title))
        for tc in topic.get("linked_tool_codes") or []:
            add(tc, "forum", {
                "title": title[:100],
                "description": f"Fórum · {topic.get('specialty', 'discussão')} · {topic.get('post_count', 0)} posts",
                "href": f"/forum?q={slugify(slug)}",
                "badge": "Fórum",
            })

    for path in career_paths or []:
        title = path.get("title_pt", path.get("career_path_code", "Carreira"))
        for tc in path.get("linked_tool_codes") or []:
            add(tc, "career", {
                "title": title,
                "description": "Trilha de carreira · " + " · ".join(path.get("milestones_pt", [])[:2]),
                "href": f"/curriculo?q={slugify(title)}",
                "badge": "Carreira",
            })

    for tool in tools:
        tc = tool["tool_code"]
        acronym = tool.get("acronym") or slug_map[tc]
        add(tc, "casos", {
            "title": f"Casos Clínicos — {acronym}",
            "description": "Estudos de caso e discussão clínica aplicada",
            "href": f"/casos?q={slugify(acronym)}",
            "badge": "Caso Clínico",
        })

    return index


def build_tool_ecosystem_items(
    tool: dict,
    *,
    resource_index: dict[str, dict],
    protocols: list[dict],
    competencies: list[dict],
    slug_map: dict[str, str],
    depth: int,
    extended_index: dict[str, dict[str, list]] | None = None,
) -> list[dict]:
    """All site content linked to one clinical calculator/scale."""
    code = tool["tool_code"]
    slug = slug_map[code]
    kind_id, kind_label = _tool_kind_label(tool)
    acronym = tool.get("acronym") or code.replace("TOOL.", "")
    items: list[dict] = []

    items.append(_eco_item(
        tool_code=code,
        resource_type="tool",
        title=tool["name"],
        description=f"{kind_label} · {tool.get('domain', tool.get('category', ''))}",
        href=route_href(f"/ferramentas/{slug}", depth),
        badge=kind_label,
        views=3000,
        featured=True,
    ))

    res = resource_index.get(code, {})
    for i, q in enumerate(res.get("quizzes", [])):
        items.append(_eco_item(
            tool_code=code,
            resource_type="quiz",
            title=q.get("title", "Quiz"),
            description=f"Quiz · {q.get('difficulty', 'Médio')} · {q.get('questions', 0)} questões",
            href=route_href("/quiz", depth) + f"?q={slugify(q.get('title', acronym))}",
            badge="Quiz",
            views=800 - i * 20,
            featured=i == 0,
        ))

    fc_count = res.get("flashcard_count", 0)
    if fc_count:
        items.append(_eco_item(
            tool_code=code,
            resource_type="flashcard",
            title=f"Flashcards {acronym}",
            description=f"{fc_count} cartões de revisão · {acronym}",
            href=route_href("/flashcards", depth) + f"?q={slugify(acronym)}",
            badge="Flashcards",
            views=600,
            featured=True,
        ))

    for i, path in enumerate(res.get("paths", [])):
        items.append(_eco_item(
            tool_code=code,
            resource_type="path",
            title=path.get("title", "Trilha"),
            description=f"Trilha · {path.get('step', 'passo')}",
            href=route_href("/trilhas", depth),
            badge="Trilha",
            views=500 - i * 30,
        ))

    from protocol_lib import protocol_slug

    for i, p in enumerate(protocols):
        if code not in (p.get("related_tool_codes") or []):
            continue
        items.append(_eco_item(
            tool_code=code,
            resource_type="protocol",
            title=p.get("title", p.get("protocol_code", "")),
            description=_protocol_description(p),
            href=route_href(f"/protocolos/{protocol_slug(p)}", depth),
            badge="Protocolo",
            views=700 - i * 25,
            featured=i < 2,
        ))

    for i, c in enumerate(competencies):
        if code not in (c.get("linked_tool_codes") or []):
            continue
        title = c.get("title_pt") or c.get("domain_name_pt") or c.get("competency_code", "")
        items.append(_eco_item(
            tool_code=code,
            resource_type="competency",
            title=title,
            description=c.get("description_pt", f"Competência · {c.get('level_name_pt', '')}"),
            href=route_href("/competencias", depth) + f"?q={slugify(title)}",
            badge="Competência",
            views=max(80, 400 - i * 10),
        ))

    ext = (extended_index or {}).get(code, {})
    _EXT_BUCKETS = (
        ("articles", "article", "Artigo"),
        ("simulados", "simulado", "Simulado"),
        ("concursos", "concurso", "Concurso"),
        ("courses", "course", "Curso"),
        ("jobs", "job", "Vaga"),
        ("casos", "caso", "Caso Clínico"),
        ("mindmaps", "mindmap", "Mapa Mental"),
        ("guidelines", "library", "Biblioteca"),
        ("nanda", "sae", "SAE / NANDA"),
        ("nic", "nic", "NIC"),
        ("noc", "noc", "NOC"),
        ("nnn", "nnn", "NNN"),
        ("drugs", "drug", "Medicamento"),
        ("labs", "lab", "Laboratório"),
        ("safety", "safety", "Segurança"),
        ("reassessment", "reassessment", "Reavaliação"),
        ("flashcards_extra", "flashcard", "Flashcard"),
        ("glossary", "glossary", "Glossário"),
        ("forum", "forum", "Fórum"),
        ("career", "career", "Carreira"),
    )
    _EXT_LIMITS = {
        "guidelines": 3, "nanda": 4, "courses": 3, "jobs": 2, "casos": 1, "mindmaps": 2,
        "nic": 4, "noc": 4, "nnn": 3, "drugs": 2, "labs": 3, "safety": 2,
        "reassessment": 1, "flashcards_extra": 3, "glossary": 2, "forum": 2, "career": 1,
    }
    for bucket, rtype, default_badge in _EXT_BUCKETS:
        cap = _EXT_LIMITS.get(bucket, 6)
        for j, link in enumerate(ext.get(bucket, [])[:cap]):
            raw_href = link["href"]
            base, _, qs = raw_href.partition("?")
            resolved = route_href(base if base.startswith("/") else f"/{base.lstrip('/')}", depth)
            if qs:
                resolved += f"?{qs}"
            items.append(_eco_item(
                tool_code=code,
                resource_type=rtype,
                title=link["title"],
                description=link.get("description", default_badge),
                href=resolved,
                badge=link.get("badge", default_badge),
                filter_tags=[link.get("badge", default_badge)],
                views=350 - j * 15,
                featured=bucket in ("articles", "simulados", "guidelines"),
            ))

    return items


def build_tool_concepts_orchestrator(
    tools: list[dict],
    *,
    quizzes: list[dict],
    flashcards: list[dict],
    paths: list[dict],
    protocols: list[dict],
    competencies: list[dict],
    slug_map: dict[str, str],
    depth: int,
    articles: list[dict] | None = None,
    exams: list[dict] | None = None,
    guidelines: list[dict] | None = None,
    diagnoses: list[dict] | None = None,
    definitions: dict[str, dict] | None = None,
    courses: list[dict] | None = None,
    jobs: list[dict] | None = None,
    template_pages: dict | None = None,
    contents: list[dict] | None = None,
    interventions: list[dict] | None = None,
    outcomes: list[dict] | None = None,
    nnn_linkages: list[dict] | None = None,
    entity_relations: list[dict] | None = None,
    reassessment_rules: list[dict] | None = None,
    glossary: list[dict] | None = None,
    forum_topics: list[dict] | None = None,
    career_paths: list[dict] | None = None,
) -> dict:
    """Build orchestrator data: each concept = one clinical calculator or scale."""
    resource_index = build_tool_resource_index(quizzes, flashcards, paths)
    extended_index = build_extended_ecosystem_index(
        tools,
        slug_map=slug_map,
        quizzes=quizzes,
        exams=exams or [],
        articles=articles or [],
        guidelines=guidelines or [],
        diagnoses=diagnoses or [],
        definitions=definitions or {},
        courses=courses or [],
        jobs=jobs or [],
        template_pages=template_pages or {},
        contents=contents,
        interventions=interventions,
        outcomes=outcomes,
        nnn_linkages=nnn_linkages,
        entity_relations=entity_relations,
        reassessment_rules=reassessment_rules,
        competencies=competencies,
        protocols=protocols,
        flashcards=flashcards,
        glossary=glossary,
        forum_topics=forum_topics,
        career_paths=career_paths,
    )
    concepts: list[dict] = []
    ecosystems: dict[str, dict] = {}
    all_items: list[dict] = []

    for tool in tools:
        code = tool["tool_code"]
        kind_id, kind_label = _tool_kind_label(tool)
        acronym = tool.get("acronym") or code.replace("TOOL.", "")
        eco_items = build_tool_ecosystem_items(
            tool,
            resource_index=resource_index,
            protocols=protocols,
            competencies=competencies,
            slug_map=slug_map,
            depth=depth,
            extended_index=extended_index,
        )
        ecosystems[code] = {
            "tool_code": code,
            "slug": slugify(acronym),
            "title": acronym,
            "full_name": tool["name"],
            "kind": kind_id,
            "kind_label": kind_label,
            "hero_title": f"{acronym} — {kind_label}",
            "hero_subtitle": (
                f"Ecossistema {acronym}: {kind_label.lower()}, artigos, casos, simulados, protocolos, "
                f"SAE/NANDA/NIC/NOC, medicamentos, biblioteca, reavaliação, cursos, vagas, "
                f"quiz, flashcards e trilhas."
            ),
            "resource_count": len(eco_items),
            "items": eco_items,
        }
        concepts.append({
            "id": code,
            "slug": slugify(acronym),
            "title": acronym,
            "subtitle": kind_label,
            "full_name": tool["name"],
            "kind": kind_id,
            "kind_label": kind_label,
            "icon": _tool_concept_icon(tool),
            "color": _tool_concept_color(tool),
            "resource_count": len(eco_items),
        })
        all_items.extend(eco_items)

    return {
        "concepts": concepts,
        "ecosystems": ecosystems,
        "all_items": all_items,
    }


def merge_orchestrator_hub(
    template: dict,
    concepts_data: dict,
) -> dict:
    """Merge static hub template with generated tool concepts."""
    hub = {**template}
    hub["concepts"] = concepts_data["concepts"]
    hub["categories"] = [
        {"id": "all", "title": "Todos os tipos", "icon": "grid", "color": "teal", "active": True},
        {"id": "tool", "title": "Ferramenta", "icon": "calculator", "color": "purple"},
        {"id": "article", "title": "Artigos", "icon": "document", "color": "blue"},
        {"id": "caso", "title": "Casos Clínicos", "icon": "clipboard", "color": "navy"},
        {"id": "simulado", "title": "Simulados", "icon": "heart", "color": "red"},
        {"id": "concurso", "title": "Concursos", "icon": "shield", "color": "orange"},
        {"id": "quiz", "title": "Quiz", "icon": "clipboard", "color": "blue"},
        {"id": "flashcard", "title": "Flashcards", "icon": "book", "color": "green"},
        {"id": "path", "title": "Trilhas", "icon": "brain", "color": "navy"},
        {"id": "protocol", "title": "Protocolos", "icon": "shield", "color": "teal"},
        {"id": "sae", "title": "SAE / NANDA", "icon": "book", "color": "green"},
        {"id": "library", "title": "Biblioteca", "icon": "document", "color": "teal"},
        {"id": "course", "title": "Cursos", "icon": "book", "color": "purple"},
        {"id": "job", "title": "Vagas", "icon": "users", "color": "orange"},
        {"id": "mindmap", "title": "Mapas Mentais", "icon": "brain", "color": "navy"},
        {"id": "competency", "title": "Competências", "icon": "users", "color": "orange"},
        {"id": "nic", "title": "NIC", "icon": "book", "color": "green"},
        {"id": "noc", "title": "NOC", "icon": "book", "color": "teal"},
        {"id": "nnn", "title": "NNN", "icon": "shield", "color": "purple"},
        {"id": "drug", "title": "Medicamentos", "icon": "pill", "color": "red"},
        {"id": "lab", "title": "Laboratório", "icon": "clipboard", "color": "blue"},
        {"id": "safety", "title": "Segurança", "icon": "shield", "color": "orange"},
        {"id": "reassessment", "title": "Reavaliação", "icon": "heart", "color": "navy"},
        {"id": "glossary", "title": "Glossário", "icon": "book", "color": "blue"},
        {"id": "forum", "title": "Fórum", "icon": "users", "color": "teal"},
        {"id": "career", "title": "Carreira", "icon": "brain", "color": "purple"},
    ]
    hub["filters"] = [
        {
            "title": "Tipo de recurso",
            "options": [
                {"label": "Ferramenta"}, {"label": "Artigo"}, {"label": "Caso Clínico"},
                {"label": "Simulado"}, {"label": "Concurso"}, {"label": "Quiz"},
                {"label": "Flashcards"}, {"label": "Trilha"}, {"label": "Protocolo"},
                {"label": "SAE / NANDA"}, {"label": "Biblioteca"}, {"label": "Curso"},
                {"label": "Vaga"}, {"label": "Mapa Mental"}, {"label": "Competência"},
                {"label": "NIC"}, {"label": "NOC"}, {"label": "NNN"},
                {"label": "Medicamento"}, {"label": "Laboratório"}, {"label": "Segurança"},
                {"label": "Reavaliação"}, {"label": "Glossário"},
                {"label": "Fórum"}, {"label": "Carreira"},
            ],
        },
    ]
    hub["sections"] = {
        **hub.get("sections", {}),
        "featured_title": "Destaques do conceito",
        "recent_title": "Recursos relacionados",
        "themes_title": "Por tipo de conteúdo",
        "popular_title": "Todo o ecossistema",
    }
    return hub


def render_hub_page(
    hub: dict,
    items: list[dict],
    *,
    depth: int,
    title: str | None = None,
    description: str | None = None,
    hero_image: str | None = "hero-protocols-hub.png",
    orchestrator: dict | None = None,
    active_concept: str = "",
) -> str:
    seo = hub.get("seo", {})
    page_title = title or seo.get("title", hub["hero"]["title"])
    page_desc = description or seo.get("description", hub["hero"]["subtitle"])
    canon = hub.get("reference_page", "/protocolos")

    crumbs = [(hub["breadcrumb"][0]["label"], None)] if hub.get("breadcrumb") else []
    if hub.get("breadcrumb") and len(hub["breadcrumb"]) > 1:
        crumbs = [(b["label"], b.get("href")) for b in hub["breadcrumb"]]

    sections = hub.get("sections", {})
    prefix = "../" * depth if depth else ""
    card_style = hub.get("card_style", "default")
    concepts_html = ""
    if orchestrator:
        concepts_html = _render_hub_concepts(
            orchestrator.get("concepts", []), depth, active_id=active_concept,
        )

    main = f"""
{_render_hub_hero(hub, depth, None)}
<div class="section-container">
  {render_breadcrumbs(crumbs, depth)}
</div>
{_render_hub_profile_strip()}
{concepts_html}
{_render_category_carousel(hub.get("categories", []), len(items))}
<div class="section-container hub-layout">
  {_render_filters(hub.get("filters", []), show_extras=bool(orchestrator))}
  <div class="hub-content" data-hub-results data-hub-view-mode="grid">
    <div class="hub-concept-sections" data-hub-concept-sections hidden aria-live="polite"></div>
    <div data-hub-default-sections>
    {_render_featured(items, sections.get("featured_title", "Em destaque"), card_style=card_style)}
    {_render_recent(items, sections.get("recent_title", "Atualizados recentemente"))}
    {_render_themes(hub.get("themes", []), sections.get("themes_title", "Navegue por temas principais"))}
    {_render_popular(items, sections.get("popular_title", "Populares"))}
    </div>
    <p class="hub-empty" data-hub-empty hidden>Nenhum resultado para os filtros selecionados.</p>
  </div>
</div>
{_render_cta(hub.get("cta", {}), depth, hero_image)}"""

    extra_css = [
        f"{prefix}assets/css/home.css",
        f"{prefix}assets/css/hub.css",
    ]

    return render_document(
        depth=depth,
        title=page_title,
        description=page_desc,
        canonical_path=canon,
        main_html=main,
        extra_css=extra_css,
        main_class="site-main hub-main",
        extra_head=(
            f'<script type="application/json" id="hub-orchestrator-config-path">'
            f'"assets/data/tool-concepts-index.json"</script>'
            if orchestrator else ""
        ),
    )


def render_institutional_hub(page: dict, *, depth: int, default_links: list[dict] | None = None) -> str:
    """Minimal hub template for institutional/secondary pages with related resources."""
    links = page.get("links") or default_links or []
    items = []
    for i, link in enumerate(links):
        items.append({
            "id": slugify(link["title"]),
            "title": link["title"],
            "description": link.get("description", ""),
            "badge": link.get("type", "recurso"),
            "category": link.get("type", "recurso").title(),
            "category_id": slugify(link.get("type", "all"))[:16],
            "theme": page["title"],
            "filter_tags": [link.get("type", "recurso"), page["title"]],
            "updated": "2026",
            "updated_sort": "2026",
            "href": route_href(link["href"], depth),
            "views": 300 - i * 10,
            "featured": i < 4,
        })
    hub = {
        "reference_page": page.get("route", f"/{slugify(page['title'])}"),
        "breadcrumb": [{"label": page["title"], "href": None}],
        "hero": {
            "title": page["title"],
            "subtitle": page["subtitle"],
            "search_placeholder": f"Buscar em {page['title']}…",
            "examples": [l["title"] for l in links[:4]],
        },
        "categories": [{"id": "all", "title": "Todos", "icon": "grid", "color": "teal", "active": True}],
        "filters": [],
        "sections": {
            "featured_title": "Recursos relacionados",
            "popular_title": "Explorar",
        },
        "cta": {
            "title": "Explore a plataforma",
            "text": "Ferramentas clínicas, educação e gestão integradas.",
            "button": "Ferramentas clínicas",
            "href": "/ferramentas",
        },
        "seo": {
            "title": f'{page["title"]} | Calculadoras de Enfermagem',
            "description": page["subtitle"],
        },
    }
    return render_hub_page(hub, items, depth=depth, hero_image=None)

