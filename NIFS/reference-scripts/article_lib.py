"""Article pages — layout 2 colunas + TOC (mockup artigo científico)."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from website_lib import (
    _svg_icon,
    esc,
    render_breadcrumbs,
    render_document,
    route_href,
    slugify,
)


def _format_date(iso: str | None) -> str:
    if not iso:
        return "2026"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        months = (
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
        )
        return f"{dt.day} de {months[dt.month - 1]} de {dt.year}"
    except ValueError:
        return iso[:10]


def _render_section(section: dict) -> str:
    stype = section.get("type", "paragraph")
    if stype == "heading":
        level = min(max(section.get("level", 2), 2), 3)
        sid = section.get("id", "")
        id_attr = f' id="{esc(sid)}"' if sid else ""
        return f"<h{level}{id_attr}>{esc(section['text'])}</h{level}>"
    if stype == "paragraph":
        return f"<p>{esc(section['text'])}</p>"
    if stype == "callout":
        variant = section.get("variant", "info")
        title = section.get("title", "")
        title_html = f"<strong>{esc(title)}</strong> " if title else ""
        return f"""
<aside class="callout callout--{esc(variant)}" role="note">
  {title_html}{esc(section["text"])}
</aside>"""
    if stype == "checklist":
        items = "".join(
            f'<li><span class="article-check" aria-hidden="true">✓</span>{esc(item)}</li>'
            for item in section.get("items", [])
        )
        return f'<ul class="article-checklist">{items}</ul>'
    if stype == "cards":
        cards = "".join(
            f"""<div class="article-info-card">
  <h3>{esc(item["title"])}</h3>
  <p>{esc(item["text"])}</p>
</div>"""
            for item in section.get("items", [])
        )
        return f'<div class="article-info-grid">{cards}</div>'
    return ""


def _render_toc(toc: list[dict]) -> str:
    if not toc:
        return ""
    items = "".join(
        f'<li><a href="#{esc(item["id"])}">{esc(item["label"])}</a></li>'
        for item in toc
    )
    return f"""
<nav class="article-toc" aria-labelledby="article-toc-title">
  <h2 id="article-toc-title">Sumário</h2>
  <ol>{items}</ol>
</nav>"""


def _render_related_tools(tools: list[dict], depth: int) -> str:
    if not tools:
        return ""
    cards = []
    for tool in tools:
        href = tool.get("href", "#")
        if href.startswith("/"):
            href = route_href(href, depth)
        icon = tool.get("icon", "document")
        cards.append(f"""
<div class="article-related-card">
  <span class="article-related-card__icon">{_svg_icon(icon)}</span>
  <div>
    <strong>{esc(tool["title"])}</strong>
    <p>{esc(tool.get("description", ""))}</p>
    <a href="{esc(href)}">Ver ferramenta →</a>
  </div>
</div>""")
    return f"""
<section class="article-related" aria-labelledby="article-related-title">
  <h2 id="article-related-title">Ferramentas relacionadas</h2>
  {''.join(cards)}
</section>"""


def render_article_page(article: dict, *, depth: int) -> str:
    seo = article.get("seo", {})
    page_title = seo.get("title", article["title"])
    page_desc = seo.get("description", article.get("subtitle", ""))
    slug = article.get("slug", slugify(article.get("title", "")))
    canon = f"/artigos/{slug}"

    crumbs = [
        ("Artigos", route_href("/artigos", depth)),
        (article["title"][:48] + ("…" if len(article["title"]) > 48 else ""), None),
    ]

    tags_html = "".join(
        f'<span class="tag-pill">#{esc(tag)}</span>'
        for tag in article.get("tags", [])[:6]
    )
    author = article.get("author", {})
    sections_html = "".join(_render_section(s) for s in article.get("sections", []))
    prefix = "../" * depth if depth else ""

    main = f"""
<div class="section-container article-breadcrumb-wrap">
  {render_breadcrumbs(crumbs, depth)}
</div>
<article class="article-page">
  <header class="article-header section-container">
    <div class="article-header__meta">
      <span class="badge-validated">{esc(article.get("content_type", "Artigo"))}</span>
      <span class="article-header__read">{esc(article.get("read_minutes", 5))} min de leitura</span>
    </div>
    <h1 class="article-header__title">{esc(article["title"])}</h1>
    <p class="article-header__subtitle">{esc(article.get("subtitle", ""))}</p>
    <div class="article-header__author">
      <div class="article-author-avatar" aria-hidden="true">{esc(author.get("name", "CE")[:1])}</div>
      <div>
        <strong>{esc(author.get("name", "Equipe Calculadoras de Enfermagem"))}</strong>
        <span>{esc(author.get("role", ""))}</span>
      </div>
      <div class="article-header__dates">
        <time datetime="{esc(article.get("updated_at", ""))}">Atualizado em {_format_date(article.get("updated_at"))}</time>
        <time datetime="{esc(article.get("published_at", ""))}">Publicado em {_format_date(article.get("published_at"))}</time>
      </div>
    </div>
    <div class="article-header__tags">{tags_html}</div>
  </header>
  <div class="section-container article-layout">
    <aside class="article-sidebar">
      {_render_toc(article.get("toc", []))}
      {_render_related_tools(article.get("related_tools", []), depth)}
    </aside>
    <div class="article-content">
      {sections_html}
    </div>
  </div>
</article>"""

    return render_document(
        depth=depth,
        title=page_title,
        description=page_desc,
        canonical_path=canon,
        main_html=main,
        extra_css=[f"{prefix}assets/css/article.css"],
        main_class="site-main article-main",
        og_type="article",
    )


def render_simulation_page(exam: dict, *, depth: int, quizzes: list[dict] | None = None) -> str:
    slug = slugify(exam.get("exam_code", exam.get("title_pt", "simulado")))
    title = exam.get("title_pt", exam.get("title", "Simulado"))
    seo_title = f"{title} | Simulados de Enfermagem"
    seo_desc = f"Simulado formativo com {exam.get('question_count', 20)} questões — {exam.get('duration_min', 30)} min."
    difficulty = _simulation_difficulty(exam)
    prefix = "../" * depth if depth else ""

    quiz_by_code = {q["quiz_code"]: q for q in (quizzes or [])}
    questions = []
    for code in exam.get("linked_quiz_codes") or []:
        quiz = quiz_by_code.get(code)
        if not quiz:
            continue
        for q in quiz.get("questions", [])[:2]:
            questions.append({
                "text": q.get("text_pt", q.get("text", "")),
                "options": [{"id": o["option_id"], "text": o.get("text_pt", o.get("text", ""))} for o in q.get("options", [])],
                "correct": q.get("correct_option_id", "A"),
                "explanation": q.get("explanation_pt", ""),
            })
            if len(questions) >= exam.get("question_count", 10):
                break
        if len(questions) >= exam.get("question_count", 10):
            break

    quiz_json = json.dumps(questions[: exam.get("question_count", 10)], ensure_ascii=False)
    passing = exam.get("passing_score_pct", 60)
    has_questions = len(questions) > 0

    quiz_block = ""
    if has_questions:
        quiz_block = f"""
  <section class="sim-quiz is-hidden" data-sim-quiz data-passing="{esc(passing)}">
    <p class="sim-quiz__progress" data-sim-progress>Questão 1 de {len(questions)}</p>
    <p class="sim-quiz__question" data-sim-question></p>
    <div class="sim-quiz__options" data-sim-options></div>
    <button type="button" class="btn-primary-sm is-hidden" data-sim-next>Próxima questão</button>
    <div class="sim-quiz__result is-hidden" data-sim-result></div>
  </section>
  <script type="application/json" id="sim-quiz-data">{quiz_json}</script>"""
    else:
        quiz_block = """
  <p class="sim-detail-empty" role="status">Questões indisponíveis no momento.</p>"""

    crumbs = [
        ("Simulados", route_href("/simulados", depth)),
        (title[:40] + ("…" if len(title) > 40 else ""), None),
    ]

    main = f"""
<div class="section-container article-breadcrumb-wrap">
  {render_breadcrumbs(crumbs, depth)}
</div>
<div class="section-container">
  <header class="sim-detail-header">
    <span class="badge-validated">Simulado formativo</span>
    <h1>{esc(title)}</h1>
    <p class="sim-detail-header__stats">
      <span>{esc(len(questions) or exam.get("question_count", 20))} questões</span>
      <span>{esc(exam.get("duration_min", 30))} min</span>
      <span>Dificuldade: {esc(difficulty)}</span>
      <span>Nota mínima: {esc(passing)}%</span>
    </p>
  </header>
  <div class="sim-detail-grid" data-sim-intro>
    <section class="card sim-detail-card">
      <h2>Sobre este simulado</h2>
      <p>Questões selecionadas da plataforma 2026 com feedback ao final. Ideal para revisão antes de provas e certificações.</p>
      <ul class="article-checklist">
        <li><span class="article-check" aria-hidden="true">✓</span>Embaralhamento de questões</li>
        <li><span class="article-check" aria-hidden="true">✓</span>Feedback comentado</li>
        <li><span class="article-check" aria-hidden="true">✓</span>Registro de desempenho local</li>
      </ul>
      <button type="button" class="btn-primary-sm" data-sim-start{" disabled" if not has_questions else ""}>Iniciar simulado</button>
    </section>
    <aside class="card sim-detail-sidebar" data-sim-results>
      <h2>Seus últimos resultados</h2>
      <p class="sim-detail-empty">Nenhum resultado registrado ainda.</p>
    </aside>
  </div>{quiz_block}
</div>"""

    return render_document(
        depth=depth,
        title=seo_title,
        description=seo_desc,
        canonical_path=f"/simulados/{slug}",
        main_html=main,
        extra_css=[f"{prefix}assets/css/article.css", f"{prefix}assets/css/templates.css"],
        main_class="site-main sim-main",
    )


def _simulation_difficulty(exam: dict) -> str:
    pct = exam.get("passing_score_pct", 70)
    qs = exam.get("question_count", 20)
    if pct >= 70 and qs >= 45:
        return "Difícil"
    if pct <= 60 or qs <= 25:
        return "Fácil"
    return "Médio"
