"""Clinical tool pages — template routing, DB bindings, standard website CSS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from website_lib import (
    BRAND,
    BRAND_FRAMEWORK,
    SITE_NAME,
    brand_text,
    esc,
    image_href,
    load_json,
    rel_prefix,
    render_breadcrumbs,
    render_document,
    route_href,
    slugify,
    tool_page_href,
)

from content_paths import content_path

DATASETS = Path(__file__).resolve().parents[1] / "datasets"
_TEMPLATES: dict | None = None
_BINDINGS: dict | None = None
_RESOURCE_INDEX: dict[str, dict] | None = None
_ENRICHMENT: dict | None = None


def build_tool_resource_index(
    quizzes: list[dict],
    flashcards: list[dict],
    paths: list[dict] | None = None,
) -> dict[str, dict]:
    """Map tool_code → linked quiz, flashcard, trilha."""
    index: dict[str, dict] = {}
    for q in quizzes:
        code = q.get("linked_tool_code")
        if not code:
            continue
        entry = index.setdefault(code, {"quizzes": [], "flashcard_count": 0, "paths": [], "flashcards": []})
        entry["quizzes"].append({
            "code": q.get("quiz_code", ""),
            "title": q.get("title_pt", q.get("title", "")),
            "difficulty": q.get("difficulty", ""),
            "questions": q.get("question_count", 0),
        })
    for fc in flashcards:
        code = fc.get("linked_entity_code", "")
        if not code.startswith("TOOL."):
            continue
        entry = index.setdefault(code, {"quizzes": [], "flashcard_count": 0, "paths": [], "flashcards": []})
        entry["flashcard_count"] += 1
        if len(entry["flashcards"]) < 6:
            entry["flashcards"].append({
                "code": fc.get("flashcard_code", ""),
                "front": fc.get("front_pt", fc.get("front_en", ""))[:80],
            })
    for path in paths or []:
        added_paths: set[str] = set()
        for step in path.get("steps", []):
            tc = step.get("tool_code")
            if not tc:
                continue
            pcode = path.get("path_code", "")
            if pcode in added_paths:
                continue
            added_paths.add(pcode)
            entry = index.setdefault(tc, {"quizzes": [], "flashcard_count": 0, "paths": [], "flashcards": []})
            entry["paths"].append({
                "code": pcode,
                "title": path.get("title_pt", path.get("title", "")),
                "step": step.get("label_pt", step.get("step_type", "")),
            })
    return index


def _load_enrichment() -> dict:
    global _ENRICHMENT
    if _ENRICHMENT is not None:
        return _ENRICHMENT
    diagnoses = load_json(DATASETS / "clinical" / "nursing_diagnoses.json")["records"]
    interventions = load_json(DATASETS / "clinical" / "nursing_interventions.json")["records"]
    outcomes = load_json(DATASETS / "clinical" / "nursing_outcomes.json")["records"]
    evidence_list = load_json(DATASETS / "clinical" / "evidence.json")["records"]
    ipsgs = load_json(DATASETS / "clinical" / "patient_safety_goals.json")["records"]
    nine_rights = None
    for d in load_json(DATASETS / "clinical" / "calculator_definitions.json")["records"]:
        if d.get("tool_code") == "TOOL.9RIGHTS":
            nine_rights = d
            break

    evidence_by_code = {e["evidence_code"]: e for e in evidence_list}
    ipsg_by_code = {g["goal_code"]: g for g in ipsgs}
    nanda_by_tool: dict[str, list] = {}
    nanda_by_code = {d["diagnosis_code"]: d for d in diagnoses}
    for d in diagnoses:
        for tc in d.get("related_tool_codes") or []:
            nanda_by_tool.setdefault(tc, []).append(d)
    nic_by_tool: dict[str, list] = {}
    for i in interventions:
        for tc in i.get("related_tool_codes") or []:
            nic_by_tool.setdefault(tc, []).append(i)
    noc_sample = outcomes[:20]

    _ENRICHMENT = {
        "evidence_by_code": evidence_by_code,
        "ipsg_by_code": ipsg_by_code,
        "nanda_by_tool": nanda_by_tool,
        "nanda_by_code": nanda_by_code,
        "nic_by_tool": nic_by_tool,
        "noc_sample": noc_sample,
        "nine_rights_def": nine_rights,
    }
    return _ENRICHMENT


def get_tool_enrichment(tool: dict, definition: dict | None) -> dict:
    enrich = _load_enrichment()
    templates, _ = _load_registry()
    code = tool.get("tool_code", "")
    res = _get_resources(code)

    nanda: list[dict] = []
    seen_n: set[str] = set()
    for dc in (definition or {}).get("related_diagnosis_codes") or []:
        if dc in enrich["nanda_by_code"] and dc not in seen_n:
            nanda.append(enrich["nanda_by_code"][dc])
            seen_n.add(dc)
    for d in enrich["nanda_by_tool"].get(code, [])[:5]:
        if d["diagnosis_code"] not in seen_n:
            nanda.append(d)
            seen_n.add(d["diagnosis_code"])

    nic = enrich["nic_by_tool"].get(code, [])[:6]
    noc = enrich["noc_sample"][:4]

    domain = tool.get("domain", "general")
    ipsg_codes = templates.get("universal_shell", {}).get("ipsg_by_domain", {}).get(
        domain, templates.get("universal_shell", {}).get("ipsg_default", ["IPSG01", "IPSG05"])
    )
    ipsgs = [enrich["ipsg_by_code"][c] for c in ipsg_codes if c in enrich["ipsg_by_code"]]

    ev_code = (definition or {}).get("evidence_code")
    evidence = enrich["evidence_by_code"].get(ev_code) if ev_code else None

    tags = []
    for t in (tool.get("acronym"), tool.get("domain"), tool.get("category"), tool.get("tool_type")):
        if t:
            tags.append("#" + slugify(str(t).replace("_", "-")))
    tags.extend(["#CalculadorasEnfermagem", "#enfermagem", "#segurancadopaciente"])

    med_types = templates.get("universal_shell", {}).get("medication_tool_types", [])
    show_nine = tool.get("tool_type") in med_types or code == "TOOL.9RIGHTS"

    return {
        "resources": res,
        "nanda": nanda[:8],
        "nic": nic,
        "noc": noc,
        "ipsgs": ipsgs,
        "evidence": evidence,
        "reference_framework": brand_text((definition or {}).get("reference_framework", BRAND_FRAMEWORK)),
        "formula": (definition or {}).get("formula", ""),
        "hashtags": tags,
        "show_nine_rights": show_nine,
        "nine_rights_params": (enrich["nine_rights_def"] or {}).get("parameters", []),
    }


def _get_resources(tool_code: str) -> dict:
    global _RESOURCE_INDEX
    if _RESOURCE_INDEX is None:
        quizzes = load_json(DATASETS / "education" / "quizzes.json")["records"]
        flashcards = load_json(DATASETS / "education" / "flashcards.json")["records"]
        paths = load_json(DATASETS / "education" / "learning_paths.json")["records"]
        _RESOURCE_INDEX = build_tool_resource_index(quizzes, flashcards, paths)
    return _RESOURCE_INDEX.get(tool_code, {"quizzes": [], "flashcard_count": 0, "paths": [], "flashcards": []})


def _resolve_charts(binding: dict, definition: dict | None) -> list[str]:
    if binding.get("charts"):
        return binding["charts"]
    _, bindings = _load_registry()
    calc = (definition or {}).get("calculation_type", "formula")
    return bindings.get("default_tool_charts", {}).get(calc, ["score_gauge"])


def _tooltip_icon(text: str, label: str = "Ajuda") -> str:
    if not text:
        return ""
    return (
        f'<button type="button" class="tool-tip-trigger" data-tooltip="{esc(text)}" '
        f'aria-label="{esc(label)}: {esc(text[:80])}">?</button>'
    )


def _load_registry() -> tuple[dict, dict]:
    global _TEMPLATES, _BINDINGS
    if _TEMPLATES is None:
        _TEMPLATES = load_json(content_path("tool_templates"))
    if _BINDINGS is None:
        _BINDINGS = load_json(content_path("tool_ui_bindings"))
    return _TEMPLATES, _BINDINGS


def resolve_template(tool: dict, definition: dict | None) -> tuple[str, dict]:
    """Return (template_code, tool_binding)."""
    _, bindings = _load_registry()
    code = tool.get("tool_code", "")
    tool_bind = bindings.get("tools", {}).get(code, {})

    if tool_bind.get("template"):
        return tool_bind["template"], tool_bind

    ttype = tool.get("tool_type", "")
    by_type = bindings.get("defaults_by_tool_type", {}).get(ttype)
    if by_type:
        return by_type["template"], tool_bind

    calc_type = (definition or {}).get("calculation_type", "formula")
    by_calc = bindings.get("defaults_by_calculation_type", {}).get(calc_type, {})
    return by_calc.get("template", "TPL.CALCULATOR"), tool_bind


def _render_user_customization(depth: int) -> str:
    profiles = load_json(DATASETS / "users" / "personalization_profiles.json")["records"]
    options = "".join(
        f'<option value="{esc(p["profile_code"])}">{esc(p["name_pt"])}</option>'
        for p in profiles if p.get("is_template")
    )
    return f"""
<section class="tool-customize" aria-labelledby="tool-customize-title" data-tool-customize>
  <div class="tool-customize__head">
    <h2 id="tool-customize-title">Personalização</h2>
    <button type="button" class="tool-customize__toggle" data-tool-customize-toggle aria-expanded="false">Ajustar visualização</button>
  </div>
  <div class="tool-customize__panel" hidden>
    <label class="tool-field" for="tool-user-profile">
      <span class="tool-field__label">Perfil de usuário {_tooltip_icon("Define módulos prioritários, densidade e modo de cálculo padrão.")}</span>
      <select id="tool-user-profile" data-tool-user-profile>{options}</select>
    </label>
    <label class="tool-field" for="tool-layout-density">
      <span class="tool-field__label">Densidade do layout</span>
      <select id="tool-layout-density" data-tool-layout-density>
        <option value="compact">Compacto</option>
        <option value="normal" selected>Normal</option>
        <option value="comfortable">Confortável</option>
      </select>
    </label>
    <fieldset class="tool-customize__sections">
      <legend>Seções visíveis</legend>
      <label><input type="checkbox" data-tool-section="charts" aria-label="Gráficos" checked> Gráficos</label>
      <label><input type="checkbox" data-tool-section="memory" aria-label="Memória de cálculo" checked> Memória de cálculo</label>
      <label><input type="checkbox" data-tool-section="resources" aria-label="Recursos adicionais" checked> Recursos adicionais</label>
      <label><input type="checkbox" data-tool-section="relationships" aria-label="Relacionamentos clínicos" checked> Relacionamentos clínicos</label>
    </fieldset>
  </div>
</section>"""


def _render_action_bar(tool_name: str) -> str:
    return """
<div class="tool-action-bar" role="toolbar" aria-label="Ações da ferramenta" data-tool-post-calc="bar" hidden>
  <button type="button" class="tool-action-btn" data-tool-action="pdf" title="Gerar relatório PDF">📄 PDF</button>
  <button type="button" class="tool-action-btn" data-tool-action="print" title="Imprimir resultado">🖨 Imprimir</button>
  <button type="button" class="tool-action-btn" data-tool-action="copy" title="Copiar resultado">📋 Copiar</button>
  <button type="button" class="tool-action-btn" data-tool-action="share" title="Compartilhar">🔗 Compartilhar</button>
  <button type="button" class="tool-action-btn" data-tool-action="save" title="Salvar no histórico local">💾 Salvar</button>
  <button type="button" class="tool-action-btn" data-tool-action="new" title="Novo cálculo">↻ Novo</button>
</div>"""


def _render_charts_panel(charts: list[str]) -> str:
    panels = []
    labels = {
        "domain_bars": "Desempenho por domínio",
        "score_gauge": "Escore total",
        "risk_donut": "Distribuição de risco",
        "result_sparkline": "Tendência recente",
        "completion_ring": "Conclusão do checklist",
        "classification_scale": "Classificação",
        "kpi_grid": "Indicadores",
    }
    for chart in charts:
        panels.append(f"""
<div class="tool-chart-card" data-tool-chart="{esc(chart)}" data-tool-section-block="charts">
  <h3>{esc(labels.get(chart, chart))} {_tooltip_icon("Gráfico gerado a partir dos dados informados e da base de dados da plataforma.")}</h3>
  <div class="tool-chart-canvas" aria-live="polite"></div>
</div>""")
    return f"""
<section class="tool-section tool-charts" id="tool-charts-section" aria-labelledby="tool-charts-title"
  data-tool-section-block="charts" data-tool-post-calc="charts" hidden>
  <h2 id="tool-charts-title">Visualização</h2>
  <p class="tool-charts__hint" data-tool-charts-hint>Calcule para gerar gráficos interativos a partir dos dados informados.</p>
  <div class="tool-charts__grid">{"".join(panels)}</div>
</section>"""


def _render_resource_subpanel(kind: str, items: list, empty: str, depth: int) -> str:
    if not items:
        return f'<div class="tool-resource-empty"><p>{esc(empty)}</p></div>'
    lis = []
    for item in items:
        if kind == "quiz":
            lis.append(
                f'<li><strong>{esc(item["title"])}</strong>'
                f'<span>{esc(item.get("difficulty", ""))} · {esc(item.get("questions", 0))} questões</span>'
                f'<code>{esc(item.get("code", ""))}</code></li>'
            )
        elif kind == "flashcard":
            lis.append(f'<li><strong>{esc(item.get("code", ""))}</strong><span>{esc(item.get("front", ""))}</span></li>')
        elif kind == "path":
            lis.append(
                f'<li><strong>{esc(item["title"])}</strong>'
                f'<span>{esc(item.get("step", ""))}</span><code>{esc(item.get("code", ""))}</code></li>'
            )
    return f'<ul class="tool-resource-list">{"".join(lis)}</ul>'


def _render_relationships_panel(
    tool: dict,
    definition: dict | None,
    protocols: list[dict],
    tools: list[dict],
    slug_map: dict[str, str],
    depth: int,
) -> tuple[str, bool]:
    from protocol_lib import protocol_slug

    blocks: list[str] = []

    related = [p for p in protocols if tool["tool_code"] in (p.get("related_tool_codes") or [])][:6]
    if related:
        items = []
        for p in related:
            pslug = protocol_slug(p)
            href = route_href(f"/protocolos/{pslug}", depth)
            items.append(
                f'<li><a href="{esc(href)}">{esc(p.get("title", p.get("protocol_code", "")))}</a></li>'
            )
        blocks.append(f'<div class="tool-rel-block"><h3>Protocolos relacionados</h3><ul class="tool-link-list">{"".join(items)}</ul></div>')

    domain = tool.get("domain", "")
    peers = [t for t in tools if t["tool_code"] != tool["tool_code"] and t.get("domain") == domain][:4]
    if peers:
        peer_items = []
        for t in peers:
            slug = slug_map.get(t["tool_code"], slugify(t.get("acronym", "tool")))
            href = f"../{slug}/index.html" if depth >= 2 else tool_page_href(slug, "ferramentas")
            peer_items.append(f'<li><a href="{esc(href)}">{esc(t["name"])}</a></li>')
        blocks.append(
            f'<div class="tool-rel-block"><h3>Ferramentas complementares</h3>'
            f'<ul class="tool-link-list">{"".join(peer_items)}</ul></div>'
        )

    codes = (definition or {}).get("related_diagnosis_codes") or []
    if codes:
        pills = "".join(
            f'<a class="tool-pill" href="{esc(route_href("/nanda", depth))}">{esc(c)}</a>'
            for c in codes[:8]
        )
        blocks.append(
            f'<div class="tool-rel-block"><h3>Diagnósticos NANDA-I relacionados</h3>'
            f'<div class="tool-pill-row">{pills}</div></div>'
        )

    ttype = (tool.get("tool_type") or "").lower()
    hub_links = [
        ("Hub de Ferramentas", "/ferramentas"),
        ("Calculadoras Clínicas", "/calculadoras"),
        ("Escalas Clínicas", "/escalas"),
        ("Biblioteca Clínica", "/biblioteca"),
        ("Protocolos", "/protocolos"),
    ]
    if ttype == "calculator":
        hub_links.insert(0, ("Calculadoras Trabalhistas", "/calculadoras-trabalhistas"))
    eco_items = "".join(
        f'<li><a href="{esc(route_href(href, depth))}">{esc(label)}</a></li>'
        for label, href in hub_links
    )
    blocks.append(
        f'<div class="tool-rel-block"><h3>Recursos integrados</h3>'
        f'<ul class="tool-link-list">{eco_items}</ul></div>'
    )

    if not blocks:
        return '<p class="tool-resource-empty">Nenhum relacionamento catalogado para esta ferramenta.</p>', False
    return "".join(blocks), True


def _render_simulator_panel(definition: dict | None, binding: dict) -> str:
    bands = definition.get("interpretation_bands", []) if definition else []
    if not bands:
        return ""
    score_min = definition.get("score_min", 0) if definition else 0
    score_max = definition.get("score_max", 30) if definition else 30
    band_rows = "".join(
        f'<tr class="{_severity_class(b.get("severity", "low"))}">'
        f'<td>{esc(b.get("min", ""))}–{esc(b.get("max", ""))}</td>'
        f'<td>{esc(b.get("label_pt", ""))}</td>'
        f'<td>{esc(b.get("action_pt", ""))}</td></tr>'
        for b in bands
    )
    presets = binding.get("quick_presets") or []
    preset_btns = ""
    if presets:
        preset_btns = "".join(
            f'<button type="button" class="tool-preset" data-tool-simulator-preset="{esc(json.dumps(p.get("values", {}), ensure_ascii=False))}">'
            f'{esc(p.get("label", "Cenário"))}</button>'
            for p in presets[:4]
        )
        preset_btns = f'<div class="tool-simulator-presets"><span>Cenários rápidos:</span>{preset_btns}</div>'

    return f"""
<div class="tool-simulator" data-tool-simulator>
  <p class="tool-panel__lead">Simule pontuações e veja a classificação clínica correspondente — antes ou depois do cálculo real.</p>
  <div class="tool-simulator-control">
    <label for="tool-simulator-range">Pontuação simulada</label>
    <input id="tool-simulator-range" type="range" data-tool-simulator-range
      min="{esc(score_min)}" max="{esc(score_max)}" value="{esc(score_min)}" step="1">
    <output data-tool-simulator-value>{esc(score_min)}</output>
    <span class="tool-simulator-max">/ {esc(score_max)}</span>
  </div>
  <div class="tool-simulator-result" data-tool-simulator-result aria-live="polite">
    <p class="tool-simulator-result__label" data-tool-simulator-label>Ajuste o controle para simular</p>
    <p class="tool-simulator-result__action" data-tool-simulator-action></p>
  </div>
  {preset_btns}
  <table class="tool-interp-table"><thead><tr><th>Faixa</th><th>Classificação</th><th>Ação</th></tr></thead>
  <tbody>{band_rows}</tbody></table>
</div>"""


def _render_tool_page_tabs(
    tool: dict,
    definition: dict | None,
    binding: dict,
    enrich: dict,
    *,
    depth: int,
    slug_map: dict[str, str],
    relationships_html: str,
    has_relationships: bool,
    simulator_html: str,
) -> str:
    res = enrich["resources"]
    sub_tabs = []
    sub_panels = []
    quizzes = res.get("quizzes", [])
    simulados = [q for q in quizzes if q.get("difficulty") != "basic"]
    resource_defs = [
        ("quiz", "Quiz", quizzes, "Nenhum quiz vinculado a esta ferramenta na plataforma."),
        ("flashcards", "Flashcards", res.get("flashcards", []), "Nenhum flashcard vinculado a esta ferramenta."),
        ("trilhas", "Trilhas", res.get("paths", []), "Nenhuma trilha inclui esta ferramenta."),
        ("simulados", "Simulados", simulados, "Nenhum simulado vinculado a esta ferramenta."),
    ]
    first_resource = True
    for kid, label, items, empty in resource_defs:
        if not items:
            continue
        active = " is-active" if first_resource else ""
        sub_tabs.append(
            f'<button type="button" class="tool-resource-tab{active}" data-tool-resource-tab="{esc(kid)}" '
            f'aria-selected="{str(first_resource).lower()}">{esc(label)}</button>'
        )
        panel_kind = "flashcard" if kid == "flashcards" else ("path" if kid == "trilhas" else "quiz")
        sub_panels.append(
            f'<div class="tool-resource-panel{active}" '
            f'data-tool-resource-panel="{esc(kid)}"{" hidden" if not first_resource else ""}>'
            f'{_render_resource_subpanel(panel_kind, items, empty, depth)}</div>'
        )
        first_resource = False

    resources_panel = ""
    if sub_tabs:
        resources_panel = f"""
<div class="tool-resource-subtabs" role="tablist">{"".join(sub_tabs)}</div>
<div class="tool-resource-panels">{"".join(sub_panels)}</div>"""
    else:
        resources_panel = '<p class="tool-resource-empty">Sem recursos adicionais catalogados para esta ferramenta.</p>'

    nanda_rows = "".join(
        f'<li data-sae-nanda><strong>{esc(d.get("name_pt", d.get("name", "")))}</strong>'
        f'<span>{esc(d.get("diagnosis_code", ""))}</span></li>'
        for d in enrich["nanda"]
    ) or "<li>Sugestões NANDA serão exibidas após o cálculo conforme o resultado.</li>"

    nic_rows = "".join(
        f'<li><strong>{esc(n.get("name_pt", n.get("name", "")))}</strong><span>{esc(n.get("intervention_code", ""))}</span></li>'
        for n in enrich["nic"]
    ) or "<li>Nenhuma intervenção NIC pré-mapeada — consulte o plano institucional.</li>"

    noc_rows = "".join(
        f'<li><strong>{esc(n.get("name_pt", n.get("name", "")))}</strong><span>{esc(n.get("outcome_code", ""))}</span></li>'
        for n in enrich["noc"]
    )

    ev = enrich.get("evidence")
    formula_text = enrich.get("formula") or (definition.get("formula", "") if definition else "")
    ref_values_html = _render_ref_values_table(binding)
    bands = definition.get("interpretation_bands", []) if definition else []
    band_rows = "".join(
        f'<tr class="{_severity_class(b.get("severity", "low"))}">'
        f'<td>{esc(b.get("min", ""))}–{esc(b.get("max", ""))}</td>'
        f'<td>{esc(b.get("label_pt", ""))}</td>'
        f'<td>{esc(b.get("action_pt", ""))}</td></tr>'
        for b in bands
    )
    interp_in_formulas = ""
    if band_rows:
        interp_in_formulas = f"""
<h3>Interpretação clínica</h3>
<table class="tool-interp-table"><thead><tr><th>Faixa</th><th>Classificação</th><th>Ação</th></tr></thead>
<tbody>{band_rows}</tbody></table>"""

    formulas_body = f"""
<p class="tool-panel__lead">Fórmula e valores de referência integrados a esta ferramenta.</p>
<h3>Fórmula</h3>
<code class="tool-formula">{esc(formula_text) or "—"}</code>
{f'<h3>Valores de referência</h3>{ref_values_html}' if ref_values_html else ''}
{interp_in_formulas}"""

    history_body = """
<p class="tool-panel__lead">Últimos cálculos desta ferramenta no seu navegador (armazenamento local).</p>
<ul class="tool-history-list" data-tool-history-list aria-live="polite">
  <li class="tool-history-empty">Nenhum cálculo salvo ainda.</li>
</ul>"""

    disclaimer_body = """
<p>Ferramenta educativa baseada em evidências. Os resultados são auxiliares e não substituem o julgamento clínico do profissional de enfermagem.</p>
<p>Uso conforme LGPD e protocolos institucionais.</p>"""

    refs_html = f"""
<p><strong>Framework:</strong> {esc(enrich.get("reference_framework", ""))}</p>
<p><strong>Fórmula:</strong> <code>{esc(formula_text)}</code></p>
{f'<p><strong>Evidência ({esc(ev.get("framework", ""))}):</strong> {esc(ev.get("level_label", ""))} — {esc(ev.get("description", ""))}</p>' if ev else ''}
<p><strong>Nível clínico:</strong> {esc((definition or {}).get("evidence_level", "B"))}</p>
<p class="tool-ref-note">Referências completas disponíveis na <a href="{esc(route_href("/biblioteca", depth))}">Biblioteca Clínica</a>.</p>"""

    ipsg_rows = "".join(
        f'<li><strong>{esc(g["goal_code"])}</strong> — {esc(g["name"])}</li>'
        for g in enrich["ipsgs"]
    )

    nine_html = ""
    if enrich.get("show_nine_rights"):
        nine_slug = slug_map.get("TOOL.9RIGHTS", "9rights")
        nine_href = f"../{nine_slug}/index.html" if depth >= 2 else tool_page_href(nine_slug, "ferramentas")
        rights = enrich.get("nine_rights_params") or []
        rights_lis = "".join(f"<li>{esc(p.get('label', ''))}</li>" for p in rights[:9])
        nine_html = f"""
<div class="tool-nine-rights">
  <h3>9 Certos — Segurança na Medicação</h3>
  <p class="tool-alert-inline" data-tool-nine-alert hidden>Alertas cognitivos ativos — adapte o protocolo de medicação.</p>
  <ol>{rights_lis}</ol>
  <a class="btn-outline" href="{esc(nine_href)}">Abrir checklist completo →</a>
</div>"""

    tags = "".join(f'<span class="tool-hashtag">{esc(t)}</span>' for t in enrich.get("hashtags", []))

    about = f"""
<p>{esc(binding.get("subtitle") or tool.get("name", ""))} — ferramenta clínica catalogada na plataforma 2026.</p>
<p><strong>Tipo:</strong> {esc(tool.get("tool_type", ""))} · <strong>Domínio:</strong> {esc(tool.get("domain", ""))}</p>
<p><strong>Taxonomia:</strong> {esc(tool.get("taxonomy_code", ""))}</p>
<div class="tool-hashtags">{tags}</div>"""

    main_tabs = [
        ("history", "Histórico", True),
        ("formulas", "Fórmulas", bool(formula_text or ref_values_html or band_rows)),
        ("refs", "Referências", True),
        ("resources", "Recursos adicionais", bool(sub_tabs)),
        ("relacionamentos", "Relacionamentos", has_relationships),
        ("simulador", "Simulador", bool(simulator_html)),
        ("about", "Sobre", True),
        ("sae", "SAE", True),
        ("safety", "Segurança", True),
        ("disclaimer", "Aviso legal", True),
    ]
    post_calc_tabs = {"simulador", "sae", "safety"}
    tab_btns = []
    first_tab = True
    for tid, label, visible in main_tabs:
        if not visible:
            continue
        active = " is-active" if first_tab else ""
        post_attr = f' data-tool-post-calc-tab="{esc(tid)}"' if tid in post_calc_tabs else ""
        hidden = " hidden" if tid in post_calc_tabs else ""
        tab_btns.append(
            f'<button type="button" class="tool-info-tab{active}" role="tab" '
            f'data-tool-info-tab="{esc(tid)}"{post_attr}{hidden} '
            f'aria-selected="{str(first_tab).lower()}">{esc(label)}</button>'
        )
        first_tab = False

    first_panel = True
    panels = []

    def panel_open(tid: str, title: str, body: str, *, extra_attrs: str = "", post_calc: bool = False) -> str:
        nonlocal first_panel
        is_first = first_panel and not post_calc
        active = " is-active" if is_first else ""
        hidden_attr = "" if is_first else " hidden"
        if post_calc:
            hidden_attr = " hidden"
        if is_first:
            first_panel = False
        post_attr = f' data-tool-post-calc-tab="{esc(tid)}"' if post_calc else ""
        return (
            f'<section class="tool-info-panel{active}" data-tool-info-panel="{esc(tid)}" '
            f'role="tabpanel"{hidden_attr}{post_attr}{extra_attrs}>'
            f'<h2 class="tool-panel__title">{esc(title)}</h2>{body}</section>'
        )

    panels.append(panel_open("history", "Histórico de cálculos", history_body))
    if formula_text or ref_values_html or band_rows:
        panels.append(panel_open("formulas", "Fórmulas e referência clínica", formulas_body))
    panels.append(panel_open(
        "resources", "Recursos adicionais",
        f'<p class="tool-panel__lead">Conteúdo vinculado a <strong>{esc(tool.get("tool_code", ""))}</strong> na plataforma.</p>{resources_panel}',
        extra_attrs=' data-tool-section-block="resources"',
    ))
    if has_relationships:
        panels.append(panel_open("relacionamentos", "Relacionamentos clínicos", relationships_html))
    if simulator_html:
        panels.append(panel_open("simulador", "Simulador de resultado", simulator_html, post_calc=True))
    panels.append(panel_open("about", "Sobre", about))
    panels.append(panel_open(
        "sae", "Sugestão SAE (NANDA · NIC · NOC)",
        f'<p class="tool-panel__lead" data-tool-sae-hint>Calcule para personalizar sugestões conforme o resultado.</p>'
        f'<div class="tool-sae-grid">'
        f'<div><h3>NANDA-I</h3><ul class="tool-sae-list" data-tool-sae-nanda>{nanda_rows}</ul></div>'
        f'<div><h3>NIC</h3><ul class="tool-sae-list">{nic_rows}</ul></div>'
        f'<div><h3>NOC</h3><ul class="tool-sae-list">{noc_rows}</ul></div></div>',
        post_calc=True,
    ))
    panels.append(panel_open("refs", "Referências bibliográficas", refs_html))
    panels.append(panel_open(
        "safety", "Metas Internacionais de Segurança (IPSG)",
        f'<ul class="tool-ipsg-list">{ipsg_rows}</ul>{nine_html}',
        post_calc=True,
    ))
    panels.append(panel_open("disclaimer", "Aviso legal", disclaimer_body))

    return f"""
<section class="tool-supplementary" aria-labelledby="tool-supplementary-title" data-tool-supplementary>
  <header class="tool-supplementary__head">
    <h2 id="tool-supplementary-title">Informações complementares</h2>
    <p class="tool-supplementary__lead">Gráficos, ações, simulador, SAE e segurança aparecem após o cálculo — SAE e Segurança conforme o resultado clínico.</p>
  </header>
  <nav class="tool-info-tabs" role="tablist" aria-label="Seções complementares">{"".join(tab_btns)}</nav>
  <div class="tool-info-panels">{"".join(panels)}</div>
  <div class="tool-mobile-insights" data-tool-mobile-insights hidden>
    <span class="tool-mobile-insights__label">Após o cálculo:</span>
    <button type="button" class="tool-mobile-insight" data-tool-mobile-jump="charts" hidden>Gráficos</button>
    <button type="button" class="tool-mobile-insight" data-tool-mobile-jump="simulador" hidden>Simulador</button>
    <button type="button" class="tool-mobile-insight" data-tool-mobile-jump="sae" hidden>SAE</button>
    <button type="button" class="tool-mobile-insight" data-tool-mobile-jump="safety" hidden>Segurança</button>
  </div>
</section>"""


def _render_pdf_template(tool: dict, binding: dict, depth: int) -> str:
    logo = image_href(depth, BRAND["logo_header"])
    name = binding.get("display_name") or tool["name"]
    return f"""
<div id="tool-pdf-report" class="pdf-report" hidden aria-hidden="true">
  <header class="pdf-report__header">
    <img src="{esc(logo)}" alt="{esc(SITE_NAME)}" width="140" height="48">
    <div>
      <h1>{esc(name)}</h1>
      <p class="pdf-report__meta">Relatório clínico-educacional · Calculadoras de Enfermagem 2026 · {esc(SITE_NAME)}</p>
      <p class="pdf-report__date" data-pdf-date></p>
    </div>
  </header>
  <section class="pdf-report__section"><h2>Dados informados</h2><div data-pdf-inputs></div></section>
  <section class="pdf-report__section"><h2>Resultado</h2><div data-pdf-result></div></section>
  <section class="pdf-report__section"><h2>Interpretação</h2><div data-pdf-interpretation></div></section>
  <section class="pdf-report__section"><h2>Memória de cálculo</h2><div data-pdf-memory></div></section>
  <section class="pdf-report__section"><h2>Sugestão SAE</h2><div data-pdf-sae></div></section>
  <section class="pdf-report__section"><h2>Referências</h2><div data-pdf-refs></div></section>
  <section class="pdf-report__section"><h2>Metas IPSG</h2><div data-pdf-ipsg></div></section>
  <footer class="pdf-report__footer">
    <p>Ferramenta educativa. Não substitui julgamento clínico. Uso conforme LGPD.</p>
    <p>{esc(SITE_NAME)} — calculadorasdeenfermagem.com</p>
  </footer>
</div>"""


def _severity_class(severity: str) -> str:
    _, templates = _load_registry()
    return templates.get("severity_classes", {}).get(severity, "tool-severity--moderate")


def _related_protocols(tool_code: str, protocols: list[dict], depth: int, slug_map: dict[str, str] | None = None) -> str:
    from protocol_lib import protocol_slug

    related = [p for p in protocols if tool_code in (p.get("related_tool_codes") or [])][:6]
    if not related:
        return ""
    items = []
    for p in related:
        pslug = protocol_slug(p)
        href = route_href(f"/protocolos/{pslug}", depth)
        items.append(
            f'<li><a href="{esc(href)}">{esc(p.get("title", p.get("protocol_code", "")))}</a></li>'
        )
    return f"""
<section class="tool-section tool-relationships" aria-labelledby="tool-proto-title" data-tool-section-block="relationships">
  <h2 id="tool-proto-title">Protocolos relacionados</h2>
  <ul class="tool-link-list">{"".join(items)}</ul>
</section>"""


def _related_diagnoses(definition: dict | None, depth: int) -> str:
    codes = (definition or {}).get("related_diagnosis_codes") or []
    if not codes:
        return ""
    pills = "".join(
        f'<a class="tool-pill" href="{esc(route_href("/nanda", depth))}">{esc(c)}</a>'
        for c in codes[:8]
    )
    return f"""
<section class="tool-section tool-relationships" aria-labelledby="tool-nanda-title" data-tool-section-block="relationships">
  <h2 id="tool-nanda-title">Diagnósticos NANDA-I relacionados</h2>
  <div class="tool-pill-row">{pills}</div>
</section>"""


def _related_tools(tool: dict, tools: list[dict], slug_map: dict[str, str], depth: int) -> str:
    domain = tool.get("domain", "")
    peers = [
        t for t in tools
        if t["tool_code"] != tool["tool_code"] and t.get("domain") == domain
    ][:4]
    if not peers:
        return ""
    items = []
    for t in peers:
        slug = slug_map.get(t["tool_code"], slugify(t.get("acronym", "tool")))
        if depth >= 2:
            href = f"../{slug}/index.html"
        else:
            href = tool_page_href(slug, "ferramentas")
        items.append(
            f'<li><a href="{esc(href)}">'
            f'{esc(t["name"])}</a></li>'
        )
    return f"""
<section class="tool-section tool-relationships" aria-labelledby="tool-peers-title" data-tool-section-block="relationships">
  <h2 id="tool-peers-title">Ferramentas complementares</h2>
  <ul class="tool-link-list">{"".join(items)}</ul>
</section>"""


def _render_mode_tabs(tool: dict, binding: dict) -> str:
    modes = binding.get("modes_visible")
    if not modes and not tool.get("urgency_mode_available"):
        return ""
    if not modes:
        modes = ["CALC_MODE.STANDARD", "CALC_MODE.URGENCY"]
    templates, reg = _load_registry()
    mode_labels = templates.get("modes", reg.get("modes", {}))
    tabs = []
    for i, m in enumerate(modes):
        meta = mode_labels.get(m, {"label": m.replace("CALC_MODE.", "").title()})
        active = " is-active" if i == 0 else ""
        tabs.append(
            f'<button type="button" class="tool-mode-tab{active}" data-tool-mode="{esc(m)}" '
            f'aria-selected="{str(i == 0).lower()}">{esc(meta.get("label", m))}</button>'
        )
    return f'<div class="tool-mode-tabs" role="tablist">{"".join(tabs)}</div>'


_SCALE_OPTIONS: dict | None = None


def _load_scale_options() -> dict:
    global _SCALE_OPTIONS
    if _SCALE_OPTIONS is None:
        path = content_path("calculator_scale_options")
        _SCALE_OPTIONS = load_json(path).get("tools", {}) if path.exists() else {}
    return _SCALE_OPTIONS


def _merge_scale_options(tool_code: str, binding: dict) -> dict:
    """Overlay rich radio_grid options from calculator_scale_options.json."""
    extra = _load_scale_options().get(tool_code, {})
    if not extra:
        return binding
    merged = {**binding, **{k: v for k, v in extra.items() if k != "scale_items"}}
    if extra.get("scale_items"):
        merged["scale_items"] = extra["scale_items"]
    return merged


def _render_safety_blocks(blocks: list[dict]) -> str:
    if not blocks:
        return ""
    items = []
    for b in blocks:
        cls = "tool-safety--hard" if b.get("block_type") == "hard" else "tool-safety--soft"
        detail = f'<p class="tool-safety__detail">{esc(b.get("detail", ""))}</p>' if b.get("detail") else ""
        items.append(
            f'<div class="tool-safety {cls}" role="alert" data-safety-block '
            f'data-field="{esc(b.get("field", ""))}" data-op="{esc(b.get("operator", "eq"))}" '
            f'data-value="{esc(b.get("value", ""))}" hidden>'
            f'<strong>{esc(b.get("message", ""))}</strong>{detail}</div>'
        )
    return f'<div class="tool-safety-list" data-tool-safety-list>{"".join(items)}</div>'


def _render_scale_item(item: dict, index: int) -> str:
    code = item["code"]
    if item.get("type") == "radio_grid" and item.get("options"):
        opts = []
        for o in item["options"]:
            desc = f'<span class="tool-radio-option__desc">{esc(o.get("description", ""))}</span>' if o.get("description") else ""
            opts.append(
                f'<label class="tool-radio-option">'
                f'<input type="radio" name="{esc(code)}" value="{esc(o["value"])}" required '
                f'aria-labelledby="field-{esc(code)}">'
                f'<span class="tool-radio-option__body">'
                f'<span class="tool-radio-option__label">{esc(o["label"])}</span>{desc}'
                f'</span></label>'
            )
        input_html = (
            f'<div class="tool-radio-grid" role="radiogroup" aria-labelledby="field-{esc(code)}">'
            f'{"".join(opts)}</div>'
        )
    elif item.get("type") == "select":
        opts = "".join(
            f'<option value="{esc(o["value"])}">{esc(o["label"])}</option>'
            for o in item.get("options", [])
        )
        input_html = f'<select id="{esc(code)}" name="{esc(code)}" required aria-labelledby="field-{esc(code)}">{opts}</select>'
    elif item.get("min") is not None and item.get("max") is not None:
        input_html = (
            f'<div class="tool-stepper">'
            f'<button type="button" class="tool-stepper__btn" data-step="-1" aria-label="Diminuir">−</button>'
            f'<input id="{esc(code)}" name="{esc(code)}" type="number" '
            f'min="{esc(item["min"])}" max="{esc(item["max"])}" value="{esc(item.get("min", 0))}" '
            f'required aria-labelledby="field-{esc(code)}">'
            f'<button type="button" class="tool-stepper__btn" data-step="1" aria-label="Aumentar">+</button>'
            f'</div>'
        )
    else:
        input_html = f'<input id="{esc(code)}" name="{esc(code)}" type="number" step="any" required aria-labelledby="field-{esc(code)}">'
    tip = item.get("tooltip") or item.get("hint") or ""
    domain = f'<span class="tool-item__domain">{esc(item["domain"])}</span>' if item.get("domain") else ""
    return f"""
<article class="tool-scale-item" data-tool-item="{esc(code)}">
  <div class="tool-scale-item__head">
    <span class="tool-scale-item__num">{index}</span>
    <div>
      <h3 id="field-{esc(code)}">{esc(item["label"])}{_tooltip_icon(tip, item["label"])}</h3>
      {domain}
    </div>
  </div>
  <div class="tool-scale-item__input">{input_html}</div>
</article>"""


def _render_scale_form(definition: dict, binding: dict, tool: dict) -> str:
    binding = _merge_scale_options(tool.get("tool_code", ""), binding)
    items = binding.get("scale_items")
    if not items and definition:
        items = [
            {
                "code": p["code"],
                "label": p.get("label", p["code"]),
                "min": p.get("min"),
                "max": p.get("max"),
                "type": p.get("type", "number"),
            }
            for p in definition.get("parameters", [])
            if p.get("type") not in ("array", "boolean")
        ]
    fields = "".join(_render_scale_item(it, i + 1) for i, it in enumerate(items or []))
    score_max = definition.get("score_max", 30) if definition else 30
    score_min = definition.get("score_min", 0) if definition else 0
    safety_html = _render_safety_blocks(binding.get("safety_blocks", []))
    return f"""
<section class="tool-panel tool-panel--form" aria-labelledby="tool-form-title">
  <h2 id="tool-form-title" class="tool-panel__title">Dados clínicos</h2>
  {safety_html}
  <form class="tool-form" data-tool-form data-calc-type="sum_score">
    <div class="tool-scale-list">{fields}</div>
    <div class="tool-form__actions">
      <button type="button" class="btn-outline tool-btn-clear" data-tool-clear>Limpar</button>
      <button type="submit" class="btn tool-btn-calc">Calcular</button>
    </div>
  </form>
</section>
<section class="tool-panel tool-panel--result" aria-labelledby="tool-result-title">
  <h2 id="tool-result-title" class="tool-panel__title">Resultado</h2>
  <div class="tool-result-card tool-severity--low" data-tool-result-card>
    <div class="tool-result-card__score">
      <span class="tool-result-card__value" data-tool-score>—</span>
      <span class="tool-result-card__max">/ {esc(score_max)}</span>
    </div>
    <p class="tool-result-card__label" data-tool-label>Aguardando cálculo</p>
    <p class="tool-result-card__action" data-tool-action></p>
  </div>
  <div class="tool-progress" data-tool-progress hidden>
    <h3>Progresso por domínio</h3>
    <div class="tool-progress__bars" data-tool-progress-bars></div>
  </div>
</section>"""


def _render_field_input(field: dict) -> str:
    code = field["code"]
    ftype = field.get("type", "number")
    if ftype == "select":
        opts = "".join(
            f'<option value="{esc(o["value"])}">{esc(o["label"])}</option>'
            for o in field.get("options", [])
        )
        return f"""
<label class="tool-field" for="{esc(code)}">
  <span class="tool-field__label">{esc(field["label"])}{_tooltip_icon(field.get("hint", ""), field["label"])}</span>
  {f'<span class="tool-field__hint">{esc(field["hint"])}</span>' if field.get("hint") else ""}
  <select id="{esc(code)}" name="{esc(code)}" required>{opts}</select>
</label>"""
    step = f' step="{esc(field["step"])}"' if field.get("step") else ""
    min_a = f' min="{esc(field["min"])}"' if field.get("min") is not None else ""
    return f"""
<label class="tool-field" for="{esc(code)}">
  <span class="tool-field__label">{esc(field["label"])}{_tooltip_icon(field.get("hint", ""), field["label"])}</span>
  {f'<span class="tool-field__hint">{esc(field["hint"])}</span>' if field.get("hint") and not field.get("hint_in_tooltip") else ""}
  <input id="{esc(code)}" name="{esc(code)}" type="number"{min_a}{step} required>
</label>"""


def _render_calculator_form(definition: dict, binding: dict, tool: dict) -> str:
    fields_src = binding.get("fields")
    if not fields_src and definition:
        fields_src = definition.get("parameters", [])
    fields = "".join(_render_field_input(f) for f in fields_src or [])
    formula = definition.get("formula", "") if definition else ""
    calc_engine = binding.get("calc_engine", "formula")
    calc_type = definition.get("calculation_type", "formula") if definition else "formula"

    presets = ""
    for preset in binding.get("quick_presets", []):
        preset_json = json.dumps(preset["values"], ensure_ascii=False).replace("&", "&amp;").replace('"', "&quot;")
        presets += (
            f'<button type="button" class="tool-preset" data-tool-preset="{preset_json}">'
            f'{esc(preset["label"])}</button>'
        )
    presets_html = f'<div class="tool-presets">{presets}</div>' if presets else ""

    ref_rows = ""
    for rv in binding.get("reference_values", []):
        ref_rows += f'<tr><th>{esc(rv["label"])}</th><td>{esc(rv["value"])}</td></tr>'
    ref_table = ""
    if ref_rows:
        ref_table = f"""
<section class="tool-section tool-section--refs">
  <h2>Valores de referência</h2>
  <table class="tool-ref-table"><tbody>{ref_rows}</tbody></table>
</section>"""

    bands = definition.get("interpretation_bands", []) if definition else []
    band_rows = "".join(
        f'<tr class="{_severity_class(b.get("severity", "low"))}">'
        f'<td>{esc(b.get("min", ""))}–{esc(b.get("max", ""))}</td>'
        f'<td>{esc(b.get("label_pt", ""))}</td>'
        f'<td>{esc(b.get("action_pt", ""))}</td></tr>'
        for b in bands
    )
    interp_table = ""
    if band_rows and binding.get("show_classification_scale"):
        interp_table = f"""
<section class="tool-section">
  <h2>Classificação</h2>
  <div class="tool-class-scale" data-tool-class-scale role="img" aria-label="Escala de classificação"></div>
  <table class="tool-interp-table"><thead><tr><th>Faixa</th><th>Classificação</th><th>Ação</th></tr></thead>
  <tbody>{band_rows}</tbody></table>
</section>"""
    elif band_rows:
        interp_table = f"""
<section class="tool-section">
  <h2>Interpretação</h2>
  <table class="tool-interp-table"><thead><tr><th>Faixa</th><th>Classificação</th><th>Ação</th></tr></thead>
  <tbody>{band_rows}</tbody></table>
</section>"""

    return f"""
<section class="tool-panel tool-panel--form" aria-labelledby="tool-form-title">
  <h2 id="tool-form-title" class="tool-panel__title">Dados para cálculo</h2>
  <form class="tool-form" data-tool-form data-calc-type="{esc(calc_type)}" data-calc-engine="{esc(calc_engine)}">
    {fields}
    <div class="tool-form__actions">
      <button type="button" class="btn-outline tool-btn-clear" data-tool-clear>Limpar tudo</button>
      <button type="submit" class="btn tool-btn-calc">Calcular</button>
    </div>
  </form>
  {presets_html}
</section>
<section class="tool-panel tool-panel--result" aria-labelledby="tool-result-title">
  <h2 id="tool-result-title" class="tool-panel__title">Resultado</h2>
  <div class="tool-result-card tool-severity--low" data-tool-result-card>
    <div class="tool-result-card__score">
      <span class="tool-result-card__value" data-tool-score>—</span>
      <span class="tool-result-card__unit" data-tool-unit></span>
    </div>
    <p class="tool-result-card__label" data-tool-label>Preencha os campos e calcule</p>
    <p class="tool-result-card__action" data-tool-action></p>
  </div>
  <details class="tool-formula-block tool-formula-block--inline" data-tool-inline-formula data-tool-section-block="formulas-inline" open>
    <summary>Fórmula utilizada</summary>
    <code class="tool-formula">{esc(formula)}</code>
  </details>
</section>
{ref_table.replace('class="tool-section tool-section--refs"', 'class="tool-section tool-section--refs tool-section--inline" data-tool-section-block="refs-inline"') if ref_table else ""}
{interp_table.replace('<section class="tool-section">', '<section class="tool-section tool-section--inline" data-tool-section-block="interp-inline">') if interp_table else ""}"""


def _render_checklist(definition: dict, binding: dict) -> str:
    params = definition.get("parameters", []) if definition else []
    items = []
    for i, p in enumerate(params, 1):
        items.append(f"""
<label class="tool-check-item">
  <input type="checkbox" name="{esc(p["code"])}" value="1">
  <span class="tool-check-item__num">{i}</span>
  <span class="tool-check-item__label">{esc(p.get("label", p["code"]))}</span>
</label>""")
    grid_class = binding.get("checklist_layout", "grid-3")
    alert = ""
    if binding.get("conditional_alerts"):
        alert = """
<div class="tool-alert-banner" data-tool-conditional-alert hidden>
  <strong>Alertas ativos</strong>
  <p>Adaptações obrigatórias no protocolo de medicação conforme escore cognitivo.</p>
</div>"""
    return f"""
{alert}
<section class="tool-panel tool-panel--form tool-panel--full" aria-labelledby="tool-form-title">
  <h2 id="tool-form-title" class="tool-panel__title">Checklist de verificação</h2>
  <form class="tool-form" data-tool-form data-calc-type="checklist">
    <div class="tool-check-grid tool-check-grid--{esc(grid_class.replace("grid-", ""))}">{"".join(items)}</div>
    <div class="tool-form__actions">
      <button type="submit" class="btn tool-btn-calc">Validar checklist</button>
    </div>
  </form>
</section>
<section class="tool-panel tool-panel--result" aria-labelledby="tool-result-title">
  <h2 id="tool-result-title" class="tool-panel__title">Status</h2>
  <div class="tool-result-card tool-severity--low" data-tool-result-card>
    <p class="tool-result-card__label" data-tool-label>Marque todos os itens obrigatórios</p>
    <p class="tool-result-card__action" data-tool-action></p>
  </div>
</section>"""


def _render_sidebar(binding: dict, tool_name: str) -> str:
    """Brand-only sidebar — navigation moved to header dropdown (desktop) / smart nav (mobile)."""
    return f"""
<aside class="tool-sidebar" aria-label="Identificação da ferramenta">
  <div class="tool-sidebar__brand">
    <span class="tool-sidebar__icon" aria-hidden="true">♥</span>
    <div>
      <strong>{esc(tool_name)}</strong>
      <span>Ferramenta clínica</span>
    </div>
  </div>
</aside>"""


def _render_ref_values_table(binding: dict) -> str:
    rows = "".join(
        f'<tr><th>{esc(rv["label"])}</th><td>{esc(rv["value"])}</td></tr>'
        for rv in binding.get("reference_values", [])
    )
    if not rows:
        return ""
    return f"""
<table class="tool-ref-table"><tbody>{rows}</tbody></table>"""


def _render_tool_nav_menu(*, has_relationships: bool, has_resources: bool) -> str:
    items = [
        ("history", "Histórico"),
        ("formulas", "Fórmulas"),
        ("refs", "Referências"),
    ]
    if has_resources:
        items.append(("resources", "Recursos"))
    if has_relationships:
        items.append(("relacionamentos", "Relacionamentos"))
    items.extend([
        ("about", "Sobre"),
        ("disclaimer", "Aviso legal"),
    ])
    lis = "".join(
        f'<li role="none"><button type="button" role="menuitem" class="tool-nav-dropdown__item" '
        f'data-tool-nav="{esc(nav_id)}">{esc(label)}</button></li>'
        for nav_id, label in items
    )
    return f"""
<div class="tool-nav-dropdown" data-tool-nav-dropdown>
  <button type="button" class="tool-nav-dropdown__toggle btn-outline" aria-expanded="false" aria-haspopup="menu">
    Conteúdo <span aria-hidden="true">▾</span>
  </button>
  <ul class="tool-nav-dropdown__menu" role="menu" hidden>{lis}</ul>
</div>"""


def _render_tool_smart_nav(*, has_relationships: bool, has_resources: bool) -> str:
    items = [
        ("history", "Histórico", "clock"),
        ("formulas", "Fórmulas", "formula"),
        ("refs", "Refs", "book"),
    ]
    if has_resources:
        items.append(("resources", "Recursos", "plus"))
    if has_relationships:
        items.append(("relacionamentos", "Relacionar", "link"))
    items.append(("about", "Sobre", "info"))
    btns = "".join(
        f'<button type="button" class="tool-smart-nav__btn" data-tool-nav="{esc(nav_id)}" '
        f'data-tool-smart-icon="{esc(icon)}">{esc(label)}</button>'
        for nav_id, label, icon in items
    )
    return f'<nav class="tool-smart-nav" aria-label="Acesso rápido à ferramenta">{btns}</nav>'


def _render_tool_body(
    tool: dict,
    definition: dict | None,
    binding: dict,
    template_code: str,
    *,
    depth: int,
    protocols: list[dict],
    tools: list[dict],
    slug_map: dict[str, str],
) -> str:
    binding = _merge_scale_options(tool.get("tool_code", ""), binding)
    theme = binding.get("theme", "scale")
    use_sidebar = binding.get("sidebar") or template_code == "TPL.TOOL_SIDEBAR"

    if template_code == "TPL.CHECKLIST":
        grid = _render_checklist(definition, binding)
    elif template_code in ("TPL.SCALE_FORM", "TPL.RISK_SCORE"):
        grid = _render_scale_form(definition, binding, tool)
    elif template_code in ("TPL.CALCULATOR", "TPL.ANTHROPOMETRIC", "TPL.TOOL_SIDEBAR"):
        grid = _render_calculator_form(definition, binding, tool)
    elif template_code == "TPL.DASHBOARD":
        grid = f"""
<section class="tool-panel tool-panel--full">
  <div class="tool-planned card">
    <h2>Painel analítico</h2>
    <p>Template <strong>{esc(template_code)}</strong> — KPIs, gráficos e relatórios (fase Dashboard).</p>
    <p>Use o formulário padrão enquanto o painel completo é implementado.</p>
  </div>
</section>"""
        grid += _render_calculator_form(definition, binding, tool)
    else:
        grid = _render_calculator_form(definition, binding, tool)

    mode_tabs = _render_mode_tabs(tool, binding)
    sidebar = _render_sidebar(binding, binding.get("display_name") or tool["name"]) if use_sidebar else ""

    config_obj = {
        "tool_code": tool.get("tool_code"),
        "calculation_type": (definition or {}).get("calculation_type"),
        "calc_engine": binding.get("calc_engine"),
        "score_min": (definition or {}).get("score_min"),
        "score_max": (definition or {}).get("score_max"),
        "bands": definition.get("interpretation_bands", []) if definition else [],
        "scale_items": binding.get("scale_items", []),
        "safety_blocks": binding.get("safety_blocks", []),
    }
    config_script = (
        f'<script type="application/json" id="tool-config">{json.dumps(config_obj, ensure_ascii=False)}</script>'
    )

    charts = _resolve_charts(binding, definition)
    charts_html = _render_charts_panel(charts)
    enrich = get_tool_enrichment(tool, definition)
    customize_html = _render_user_customization(depth)
    actions_html = _render_action_bar(binding.get("display_name") or tool["name"])
    pdf_html = _render_pdf_template(tool, binding, depth)

    relationships_html, has_relationships = _render_relationships_panel(
        tool, definition, protocols, tools, slug_map, depth,
    )
    simulator_html = _render_simulator_panel(definition, binding)

    enrich = get_tool_enrichment(tool, definition)
    res = enrich["resources"]
    has_resources = bool(res.get("quizzes") or res.get("flashcards") or res.get("paths"))

    nav_menu_html = _render_tool_nav_menu(
        has_relationships=has_relationships, has_resources=has_resources,
    )
    smart_nav_html = _render_tool_smart_nav(
        has_relationships=has_relationships, has_resources=has_resources,
    )

    calc_zone = f'<div class="tool-calc-zone"><div class="tool-grid tool-grid--split">{grid}</div></div>'

    tabs_html = _render_tool_page_tabs(
        tool, definition, binding, enrich,
        depth=depth, slug_map=slug_map,
        relationships_html=relationships_html,
        has_relationships=has_relationships,
        simulator_html=simulator_html,
    )

    shell_class = "tool-shell tool-shell--sidebar" if use_sidebar else "tool-shell"
    voice_btn = (
        '<button type="button" class="tool-voice-btn" data-tool-voice '
        'aria-label="Comando por voz" title="Comando por voz">🎤 Voz</button>'
    )
    return f"""
<div class="{shell_class}" data-tool-theme="{esc(theme)}" data-tool-template="{esc(template_code)}">
  {sidebar}
  <div class="tool-workspace">
    <header class="tool-header">
      <div class="tool-header__text">
        <p class="tool-header__breadcrumb">{esc(tool.get("acronym", ""))} · {esc(tool.get("domain", ""))}</p>
        <h1>{esc(binding.get("display_name") or tool["name"])}</h1>
        <p class="tool-header__subtitle">{esc(binding.get("subtitle") or tool.get("category", ""))}</p>
      </div>
      <div class="tool-header__meta">
        {nav_menu_html}
        {voice_btn}
        {f'<span class="tool-badge">Evidência {esc(definition.get("evidence_level", "B"))}</span>' if definition and definition.get("evidence_level") else ""}
        <span class="tool-badge tool-badge--muted">CE 2026</span>
      </div>
    </header>
    {smart_nav_html}
    {customize_html}
    {mode_tabs}
    {actions_html}
    {config_script}
    {calc_zone}
    {charts_html}
    <details class="tool-calc-memory" data-tool-section-block="memory" data-tool-post-calc="memory" hidden>
      <summary>Memória de cálculo / avaliação</summary>
      <div class="tool-calc-memory__body" data-tool-memory aria-live="polite"></div>
    </details>
    {tabs_html}
    <footer class="tool-disclaimer" data-tool-disclaimer>
      <p>Ferramenta educativa baseada em evidências. Os resultados são auxiliares e não substituem o julgamento clínico do profissional.</p>
    </footer>
    {pdf_html}
  </div>
</div>"""


def render_tool_page(
    tool: dict,
    definition: dict | None,
    *,
    depth: int,
    path_slug: str,
    slug_map: dict[str, str] | None = None,
    tools: list[dict] | None = None,
    protocols: list[dict] | None = None,
) -> str:
    slug_map = slug_map or {}
    tools = tools or []
    protocols = protocols or []

    template_code, binding = resolve_template(tool, definition)
    acronym = tool.get("acronym") or tool["tool_code"].replace("TOOL.", "")
    display_name = binding.get("display_name") or tool["name"]

    crumbs = [
        ("Ferramentas", "../index.html" if depth >= 2 else "index.html"),
        (display_name, None),
    ]

    body = f"""
<div class="section-container tool-page-top">
  {render_breadcrumbs(crumbs, depth)}
</div>
{_render_tool_body(tool, definition, binding, template_code, depth=depth, protocols=protocols, tools=tools, slug_map=slug_map)}"""

    display_name = binding.get("display_name") or tool["name"]
    seo_title = f"{display_name} ({acronym}) | {SITE_NAME}"
    desc = (
        f"Ferramenta clínica {display_name} — Calculadoras de Enfermagem 2026. "
        f"Template {template_code.replace('TPL.', '')}."
    )
    prefix = rel_prefix(depth)
    return render_document(
        depth=depth,
        title=seo_title,
        description=desc,
        canonical_path=f"/ferramentas/{path_slug}",
        main_html=body,
        extra_css=[f"{prefix}assets/css/tools.css"],
        main_class="site-main tool-main",
    )
