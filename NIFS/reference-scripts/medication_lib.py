"""Render the medication hub (/medicamentos) and nursing monograph pages.

Rich monographs come from datasets/clinical/drug_monographs.json and are linked
to the broader DrugReference catalog (datasets/clinical/drug_references.json).
Pages reuse website_lib.render_page so they inherit chrome, SEO head, hreflang
and JSON-LD; a schema.org Drug node is injected per monograph.
"""
from __future__ import annotations

from website_lib import SITE_NAME, esc, render_page, slugify

ALERT_STYLE = (
    "border:1px solid #f1b0b0;background:#fdeaea;border-radius:8px;"
    "padding:.85rem 1rem;margin-bottom:1rem"
)
LASA_STYLE = (
    "border:1px solid #f3d39b;background:#fdf4e3;border-radius:8px;"
    "padding:.85rem 1rem;margin-bottom:1rem"
)


def _ul(items: list[str]) -> str:
    return "".join(f"<li>{esc(i)}</li>" for i in items if i)


def _drug_jsonld(m: dict) -> dict:
    node = {
        "@type": "Drug",
        "name": m.get("generic_name_pt", ""),
        "nonProprietaryName": m.get("generic_name_pt", ""),
        "drugClass": m.get("drug_class", ""),
        "mechanismOfAction": m.get("mechanism_of_action", ""),
    }
    if m.get("trade_names"):
        node["alternateName"] = m["trade_names"]
    if m.get("pregnancy_category"):
        node["pregnancyCategory"] = m["pregnancy_category"]
    return node


def render_medication_page(m: dict, safety_goals: dict, med_rights: list[dict],
                           depth: int = 2) -> str:
    name = m.get("generic_name_pt", "")
    icon = m.get("icon", "💊")

    blocks = []
    if m.get("high_alert_medication"):
        blocks.append(
            f'<div class="card" role="alert" style="{ALERT_STYLE}">'
            "<strong>⚠️ MEDICAMENTO DE ALTA VIGILÂNCIA (ISMP)</strong>"
            "<p>Requer dupla checagem obrigatória por dois profissionais antes da administração. "
            "Erros com este medicamento têm maior potencial de causar dano significativo ao paciente.</p></div>"
        )
    if m.get("look_alike_sound_alike"):
        blocks.append(
            f'<div class="card" role="alert" style="{LASA_STYLE}">'
            "<strong>👁️ Atenção LASA (Look-Alike, Sound-Alike)</strong>"
            f"<ul class=\"meta-list\">{_ul(m['look_alike_sound_alike'])}</ul></div>"
        )

    # Mechanism / indications / contraindications
    blocks.append(
        '<section class="section section-container"><div class="card">'
        f"<h2>Mecanismo de Ação</h2><p>{esc(m.get('mechanism_of_action', ''))}</p>"
        f"<h3>Indicações</h3><ul class=\"meta-list\">{_ul(m.get('indications', []))}</ul>"
        f"<h3>Contraindicações</h3><ul class=\"meta-list\">{_ul(m.get('contraindications', []))}</ul>"
        "</div></section>"
    )

    # Routes
    route_cards = []
    for r in m.get("routes", []):
        flags = []
        if r.get("filter_required"):
            flags.append("Filtro obrigatório")
        if r.get("light_protection"):
            flags.append("Proteção da luz")
        route_cards.append(
            '<div class="card">'
            f'<span class="badge">{esc(r.get("route", ""))}</span>'
            f"<p><strong>Preparo:</strong> {esc(r.get('preparation', '—'))}</p>"
            f"<p><strong>Diluição:</strong> {esc(r.get('dilution', '—'))}</p>"
            f"<p><strong>Tempo/infusão:</strong> {esc(r.get('infusion_time', '—'))}</p>"
            + (f"<p><strong>Atenção:</strong> {esc(' · '.join(flags))}</p>" if flags else "")
            + "</div>"
        )
    if route_cards:
        blocks.append(
            '<section class="section section-container"><h2>💉 Vias de Administração</h2>'
            f'<div class="card-grid">{"".join(route_cards)}</div></section>'
        )

    # Doses
    blocks.append(
        '<section class="section section-container"><div class="card"><h2>Doses</h2>'
        f"<p><strong>Adulto:</strong> {esc(m.get('dosage_adult', '—'))}</p>"
        f"<p><strong>Pediátrico:</strong> {esc(m.get('dosage_pediatric', '—'))}</p></div></section>"
    )

    # Monitoring / adverse / incompatibilities
    mon = m.get("nursing_monitoring", [])
    adv = m.get("adverse_effects_nursing_relevant", [])
    inc = m.get("incompatibilities", [])
    blocks.append(
        '<section class="section section-container"><div class="card">'
        "<h2>🔍 Monitorização de Enfermagem</h2>"
        f"<ul class=\"meta-list\">{_ul(mon)}</ul>"
        + (f"<h3>Reações adversas relevantes</h3><ul class=\"meta-list\">{_ul(adv)}</ul>" if adv else "")
        + (f"<h3>Incompatibilidades</h3><ul class=\"meta-list\">{_ul(inc)}</ul>" if inc else "")
        + "</div></section>"
    )

    # 9 Certos
    rights_rows = "".join(
        f"<li><strong>{esc(r['name'])}:</strong> {esc(r['description'])}</li>"
        for r in med_rights
    )
    blocks.append(
        '<section class="section section-container"><div class="card">'
        "<h2>💊 Os 9 Certos da Administração de Medicamentos</h2>"
        f"<ul class=\"meta-list\">{rights_rows}</ul></div></section>"
    )

    # Patient education + storage
    blocks.append(
        '<section class="section section-container"><div class="card">'
        f"<h2>Orientação ao paciente</h2><p>{esc(m.get('patient_education', '—'))}</p>"
        f"<h3>🗄️ Armazenamento</h3><p>{esc(m.get('storage_conditions', '—'))}</p>"
        f"<p style=\"font-size:.85rem;color:var(--gray-700,#555)\">Categoria gestacional: {esc(m.get('pregnancy_category', 'N/D'))}"
        f"{' · Substância controlada' if m.get('controlled_substance') else ''}</p></div></section>"
    )

    blocks.append(
        '<section class="section section-container"><div class="card" '
        'style="font-size:.85rem;color:#555">⚠️ Conteúdo de apoio à prática de enfermagem. '
        "Sempre consulte a bula do fabricante e o protocolo institucional vigente.</div></section>"
    )

    body = "".join(blocks)
    subtitle = " · ".join(
        s for s in [m.get("drug_class", ""), m.get("pharmacological_group", "")] if s
    )
    if m.get("trade_names"):
        subtitle += f" · {', '.join(m['trade_names'])}"

    return render_page(
        depth=depth,
        title=f"{name} — Bula de Enfermagem | {SITE_NAME}",
        description=f"{name} — preparo, vias, monitorização de enfermagem, incompatibilidades e os 9 Certos. {m.get('drug_class', '')}.",
        canonical_path=f"/medicamentos/{m['slug']}",
        hero_title=f"{icon} {name}",
        hero_subtitle=subtitle,
        breadcrumbs=[
            ("Medicamentos", "../index.html" if depth >= 2 else "index.html"),
            (name, None),
        ],
        body=body,
        json_ld=[_drug_jsonld(m)],
    )


def render_medication_hub(monographs: list[dict], drug_refs: list[dict],
                          depth: int = 1) -> str:
    # Featured rich monographs
    mono_cards = []
    for m in monographs:
        badges = '<span class="badge">Alta vigilância</span>' if m.get("high_alert_medication") else ""
        mono_cards.append(
            '<article class="card">'
            f'{badges}<h3><a href="{esc(m["slug"])}/index.html">{esc(m.get("icon", "💊"))} {esc(m["generic_name_pt"])}</a></h3>'
            f"<p>{esc(m.get('drug_class', ''))} — {esc(m.get('pharmacological_group', ''))}</p></article>"
        )
    featured = (
        '<section class="section section-container"><h2>Bulas de Enfermagem</h2>'
        '<p>Monografias detalhadas com preparo, vias, monitorização e os 9 Certos contextualizados.</p>'
        f'<div class="card-grid">{"".join(mono_cards)}</div></section>'
    )

    # Reference catalog grouped by pharmacological class
    by_class: dict[str, list[dict]] = {}
    for d in drug_refs:
        cls = d.get("pharmacological_class") or "Outros"
        by_class.setdefault(cls, []).append(d)
    class_rows = []
    for cls in sorted(by_class):
        items = by_class[cls]
        names = ", ".join(sorted({d.get("generic_name_pt") or d.get("generic_name", "") for d in items})[:8])
        high = sum(1 for d in items if d.get("high_alert"))
        badge = f' <span class="badge">{high} alta vigilância</span>' if high else ""
        class_rows.append(f"<li><strong>{esc(cls)}</strong> ({len(items)}){badge} — {esc(names)}</li>")
    catalog = (
        '<section class="section section-container"><h2>Catálogo de referência</h2>'
        f"<p>{len(drug_refs)} medicamentos indexados por classe farmacológica (referência farmacológica 2026).</p>"
        f'<ul class="meta-list">{"".join(class_rows)}</ul></section>'
    )

    return render_page(
        depth=depth,
        title=f"Medicamentos — Bulas de Enfermagem | {SITE_NAME}",
        description="Referência de medicamentos focada em enfermagem: preparo, vias, monitorização, incompatibilidades e os 9 Certos contextualizados.",
        canonical_path="/medicamentos",
        hero_title="Medicamentos",
        hero_subtitle="Bulas de enfermagem e catálogo de referência farmacológica — Calculadoras de Enfermagem 2026.",
        breadcrumbs=[("Medicamentos", None)],
        body=featured + catalog,
    )
