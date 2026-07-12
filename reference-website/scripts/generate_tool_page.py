#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_tool_page.py — Gera uma página de calculadora/escala completa
(HTML estático, texto "assado" para SEO) a partir de um JSON no formato
tool.schema.json.

Uso:
    python3 generate_tool_page.py data/tools/escala-de-braden.json > braden.html

Reaproveita literalmente as mesmas classes CSS do calculadora-template.html
(.tpl-*/.tool-*/.calc-*/.est-*/.urg-*/.aca-*/.kpi-*/.audit-*/.about-*/.faq-*)
e o mesmo shell modular (site-header/site-a11y/site-footer/site-cookie +
js/partials-loader.js). A parte interativa (recalcular ao mudar um campo)
é feita por js/calc-engine.js, que lê o bloco <script id="tool-config">
embutido nesta página.
"""
import json
import sys
import html as htmlmod


def esc(s):
    if s is None:
        return ""
    return htmlmod.escape(str(s), quote=True)


def nl2br_p(text):
    """Converte um bloco de texto com \n em parágrafos <p>."""
    if not text:
        return ""
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    return "".join("<p>" + esc(p) + "</p>" for p in parts)


def default_state(inputs):
    state = {}
    for inp in inputs:
        if "defaultValue" in inp and inp["defaultValue"] is not None:
            state[inp["id"]] = inp["defaultValue"]
        elif inp.get("options"):
            state[inp["id"]] = inp["options"][0]["value"]
        elif inp.get("optional"):
            state[inp["id"]] = ""
        else:
            state[inp["id"]] = 0
    return state


def score_of(inp, value):
    if inp["type"] == "select":
        for o in inp.get("options", []):
            if o["value"] == value:
                return o["score"]
        return 0
    return value


def _read_gasometria_val(inputs, state, field_id):
    inp = next((i for i in inputs if i["id"] == field_id), None)
    raw = state.get(field_id)
    if inp and inp.get("optional") and raw in ("", None):
        return float("nan")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return float("nan")


def _interpret_gasometria_severity(cfg, state):
    inputs = cfg["calculator"]["inputs"]
    ph = _read_gasometria_val(inputs, state, "ph")
    paco2 = _read_gasometria_val(inputs, state, "paco2")
    hco3 = _read_gasometria_val(inputs, state, "hco3")
    if ph != ph or paco2 != paco2 or hco3 != hco3:
        return -1
    severity = 0
    if ph < 7.35:
        diagnostico = "ACIDOSE"
    elif ph > 7.45:
        diagnostico = "ALCALOSE"
    else:
        diagnostico = "NORMAL / COMPENSADA"
    if diagnostico != "NORMAL / COMPENSADA":
        is_resp = (ph < 7.35 and paco2 > 45) or (ph > 7.45 and paco2 < 35)
        is_metab = (ph < 7.35 and hco3 < 22) or (ph > 7.45 and hco3 > 26)
        if is_resp and not is_metab:
            severity = 20 if ((ph < 7.35 and hco3 > 26) or (ph > 7.45 and hco3 < 22)) else 30
        elif is_metab and not is_resp:
            severity = 20 if ((ph < 7.35 and paco2 < 35) or (ph > 7.45 and paco2 > 45)) else 30
        elif is_resp and is_metab:
            severity = 40
        else:
            severity = 30
    elif paco2 != 40 and hco3 != 24:
        severity = 10
    return severity


def compute_total(cfg, state):
    formula = cfg["calculator"]["formula"]
    inputs = cfg["calculator"]["inputs"]
    if formula["type"] == "sum":
        return sum(score_of(inp, state[inp["id"]]) for inp in inputs)
    if formula["type"] == "expression":
        expr = formula["expression"]
        scope = {inp["id"]: float(state[inp["id"]]) for inp in inputs}
        return eval(expr, {"__builtins__": {}}, scope)
    if formula["type"] == "gasometria":
        return _interpret_gasometria_severity(cfg, state)
    return 0


def find_range(cfg, total):
    for r in cfg.get("interpretation", {}).get("ranges", []):
        if r["min"] <= total <= r["max"]:
            return r
    return None


def fmt(cfg, n):
    dec = cfg["calculator"]["formula"].get("decimals", 0)
    return f"{n:.{dec}f}" if dec else str(round(n))


RISK_WARN = {"high", "critical"}


def option_label(o, formula_type):
    if formula_type == "sum":
        return f'{o["score"]} — {esc(o["label"])}'
    return esc(o["label"])


def render_field_row(inp, state, formula_type="sum"):
    if inp["type"] == "select":
        opts = "".join(
            '<option value="{v}"{sel}>{label}</option>'.format(
                v=esc(o["value"]), sel=" selected" if o["value"] == state[inp["id"]] else "",
                label=option_label(o, formula_type)
            ) for o in inp.get("options", [])
        )
        hint = f'<p class="field-hint">{esc(inp.get("description",""))}</p>' if inp.get("description") else ""
        return f'''
            <div class="field-row">
              <div class="field-top">
                <label class="field-label" for="calc-{esc(inp['id'])}">{esc(inp['label'])}</label>
              </div>
              <div class="field-select-wrap">
                <select id="calc-{esc(inp['id'])}" class="field-select" data-calc-input="{esc(inp['id'])}">{opts}</select>
                <svg class="icon"><use href="#i-arrow"/></svg>
              </div>
              {hint}
            </div>'''
    else:
        unit = inp.get("unit", "")
        val = state[inp["id"]]
        val_attr = "" if val in ("", None) else esc(val)
        optional_hint = (
            f'<p class="field-hint">{esc(inp.get("description",""))} (opcional)</p>'
            if inp.get("optional") and inp.get("description")
            else (f'<p class="field-hint">Opcional</p>' if inp.get("optional") else "")
        )
        return f'''
            <div class="field-row">
              <div class="field-top">
                <label class="field-label" for="calc-{esc(inp['id'])}">{esc(inp['label'])}</label>
                <span class="field-unit">{esc(unit)}</span>
              </div>
              <div class="field-input-wrap">
                <input type="number" inputmode="decimal" id="calc-{esc(inp['id'])}" class="field-input"
                       data-calc-input="{esc(inp['id'])}" value="{val_attr}"
                       min="{esc(inp.get('min',''))}" max="{esc(inp.get('max',''))}" step="{esc(inp.get('step',1))}">
                <span class="field-suffix">{esc(unit)}</span>
              </div>
              {optional_hint}
            </div>'''


def render_formula_strip(inputs, formula, state):
    cells = []
    for inp in inputs:
        val = score_of(inp, state[inp["id"]]) if formula["type"] == "sum" else state[inp["id"]]
        cells.append(f'''<div class="formula-cell">
              <div class="formula-box" data-formula-box="{esc(inp['id'])}">{esc(val)}</div>
              <span class="formula-cap">{esc(inp['label'])}</span>
            </div>''')
    op = "+" if formula["type"] == "sum" else "="
    joined = f' <span class="formula-op">{op}</span> '.join(cells)
    return joined


def build(cfg):
    ov = cfg["overview"]
    calc = cfg["calculator"]
    inputs = calc["inputs"]
    formula = calc["formula"]
    seo = cfg.get("seo", {})
    breadcrumb = cfg.get("breadcrumb", {})
    evidence = cfg.get("evidence", {})
    sae = cfg.get("sae", {})
    learning = cfg.get("learning", {})
    faq = cfg.get("faq", [])
    about = cfg.get("about", {})

    state = default_state(inputs)
    total = compute_total(cfg, state)
    rng = find_range(cfg, total)
    total_str = fmt(cfg, total)
    warn = rng and rng.get("riskLevel") in RISK_WARN
    result_unit = formula.get("resultUnit", "")

    fields_html = "".join(render_field_row(inp, state, formula["type"]) for inp in inputs)
    formula_cells = render_formula_strip(inputs, formula, state)

    step_cards = []
    for i, inp in enumerate(inputs, 1):
        if inp["type"] == "select":
            opts = "".join(
                '<option value="{v}"{sel}>{label}</option>'.format(
                    v=esc(o["value"]), sel=" selected" if o["value"] == state[inp["id"]] else "",
                    label=option_label(o, formula["type"])
                ) for o in inp.get("options", [])
            )
            control = f'''<div class="field-select-wrap" style="flex:1;min-width:220px;">
                <select class="field-select" data-calc-input="{esc(inp['id'])}">{opts}</select>
                <svg class="icon"><use href="#i-arrow"/></svg>
              </div>'''
        else:
            control = f'''<div class="big-input-wrap">
                <input type="number" class="big-input" data-calc-input="{esc(inp['id'])}" value="{esc(state[inp['id']])}">
                <span class="big-input-suffix">{esc(inp.get('unit',''))}</span>
              </div>'''
        step_cards.append(f'''
            <section class="calc-card">
              <div class="step-card">
                <div class="step-num">{i}</div>
                <div class="step-body">
                  <h3>{esc(inp['label'])}</h3>
                  <p class="step-hint">{esc(inp.get('description',''))}</p>
                  <div class="step-content">{control}</div>
                </div>
              </div>
            </section>''')
    step_cards_html = "".join(step_cards)

    fd_steps = []
    for i, inp in enumerate(inputs, 1):
        val = score_of(inp, state[inp["id"]]) if formula["type"] == "sum" else state[inp["id"]]
        fd_steps.append(f'''<div class="fd-step">
              <div class="fd-step-num">{i}</div>
              <div class="fd-step-label"><div class="l1">{esc(inp['label'])}</div></div>
              <div class="fd-step-value" data-fd-step="{esc(inp['id'])}">{esc(val)}</div>
            </div>''')
    fd_steps_html = "".join(fd_steps)

    examples_html = ""
    for ex in learning.get("examples", []):
        values_json = esc(json.dumps(ex.get("values", {})))
        examples_html += f'''<button type="button" class="example-btn" data-example data-values='{values_json}'>
              <div class="ex-emoji">{esc(ex.get("emoji","📋"))}</div>
              <div class="ex-label">{esc(ex.get("label",""))}</div>
              <div class="ex-desc">{esc(ex.get("sublabel",""))}</div>
            </button>'''

    glossary_items = learning.get("glossary")
    if not glossary_items:
        glossary_items = []
        for inp in inputs:
            if inp.get("description"):
                glossary_items.append({"term": inp["label"], "def": inp["description"]})
    glossary_html = "".join(
        f'''<li><span class="glossary-dot"></span><div><div class="glossary-term">{esc(g['term'])}</div><div class="glossary-def">{esc(g['def'])}</div></div></li>'''
        for g in glossary_items
    )

    has_quiz = bool(learning.get("quiz"))

    urg_presets_html = ""
    for ex in learning.get("examples", [])[:6]:
        values_json = esc(json.dumps(ex.get("values", {})))
        urg_presets_html += f'''<button type="button" class="urg-preset" data-example data-values='{values_json}'>{esc(ex.get("label",""))} <span class="p-sub">{esc(ex.get("sublabel",""))}</span></button>'''

    urg_fields_html = ""
    for inp in inputs:
        if inp["type"] == "select":
            opts = "".join(
                '<option value="{v}"{sel}>{label}</option>'.format(
                    v=esc(o["value"]), sel=" selected" if o["value"] == state[inp["id"]] else "", label=esc(o["label"])
                ) for o in inp.get("options", [])
            )
            urg_fields_html += f'''<div class="urg-field"><label>{esc(inp['label'])}</label>
              <select class="field-select" data-calc-input="{esc(inp['id'])}" style="background:rgba(255,255,255,.07);color:#fff;border-color:rgba(255,255,255,.16);">{opts}</select></div>'''
        else:
            urg_fields_html += f'''<div class="urg-field"><label>{esc(inp['label'])}</label>
              <input type="number" data-calc-input="{esc(inp['id'])}" value="{esc(state[inp['id']])}"></div>'''

    aca_dados = " · ".join(
        f'{esc(inp["label"])}: <strong data-aca-value="{esc(inp["id"])}">{esc(state[inp["id"]])}</strong>'
        for inp in inputs
    )

    sae_html = ""
    if sae.get("nanda") or sae.get("noc") or sae.get("nic"):
        for n in sae.get("nanda", []):
            sae_html += f'<h4>NANDA — {esc(n["diagnosis"])}</h4><p>{esc(n.get("definition",""))}</p>'
        for n in sae.get("noc", []):
            inds = "".join(f"<li>{esc(i)}</li>" for i in n.get("indicators", []))
            sae_html += f'<h4>NOC — {esc(n["outcome"])}</h4><ul class="tips-list">{inds}</ul>'
        for n in sae.get("nic", []):
            acts = "".join(f"<li>{esc(a)}</li>" for a in n.get("activities", []))
            sae_html += f'<h4>NIC — {esc(n["intervention"])}</h4><ul class="tips-list">{acts}</ul>'

    evid_html = ""
    if evidence.get("foundation"):
        evid_html += f'<h4>Fundamentação</h4>{nl2br_p(evidence["foundation"])}'
    if evidence.get("history"):
        evid_html += f'<h4>Histórico</h4>{nl2br_p(evidence["history"])}'
    valid_html = ""
    if evidence.get("validation"):
        valid_html += f'<h4>Validação científica</h4>{nl2br_p(evidence["validation"])}'
    if evidence.get("sensitivity") is not None:
        valid_html += f'<p>Sensibilidade: <strong>{round(evidence["sensitivity"]*100)}%</strong> · Especificidade: <strong>{round(evidence.get("specificity",0)*100)}%</strong></p>'
    if evidence.get("limitations"):
        valid_html += f'<h4>Limitações</h4>{nl2br_p(evidence["limitations"])}'

    refs_html = "".join(
        f'<li><span class="ref-num">{i+1}</span>{esc(r["text"])}</li>'
        for i, r in enumerate(evidence.get("references", []))
    )

    ranges_html = ""
    for r in cfg.get("interpretation", {}).get("ranges", []):
        ranges_html += f'''<li><span class="glossary-dot" style="background:{esc(r.get("color","#999"))}"></span>
          <div><div class="glossary-term">{r['min']}–{r['max']}: {esc(r['label'])}</div></div></li>'''

    tips_html = "".join(f'<li><svg class="icon"><use href="#i-clipcheck"/></svg> {esc(t)}</li>' for t in learning.get("tips", []))

    faq_html = ""
    for f in faq:
        faq_html += f'''<div class="faq-item"><details>
              <summary>{esc(f['q'])} <svg class="icon"><use href="#i-arrow"/></svg></summary>
              <p>{esc(f['a'])}</p>
            </details></div>'''

    gestor_dist_html = ""
    rlist = cfg.get("interpretation", {}).get("ranges", [])
    if rlist:
        n = len(rlist)
        raw_weights = list(range(n, 0, -1))
        s = sum(raw_weights)
        for i, (r, w) in enumerate(zip(rlist, raw_weights)):
            pct = round(w * 100 / s)
            gestor_dist_html += f'''<div class="dist-row"><span class="dist-label">{esc(r['label'])}</span>
              <div class="dist-bar-wrap"><div class="dist-bar" style="width:{pct}%; background:{esc(r.get('color','#0f9d74'))};"></div></div>
              <span class="dist-pct">{pct}%</span></div>'''

    has_sae = bool(sae.get("nanda") or sae.get("noc") or sae.get("nic"))
    sae_tab_btn = '<button class="tab" data-tab="sae" type="button">SAE</button>' if has_sae else ""
    sae_tab_panel = f'<div class="tab-panel" data-tab-panel="sae">{sae_html}</div>' if has_sae else ""

    rating = ov.get("rating", 4.8)
    rating_count = ov.get("ratingCount", 0)
    full_stars = round(rating)
    stars_html = "".join(
        f'<button type="button" class="{"on" if i < full_stars else ""}" tabindex="-1" aria-hidden="true"><svg class="icon icon-sm"><use href="#i-star"/></svg></button>'
        for i in range(5)
    )

    tool_config_json = json.dumps(cfg, ensure_ascii=False)

    page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{esc(seo.get('title', ov['name']))} | Calculadoras de Enfermagem</title>
<meta name="description" content="{esc(seo.get('description', ov.get('objective','')))}">
<link rel="canonical" href="{esc(seo.get('canonical',''))}" />

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/main.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />
<link rel="stylesheet" href="css/site-styles.css">
<link rel="stylesheet" href="css/calc-tool.css">
</head>
<body data-page="{esc(cfg['slug'])}">
<a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>
<div id="statusMessage" class="sr-only" aria-live="polite" aria-atomic="true"></div>

<div id="site-header"></div>
<div id="site-a11y"></div>

<main id="main-content">
  <div class="container">

    <nav class="tpl-breadcrumb" aria-label="Breadcrumb">
      <a href="index.html">Início</a>
      <svg class="sep"><use href="#i-arrow"/></svg>
      <a href="{esc(breadcrumb.get('categoryHref','index.html#calculadoras'))}">Ferramentas</a>
      <svg class="sep"><use href="#i-arrow"/></svg>
      <a href="{esc(breadcrumb.get('categoryHref','index.html#calculadoras'))}">{esc(breadcrumb.get('category',''))}</a>
      <svg class="sep"><use href="#i-arrow"/></svg>
      <span class="current" aria-current="page">{esc(ov['name'])}</span>
    </nav>

    <div class="tool-header">
      <div class="tool-header-main">
        <div class="tool-icon-badge" aria-hidden="true">
          <svg class="icon"><use href="#{esc(ov.get('icon','i-calculator'))}"/></svg>
        </div>
        <div>
          <span class="tool-category-badge">{esc(ov.get('categoryBadge',''))}</span>
          <h1>{esc(ov['name'])}</h1>
          <p class="tool-subtitle">{esc(ov.get('objective',''))}</p>
          <div class="tool-rating" aria-label="Avaliação desta calculadora">
            <div class="stars" role="img" aria-label="{rating} de 5 estrelas">{stars_html}</div>
            <span>{rating} · {rating_count} avaliações</span>
          </div>
        </div>
      </div>
      <div class="tool-actions">
        <button type="button" class="btn-icon" id="calcFavoriteBtn" aria-pressed="false">
          <svg class="icon"><use href="#i-bookmark"/></svg> Favoritar
        </button>
        <button type="button" class="btn-icon" id="calcShareBtn">
          <svg class="icon"><use href="#i-share"/></svg> Compartilhar
        </button>
        <button type="button" class="btn-icon" id="calcPrintBtn" onclick="window.print()">
          <svg class="icon"><use href="#i-printer"/></svg> Imprimir
        </button>
      </div>
    </div>

    <div class="profile-tabs-bar">
      <div class="tabs-inner" data-tab-group="perfil" role="tablist" aria-label="Perfil de visualização">
        <button class="tab active" data-tab="padrao" type="button" role="tab" aria-selected="true"><svg class="icon icon-sm"><use href="#i-person"/></svg> Padrão</button>
        <button class="tab" data-tab="estudante" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-cap"/></svg> Estudante</button>
        <button class="tab" data-tab="urgencia" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-bolt"/></svg> Modo Urgência</button>
        <button class="tab" data-tab="academico" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-book"/></svg> Acadêmico</button>
        <button class="tab" data-tab="gestor" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-trend"/></svg> Gestor</button>
      </div>
    </div>

    <div data-tab-panels="perfil">

      <!-- ================= PERFIL: PADRÃO ================= -->
      <div class="tab-panel active" data-tab-panel="padrao">
        <form class="calc-grid" id="calcForm" novalidate>
          <section class="calc-card" aria-labelledby="calcParamsTitle">
            <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 id="calcParamsTitle">Parâmetros</h2></div>
            {fields_html}
            <div class="tip-callout">
              <div class="icon-wrap"><svg class="icon"><use href="#i-bulb"/></svg></div>
              <div><strong>Lembre-se</strong><p>Esta ferramenta é um apoio ao cálculo clínico e não substitui a avaliação e o julgamento do profissional de enfermagem.</p></div>
            </div>
            <div class="form-actions">
              <button type="reset" class="btn btn-outline-navy" id="calcClearBtn">Limpar</button>
              <button type="submit" class="btn btn-green" id="calcSubmitBtn"><svg class="icon icon-sm"><use href="#i-calculator"/></svg> Calcular</button>
            </div>
          </section>

          <div>
            <section class="calc-card result-card" aria-live="polite">
              <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2>Resultado</h2></div>
              <div class="result-body">
                <p class="result-label">{esc(formula.get('resultLabel','Resultado'))}</p>
                <div class="result-value-wrap">
                  <span class="result-value" id="calcResultValue">{total_str}</span>
                  <span class="result-unit" id="calcResultUnit">{esc(result_unit)}</span>
                </div>
              </div>
              <div class="status-banner {'warning' if warn else 'success'}" id="calcStatusBanner">
                <div class="icon-wrap"><svg class="icon" id="calcStatusIcon"><use href="#{'i-warning' if warn else 'i-check'}"/></svg></div>
                <div>
                  <strong id="calcStatusTitle">{esc(rng['label'] if rng else '')}</strong>
                  <p id="calcStatusText">{esc(rng.get('clinicalImplications','') if rng else '')}</p>
                </div>
              </div>
              <div class="formula-strip">
                <div class="formula-row" id="calcFormulaRow">
                  {formula_cells}
                  <span class="formula-op">=</span>
                  <div class="formula-cell">
                    <div class="formula-box highlight" data-formula-box="__result__">{total_str}</div>
                    <span class="formula-cap">{esc(formula.get('resultLabel','Resultado'))}</span>
                  </div>
                </div>
              </div>
            </section>

            <section class="calc-card history-card" aria-labelledby="calcHistoryTitle">
              <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 id="calcHistoryTitle">Últimos cálculos</h2></div>
              <ul class="history-list" id="calcHistoryList">
                <li class="history-empty" id="calcHistoryEmpty">Seus últimos cálculos aparecerão aqui nesta sessão.</li>
              </ul>
            </section>
          </div>

          <div class="info-stack">
            <section class="calc-card info-card">
              <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2>Sobre esta ferramenta</h2></div>
              <p>{esc(ov.get('objective',''))} {esc(ov.get('indication',''))}</p>
            </section>
            <section class="calc-card info-card">
              <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2>Faixas de interpretação</h2></div>
              <ul class="glossary-list">{ranges_html}</ul>
            </section>
            <section class="calc-card info-card">
              <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2>Dicas importantes</h2></div>
              <ul class="tips-list">{tips_html}</ul>
            </section>
          </div>
        </form>
      </div>

      <!-- ================= PERFIL: ESTUDANTE ================= -->
      <div class="tab-panel" data-tab-panel="estudante">
        <div class="est-grid">
          <div class="side-stack">
            {step_cards_html}
            <div class="formula-dark">
              <div class="fd-eyebrow"><svg class="icon icon-sm"><use href="#i-bolt"/></svg> Como chegamos aqui</div>
              <h3>Construindo o cálculo, passo a passo</h3>
              <div class="fd-steps">
                {fd_steps_html}
                <div class="fd-divider"><div class="line"></div><div class="op">=</div><div class="line"></div></div>
                <div class="fd-final">
                  <div>
                    <div style="font-size:10.5px;text-transform:uppercase;letter-spacing:.1em;opacity:.85;font-weight:800;margin-bottom:4px;">{esc(formula.get('resultLabel','Resultado'))}</div>
                    <span class="fd-final-num" data-fd-step="__result__">{total_str}</span><span class="fd-final-unit">{esc(result_unit)}</span>
                  </div>
                  <span class="fd-final-badge{' alarm' if warn else ''}" id="estFdBadge"><svg class="icon icon-sm"><use href="#{'i-warning' if warn else 'i-check'}"/></svg> {esc(rng['label'] if rng else '')}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="side-stack">
            <section class="calc-card">
              <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px;">Exemplos prontos</h2></div>
              <div class="example-grid">{examples_html}</div>
            </section>
            <section class="calc-card">
              <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px;">Glossário rápido</h2></div>
              <ul class="glossary-list">{glossary_html}</ul>
            </section>
            {'''<section class="calc-card quiz-card" id="estQuizCard">
              <div class="calc-card-header" style="justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:10px;"><span class="bar" style="background:#7c3aed;" aria-hidden="true"></span><h2 style="font-size:15px;">Quiz rápido</h2></div>
                <span class="quiz-progress" id="estQuizProgress">1/1</span>
              </div>
              <p class="quiz-question" id="estQuizQuestion"></p>
              <ul class="quiz-opts" id="estQuizOpts"></ul>
              <div class="quiz-expl" id="estQuizExpl"></div>
              <button type="button" class="quiz-next" id="estQuizNext" style="display:none;">Próxima pergunta →</button>
            </section>''' if has_quiz else ''}
          </div>
        </div>
      </div>

      <!-- ================= PERFIL: MODO URGÊNCIA ================= -->
      <div class="tab-panel" data-tab-panel="urgencia">
        <div class="urg-panel">
          <div class="urg-inner">
            <div class="urg-top">
              <div><span class="urg-badge"><span class="dot"></span> Modo urgência ativo</span><h3>Cálculo rápido — {esc(ov['name'])}</h3></div>
              <div class="urg-presets">{urg_presets_html}</div>
            </div>
            <div class="urg-grid">{urg_fields_html}</div>
            <div class="urg-result">
              <div><span class="urg-result-num {'alarm' if warn else 'safe'}" id="urgResultNum">{total_str}</span><span class="urg-result-unit" id="urgResultUnit">{esc(result_unit)}</span></div>
              <span class="urg-alarm-badge {'alarm' if warn else 'safe'}" id="urgAlarmBadge"><svg class="icon icon-sm"><use href="#{'i-warning' if warn else 'i-check'}"/></svg> {esc(rng['label'] if rng else '')}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= PERFIL: ACADÊMICO ================= -->
      <div class="tab-panel" data-tab-panel="academico">
        <div class="aca-panel">
          <div class="aca-head">
            <div class="aca-eyebrow"><svg class="icon icon-sm"><use href="#i-book"/></svg> Visão acadêmica</div>
            <h3>{esc(ov['name'])}: cálculo, fundamentação e evidências</h3>
            <p>Conteúdo estruturado para estudo e referência, com fundamentação teórica, evidências da literatura e referências bibliográficas no padrão ABNT.</p>
          </div>
          <div class="aca-tabs">
            <div class="tabs-inner" data-tab-group="academico-conteudo" role="tablist">
              <button class="tab active" data-tab="calculo" type="button">Cálculo</button>
              <button class="tab" data-tab="fundamentacao" type="button">Fundamentação</button>
              {sae_tab_btn}
              <button class="tab" data-tab="evidencias" type="button">Evidências</button>
              <button class="tab" data-tab="referencias" type="button">Referências</button>
            </div>
          </div>
          <div class="aca-body" data-tab-panels="academico-conteudo">
            <div class="tab-panel active" data-tab-panel="calculo">
              <h4>Dados informados</h4>
              <p>{aca_dados}</p>
              <h4>Resultado</h4>
              <p>{esc(formula.get('resultLabel','Resultado'))}: <strong data-aca-value="__result__">{total_str} {esc(result_unit)}</strong> — <span data-aca-value="__range__">{esc(rng['label'] if rng else '')}</span></p>
              <button type="button" class="btn btn-outline-navy aca-print-btn" onclick="window.print()"><svg class="icon icon-sm"><use href="#i-printer"/></svg> Exportar / Imprimir</button>
            </div>
            <div class="tab-panel" data-tab-panel="fundamentacao">{evid_html}</div>
            {sae_tab_panel}
            <div class="tab-panel" data-tab-panel="evidencias">{valid_html}</div>
            <div class="tab-panel" data-tab-panel="referencias"><ol class="ref-list">{refs_html}</ol></div>
          </div>
        </div>
      </div>

      <!-- ================= PERFIL: GESTOR (demonstrativo) ================= -->
      <div class="tab-panel" data-tab-panel="gestor">
        <div class="gestor-notice"><svg class="icon"><use href="#i-warning"/></svg> Painel demonstrativo — os dados abaixo são fictícios (mock), pensados como referência de layout. Para uso real, conecte esta visão a uma fonte de dados/backend da sua instituição.</div>
        <div class="kpi-grid">
          <div class="kpi-card"><div class="kpi-label">Avaliações (7 dias)</div><div class="kpi-value">284</div><div class="kpi-sub">▲ 9% vs. semana anterior</div></div>
          <div class="kpi-card"><div class="kpi-label">Dentro da faixa esperada</div><div class="kpi-value">231</div><div class="kpi-sub">81% do total</div></div>
          <div class="kpi-card"><div class="kpi-label">Casos de alto risco</div><div class="kpi-value">37</div><div class="kpi-sub" style="color:#ef4444;">13% do total</div></div>
          <div class="kpi-card"><div class="kpi-label">Unidades ativas</div><div class="kpi-value">4</div><div class="kpi-sub">UTI, Enfermaria, Pediatria, Emergência</div></div>
        </div>
        <div class="gestor-grid">
          <section class="calc-card">
            <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px;">Avaliações por dia (últimos 7 dias)</h2></div>
            <div class="bar-chart">
              <div class="bar-col"><span class="bar-val">38</span><div class="bar" style="height:60%;"></div><span class="bar-day">Seg</span></div>
              <div class="bar-col"><span class="bar-val">33</span><div class="bar" style="height:52%;"></div><span class="bar-day">Ter</span></div>
              <div class="bar-col"><span class="bar-val">47</span><div class="bar" style="height:75%;"></div><span class="bar-day">Qua</span></div>
              <div class="bar-col"><span class="bar-val">41</span><div class="bar" style="height:65%;"></div><span class="bar-day">Qui</span></div>
              <div class="bar-col"><span class="bar-val">58</span><div class="bar" style="height:92%;"></div><span class="bar-day">Sex</span></div>
              <div class="bar-col"><span class="bar-val">27</span><div class="bar" style="height:43%;"></div><span class="bar-day">Sáb</span></div>
              <div class="bar-col"><span class="bar-val">40</span><div class="bar" style="height:63%;"></div><span class="bar-day">Dom</span></div>
            </div>
          </section>
          <section class="calc-card">
            <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px;">Distribuição por faixa de risco</h2></div>
            <div class="equipo-dist">{gestor_dist_html}</div>
          </section>
        </div>
        <section class="calc-card">
          <div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px;">Trilha de auditoria (amostra)</h2></div>
          <div style="overflow-x:auto;">
            <table class="audit-table">
              <thead><tr><th>ID</th><th>Data</th><th>Avaliação</th><th>Resultado</th><th>Status</th><th>Profissional</th></tr></thead>
              <tbody>
                <tr><td>A-3021</td><td>02/07 09:14</td><td>{esc(ov['name'])}</td><td>{total_str} {esc(result_unit)}</td><td><span class="audit-status ok">OK</span></td><td>Enf. Carla</td></tr>
                <tr><td>A-3020</td><td>02/07 08:40</td><td>{esc(ov['name'])}</td><td>—</td><td><span class="audit-status alarm">Alarme</span></td><td>Enf. Pedro</td></tr>
                <tr><td>A-3019</td><td>01/07 22:05</td><td>{esc(ov['name'])}</td><td>—</td><td><span class="audit-status ok">OK</span></td><td>Enf. Joana</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>

    </div>

    <section class="about-section">
      <div class="about-grid">
        <div class="about-box">
          <h2>{esc(about.get('title', 'Como funciona ' + ov['name']))}</h2>
          {about.get('html','')}
          {faq_html}
        </div>
        <div class="disclaimer-card">
          <h3><svg class="icon"><use href="#i-shieldcheck"/></svg> Aviso importante</h3>
          <p>Esta ferramenta tem finalidade educacional e de apoio à decisão clínica. Os resultados devem ser sempre conferidos e validados por um profissional de enfermagem qualificado, de acordo com a avaliação do paciente e os protocolos da instituição.</p>
        </div>
      </div>
    </section>

  </div>
</main>

<script type="application/json" id="tool-config">{tool_config_json}</script>

<svg style="display:none" aria-hidden="true"><defs>
  <symbol id="i-cross" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7.5v9M7.5 12h9"/></symbol>
  <symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.6" y2="16.6"/></symbol>
  <symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></symbol>
  <symbol id="i-moon" viewBox="0 0 24 24"><path d="M20.5 13.9A8.5 8.5 0 1 1 10.1 3.5a7 7 0 0 0 10.4 10.4z"/></symbol>
  <symbol id="i-file" viewBox="0 0 24 24"><path d="M6 3h9l4 4v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M15 3v4h4"/><line x1="8.5" y1="12" x2="15.5" y2="12"/><line x1="8.5" y1="15.5" x2="15.5" y2="15.5"/><line x1="8.5" y1="8.5" x2="11" y2="8.5"/></symbol>
  <symbol id="i-users" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.2"/><path d="M3.5 20c0-3.3 2.5-5.8 5.5-5.8s5.5 2.5 5.5 5.8"/><circle cx="17.5" cy="9" r="2.4"/><path d="M15.7 14.5c2.4.3 4.3 2.4 4.3 5"/></symbol>
  <symbol id="i-trend" viewBox="0 0 24 24"><polyline points="3 17 9.5 10.5 13.5 14.5 21 6.5"/><polyline points="15 6.5 21 6.5 21 12.5"/></symbol>
  <symbol id="i-book" viewBox="0 0 24 24"><path d="M12 6.2c-2-1.6-5-2.1-8-1.6v13.6c3-.5 6 0 8 1.6 2-1.6 5-2.1 8-1.6V4.6c-3-.5-6 0-8 1.6z"/><line x1="12" y1="6.2" x2="12" y2="19.8"/></symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><polyline points="8 12.5 10.8 15.3 16 9.3"/></symbol>
  <symbol id="i-bulb" viewBox="0 0 24 24"><path d="M9.5 18.5h5M10.3 21h3.4M12 3.2a6.2 6.2 0 0 0-3.2 11.5c1 .8 1.2 1.6 1.2 2.3h4c0-.7.2-1.5 1.2-2.3A6.2 6.2 0 0 0 12 3.2z"/></symbol>
  <symbol id="i-clipcheck" viewBox="0 0 24 24"><rect x="5.5" y="4.5" width="13" height="16.5" rx="2"/><rect x="9" y="2.5" width="6" height="3.5" rx="1"/><polyline points="9 13 11 15 15 10.5"/></symbol>
  <symbol id="i-arrow" viewBox="0 0 24 24"><line x1="4" y1="12" x2="19" y2="12"/><polyline points="13 6 19 12 13 18"/></symbol>
  <symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 2.2 4.8 13.5h5.8l-1 8.3 8.4-11.3h-5.8l1-8.3z"/></symbol>
  <symbol id="i-share" viewBox="0 0 24 24"><circle cx="6" cy="12" r="2.2"/><circle cx="18" cy="6" r="2.2"/><circle cx="18" cy="18" r="2.2"/><line x1="8" y1="11" x2="16" y2="7"/><line x1="8" y1="13" x2="16" y2="17"/></symbol>
  <symbol id="i-bookmark" viewBox="0 0 24 24"><path d="M6 3.5h12v17l-6-4-6 4z"/></symbol>
  <symbol id="i-printer" viewBox="0 0 24 24"><rect x="6" y="9" width="12" height="7" rx="1.5"/><path d="M7 9V4.5h10V9"/><path d="M7 16v3.5h10V16"/><circle cx="16" cy="12" r="0.6" fill="currentColor" stroke="none"/></symbol>
  <symbol id="i-star" viewBox="0 0 24 24"><path d="M12 3.5l2.6 5.5 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6-4.4-4.2 6-.8z"/></symbol>
  <symbol id="i-warning" viewBox="0 0 24 24"><path d="M12 3.5l10 17.5H2z"/><line x1="12" y1="10" x2="12" y2="15"/><circle cx="12" cy="17.7" r="0.7" fill="currentColor" stroke="none"/></symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.5"/><path d="M10 8.3l6 3.7-6 3.7z" fill="currentColor" stroke="none"/></symbol>
  <symbol id="i-cap" viewBox="0 0 24 24"><path d="M12 4.5 2 9l10 4.5L22 9z"/><path d="M6 11v5c0 1.5 3 3 6 3s6-1.5 6-3v-5"/><line x1="22" y1="9" x2="22" y2="15"/></symbol>
  <symbol id="i-person" viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-4 3-6.5 7-6.5s7 2.5 7 6.5"/></symbol>
  <symbol id="i-calculator" viewBox="0 0 24 24"><rect x="4.5" y="4.5" width="15" height="15" rx="2"/><line x1="8" y1="8.5" x2="16" y2="8.5"/><line x1="8" y1="12" x2="8.01" y2="12"/><line x1="12" y1="12" x2="12.01" y2="12"/><line x1="16" y1="12" x2="16.01" y2="12"/><line x1="8" y1="15.5" x2="8.01" y2="15.5"/><line x1="12" y1="15.5" x2="12.01" y2="15.5"/><line x1="16" y1="15.5" x2="16.01" y2="15.5"/></symbol>
  <symbol id="i-shieldcheck" viewBox="0 0 24 24"><path d="M12 3l7 3v6c0 5-3 8.2-7 9.2-4-1-7-4.2-7-9.2V6l7-3z"/><polyline points="9 12 11 14 15.5 9"/></symbol>
  <symbol id="i-flask" viewBox="0 0 24 24"><path d="M9 3h6M10 3v6l-5.5 9.5A2 2 0 0 0 6.2 21h11.6a2 2 0 0 0 1.7-3L14 9V3"/><line x1="8" y1="15" x2="16" y2="15"/></symbol>
  <symbol id="i-leaf" viewBox="0 0 24 24"><path d="M5 21c0-9.5 6.5-16 16-16 0 9.5-6.5 16-16 16z"/><path d="M5 21c3.2-3.2 6.3-6.5 9-11"/></symbol>
  <symbol id="i-rocket" viewBox="0 0 24 24"><path d="M12 2.5c3 2 5 6 5 10.3 0 2-.9 3.9-2 5.2l-3 3-3-3c-1.1-1.3-2-3.2-2-5.2 0-4.3 2-8.3 5-10.3z"/><circle cx="12" cy="11" r="1.8"/><path d="M8 17l-2.5 4.5M16 17l2.5 4.5"/></symbol>
  <symbol id="i-brain" viewBox="0 0 24 24"><rect x="5" y="8" width="14" height="11" rx="2.5"/><circle cx="9.2" cy="13.2" r="1.1" fill="currentColor" stroke="none"/><circle cx="14.8" cy="13.2" r="1.1" fill="currentColor" stroke="none"/><line x1="12" y1="4" x2="12" y2="8"/><circle cx="12" cy="3.4" r="1.2" fill="currentColor" stroke="none"/><line x1="2" y1="12.5" x2="5" y2="12.5"/><line x1="19" y1="12.5" x2="22" y2="12.5"/></symbol>
  <symbol id="i-cloud" viewBox="0 0 24 24"><path d="M6.5 18.5h11a4 4 0 0 0 0-8 6.2 6.2 0 0 0-11.8 1.6A3.6 3.6 0 0 0 6.5 18.5z"/></symbol>
  <symbol id="i-monitor" viewBox="0 0 24 24"><rect x="3" y="4.5" width="18" height="12" rx="2"/><line x1="8" y1="20" x2="16" y2="20"/><line x1="12" y1="16.5" x2="12" y2="20"/></symbol>
  <symbol id="i-gauge" viewBox="0 0 24 24"><circle cx="12" cy="12.5" r="8.5"/><line x1="12" y1="12.5" x2="15.5" y2="9"/><circle cx="12" cy="12.5" r="1" fill="currentColor" stroke="none"/><line x1="12" y1="4.3" x2="12" y2="5.8"/></symbol>
  <symbol id="i-sliders" viewBox="0 0 24 24"><line x1="6" y1="4" x2="6" y2="20"/><circle cx="6" cy="9.5" r="2" fill="#fff"/><line x1="12" y1="4" x2="12" y2="20"/><circle cx="12" cy="15.5" r="2" fill="#fff"/><line x1="18" y1="4" x2="18" y2="20"/><circle cx="18" cy="7.5" r="2" fill="#fff"/></symbol>
  <symbol id="i-access" viewBox="0 0 24 24"><circle cx="12" cy="4.3" r="1.8" fill="currentColor" stroke="none"/><path d="M4.5 9h15M12 9v5.5l-4.2 7.2M12 13.8l4.2 6.9"/></symbol>
  <symbol id="i-lock" viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9.5" rx="2"/><path d="M8 11V7.5a4 4 0 0 1 8 0V11"/></symbol>
  <symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 3l7 3v6c0 5-3 8.2-7 9.2-4-1-7-4.2-7-9.2V6l7-3z"/></symbol>
  <symbol id="i-cookie" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="9" cy="9.5" r="1" fill="currentColor" stroke="none"/><circle cx="14.5" cy="8.5" r="1" fill="currentColor" stroke="none"/><circle cx="15.5" cy="14" r="1" fill="currentColor" stroke="none"/><circle cx="9.5" cy="15" r="1" fill="currentColor" stroke="none"/></symbol>
  <symbol id="i-clipboard" viewBox="0 0 24 24"><rect x="5.5" y="4.5" width="13" height="16.5" rx="2"/><rect x="9" y="2.5" width="6" height="3.5" rx="1"/><line x1="8.5" y1="11.5" x2="15.5" y2="11.5"/><line x1="8.5" y1="15.5" x2="15.5" y2="15.5"/></symbol>
  <symbol id="i-download" viewBox="0 0 24 24"><path d="M12 3v12.5M7 11.5l5 5 5-5"/><line x1="5" y1="20.5" x2="19" y2="20.5"/></symbol>
  <symbol id="i-refresh" viewBox="0 0 24 24"><path d="M21.5 4v6h-6"/><path d="M2.5 20v-6h6"/><path d="M4 10a8 8 0 0 1 13.4-3.6L21.5 10"/><path d="M20 14a8 8 0 0 1-13.4 3.6L2.5 14"/></symbol>
  <symbol id="i-pulse" viewBox="0 0 24 24"><polyline points="2.5 13 7.5 13 9.5 6 13.5 19 16 13 21.5 13"/></symbol>
  <symbol id="i-headphone" viewBox="0 0 24 24"><path d="M4 14a8 8 0 0 1 16 0"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/></symbol>
  <symbol id="i-headset" viewBox="0 0 24 24"><path d="M4 14a8 8 0 0 1 16 0v4"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/><path d="M20 18a3 3 0 0 1-3 3h-2"/></symbol>
  <symbol id="i-handshake" viewBox="0 0 24 24"><path d="M2 12l4-3 3 2 3-2 3 2 3-2 4 3"/><path d="M7 11l3 6M14 11l-3 6"/></symbol>
  <symbol id="i-building" viewBox="0 0 24 24"><rect x="4" y="3" width="10" height="18" rx="1"/><rect x="14" y="9" width="6" height="12" rx="1"/><line x1="7" y1="7" x2="7.01" y2="7"/><line x1="11" y1="7" x2="11.01" y2="7"/><line x1="7" y1="11" x2="7.01" y2="11"/><line x1="11" y1="11" x2="11.01" y2="11"/><line x1="7" y1="15" x2="7.01" y2="15"/><line x1="11" y1="15" x2="11.01" y2="15"/></symbol>
  <symbol id="i-briefcase" viewBox="0 0 24 24"><rect x="3" y="8" width="18" height="12" rx="2"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="3" y1="13" x2="21" y2="13"/></symbol>
  <symbol id="i-stetho" viewBox="0 0 24 24"><path d="M5 3v5a3 3 0 0 0 6 0V3"/><path d="M8 11v2.5a6 6 0 0 0 12 0v-1.5"/><circle cx="20" cy="10.5" r="2.2"/></symbol>
  <symbol id="i-network" viewBox="0 0 24 24"><circle cx="12" cy="5" r="2.2"/><circle cx="5" cy="18" r="2.2"/><circle cx="19" cy="18" r="2.2"/><path d="M12 7.2v5M10.5 13.5 6.5 16M13.5 13.5l4 2.5"/></symbol>
  <symbol id="i-sitemap" viewBox="0 0 24 24"><rect x="9" y="2.5" width="6" height="5" rx="1"/><rect x="2" y="12.5" width="6" height="5" rx="1"/><rect x="16" y="12.5" width="6" height="5" rx="1"/><line x1="12" y1="7.5" x2="12" y2="10"/><line x1="5" y1="12.5" x2="5" y2="10"/><line x1="19" y1="12.5" x2="19" y2="10"/><path d="M5 10h14"/></symbol>
  <symbol id="i-tags" viewBox="0 0 24 24"><circle cx="8" cy="8" r="1.5" fill="currentColor" stroke="none"/><path d="M12.5 2.5l-8 8a2 2 0 0 0 0 2.8l6.2 6.2a2 2 0 0 0 2.8 0l8-8a2 2 0 0 0 .6-1.4V4.5a2 2 0 0 0-2-2z"/><path d="M4.5 10.5l-2 2a2 2 0 0 0 0 2.8l6.2 6.2"/></symbol>
  <symbol id="i-link" viewBox="0 0 24 24"><path d="M10 13.5l2.5 2.5a2.5 2.5 0 0 0 3.5-3.5L13 9.5"/><path d="M14 10.5l-2.5-2.5a2.5 2.5 0 0 0-3.5 3.5L11 14.5"/></symbol>
</defs></svg>

<div id="site-footer"></div>
<div id="site-cookie"></div>

<script src="js/calc-engine.js"></script>
<script src="js/partials-loader.js"></script>
</body>
</html>
"""
    return page


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 generate_tool_page.py data/tools/<slug>.json", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        cfg = json.load(f)
    sys.stdout.write(build(cfg))


if __name__ == "__main__":
    main()
