#!/usr/bin/env python3
"""Fail-closed kernel for canonical object families.

Norms, tools and libraries are canonical. HTML is a projection.
Canonical ≠ published ≠ Vigente ≠ released.
"""
from __future__ import annotations

import html as htmlmod
from typing import Any

REQUIRED_KINDS = ("normative_instrument", "tool", "library_article")
GOVERNED_ALLOWED = {"VERIFY_PENDING", "HOLD", "QUARANTINE"}
FORBIDDEN_GOVERNED = {"Vigente", "published", "publicado", "RELEASED", "ACTIVE"}


def validate_catalog(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if doc.get("kind") != "canonical_object_catalog":
        errors.append("kind must be canonical_object_catalog")
    if doc.get("release_allowed") is not False:
        errors.append("release_allowed must be false")
    if doc.get("assigns_vigencia") is not False:
        errors.append("assigns_vigencia must be false")
    if doc.get("canonical_promotion") is not False:
        errors.append("canonical_promotion must be false")
    if doc.get("status") not in GOVERNED_ALLOWED:
        errors.append("catalog status must stay HOLD|VERIFY_PENDING|QUARANTINE")
    kinds = doc.get("canonical_kinds") or []
    for required in REQUIRED_KINDS:
        if required not in kinds:
            errors.append(f"canonical kind missing: {required}")
    families = {row.get("id"): row for row in (doc.get("families") or []) if isinstance(row, dict)}
    for required in REQUIRED_KINDS:
        family = families.get(required)
        if not family:
            errors.append(f"family missing: {required}")
            continue
        if family.get("canonical") is not True:
            errors.append(f"{required}: canonical must be true")
        if not family.get("template_id"):
            errors.append(f"{required}: template_id required")
        if int(family.get("objects_n") or 0) < 1:
            errors.append(f"{required}: empty family is FAIL")
        governed = family.get("governed_status")
        if governed not in GOVERNED_ALLOWED:
            errors.append(f"{required}: governed_status forbidden ({governed})")
        if governed in FORBIDDEN_GOVERNED or family.get("observed_as_governed") is True:
            errors.append(f"{required}: payload published/Vigente is not governed status")
    tools = families.get("tool") or {}
    if int(tools.get("observed_payload_status_published_n") or 0) > 0 and tools.get("governed_status") == "published":
        errors.append("tool: observed published cannot become governed published")
    return errors


def render_catalog(doc: dict[str, Any]) -> str:
    errors = validate_catalog(doc)
    if errors:
        raise ValueError("cannot render invalid catalog: " + "; ".join(errors))
    esc = htmlmod.escape
    rows = []
    for family in doc.get("families") or []:
        rows.append(
            "<tr>"
            f"<td><code>{esc(family.get('id', ''))}</code></td>"
            f"<td>{'sim' if family.get('canonical') else 'não'}</td>"
            f"<td><code>{esc(family.get('template_id', ''))}</code></td>"
            f"<td>{int(family.get('objects_n') or 0)}</td>"
            f"<td>{int(family.get('atomized_n') or 0)}</td>"
            f"<td>{esc(family.get('governed_status', ''))}</td>"
            f"<td>{esc(family.get('materialization', ''))}</td>"
            "</tr>"
        )
    tool_rows = []
    for tool in (doc.get("materialization") or {}).get("tool_index") or []:
        tool_rows.append(
            "<tr>"
            f"<td><code>{esc(tool.get('slug', ''))}</code></td>"
            f"<td>{esc(tool.get('name', ''))}</td>"
            f"<td><code>{esc(tool.get('source', ''))}</code></td>"
            f"<td>{esc(tool.get('observed_payload_status', ''))}</td>"
            f"<td>HOLD</td>"
            "</tr>"
        )
    findings = doc.get("findings") or []
    finding_html = "".join(f"<li><code>{esc(item.get('id', ''))}</code> — {esc(item.get('statement', ''))}</li>" for item in findings)
    by_id = {row["id"]: row for row in doc["families"]}
    n_norm = int(by_id["normative_instrument"]["objects_n"])
    n_tool = int(by_id["tool"]["objects_n"])
    n_lib = int(by_id["library_article"]["objects_n"])
    return f"""<!doctype html>
<html lang="pt-BR" data-cko-md="CKO-MD" data-cko-reg="CKO-REG" data-cko-norm="NIFS-900-03" data-cko-evidence="HOLD" data-cko-chain="MD / REG / Schema / Engine / Validator / Renderer / Runtime / Frontend" data-cko-template="canonical-catalog">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Objectos canónicos | HOLD</title>
<meta name="description" content="Normas, ferramentas e bibliotecas são canónicas. HTML é projecção. Não é vigência nem release.">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1A3E74">
<link rel="stylesheet" href="/public/output.css">
<link rel="stylesheet" href="/global-styles.css">
<style id="candidate-preview-only">
:root{{--cko-navy:#1A3E74;--cko-navy2:#1E4D8C;--cko-navy3:#163269;--cko-link:#1D4ED8;--cko-focus:#1D4ED8;--cko-text:#1f2937;--cko-muted:#475569;--cko-bg:#f8fafc}}
*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,system-ui,sans-serif;color:var(--cko-text);background:var(--cko-bg);line-height:1.65}}
a{{color:var(--cko-link)}}a:focus-visible{{outline:3px solid var(--cko-focus);outline-offset:3px}}
.skip{{position:absolute;left:-9999px}}.skip:focus{{left:1rem;top:1rem;background:white;padding:.8rem;z-index:9}}
.shell{{width:min(1120px,calc(100% - 2rem));margin-inline:auto}}.crumbs{{font-size:.88rem;margin:1rem 0}}
.hero{{border-radius:1.4rem;background:linear-gradient(135deg,var(--cko-navy),var(--cko-navy2) 60%,var(--cko-navy3));color:white;margin:1rem 0 2rem}}
.hero-content{{padding:clamp(2rem,6vw,4rem);max-width:860px}}
.eyebrow{{font-weight:800;text-transform:uppercase;letter-spacing:.14em;font-size:.75rem;color:#bfdbfe}}
.hero h1{{font-family:'Nunito Sans',Inter,sans-serif;font-size:clamp(1.6rem,4vw,2.6rem);line-height:1.1;margin:.5rem 0 1rem}}
.card{{background:white;border:1px solid #dbeafe;border-radius:1rem;padding:1.25rem;margin-bottom:1rem}}
.hold{{border-left:4px solid #7c3aed;background:#f5f3ff}}.warn{{border-left:4px solid #b45309;background:#fffbeb}}
table{{width:100%;border-collapse:collapse;font-size:.88rem}}th,td{{text-align:left;padding:.45rem .3rem;border-bottom:1px solid #e2e8f0;vertical-align:top}}
.label{{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;background:#e0e7ff;color:#3730a3;padding:.25rem .5rem;border-radius:999px}}
.small{{font-size:.88rem;color:var(--cko-muted)}}code{{font-size:.86em;background:#f1f5f9;padding:.1rem .3rem;border-radius:.3rem}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin:1rem 0}}
.kpi{{background:white;border:1px solid #dbeafe;border-radius:1rem;padding:1rem}}
.kpi b{{display:block;font-size:1.6rem;color:var(--cko-navy)}}
@media(max-width:800px){{.kpis{{grid-template-columns:1fr}}}}
</style>
</head>
<body data-cko-status="CANDIDATE_HOLD_RELEASE" data-cko-scope="CANONICAL_OBJECTS_HOLD">
<a class="skip" href="#main-content">Pular para o conteúdo principal</a>
<div id="global-header-container"></div>
<main id="main-content" class="shell">
<nav class="crumbs" aria-label="Breadcrumb" data-cko-static="breadcrumb"><a href="/">Início</a> <span aria-hidden="true">›</span> <a href="/cko-governanca.html">Governação</a> <span aria-hidden="true">›</span> <span aria-current="page">Canónicos</span></nav>
<section class="hero" data-cko-static="hero"><div class="hero-content">
  <div class="eyebrow">HOLD · canónico · normas · ferramentas · bibliotecas</div>
  <h1>O original é o objecto. A página é projecção.</h1>
  <p>Normas, ferramentas (calculadoras, escalas) e bibliotecas são canónicas. O HTML não é a fonte. Canonical não é published, não é Vigente e não é release.</p>
</div></section>
<div class="kpis">
  <div class="kpi"><span class="small">Normas atomizadas</span><b>{n_norm}</b></div>
  <div class="kpi"><span class="small">Ferramentas JSON</span><b>{n_tool}</b></div>
  <div class="kpi"><span class="small">Artigos de biblioteca</span><b>{n_lib}</b></div>
</div>
<article class="card hold">
  <span class="label">Invariante</span>
  <h2>{esc(doc.get("invariant") or "")}</h2>
  <p>release_allowed = false · assigns_vigencia = false · canonical_promotion = false · UT implemented_n = 0</p>
</article>
<article class="card">
  <h2>Famílias canónicas</h2>
  <table>
    <thead><tr><th>Kind</th><th>Canónico</th><th>Template</th><th>N</th><th>Atomizados</th><th>Estado governado</th><th>Materialização</th></tr></thead>
    <tbody>
{''.join(rows)}
    </tbody>
  </table>
</article>
<article class="card">
  <h2>Ferramentas observadas</h2>
  <p class="small">O JSON em <code>data/tools</code> é o payload canónico. O HTML da calculadora é a projecção do template <code>tool</code>. O campo <code>status: published</code> no payload permanece drift: o estado governado é HOLD.</p>
  <table>
    <thead><tr><th>Slug</th><th>Nome</th><th>Fonte</th><th>Payload</th><th>Governado</th></tr></thead>
    <tbody>
{''.join(tool_rows)}
    </tbody>
  </table>
</article>
<article class="card warn">
  <h2>Achados</h2>
  <ul>{finding_html}</ul>
  <p class="small">Não gerámos 1332 HTML novos. Não promovemos 97 published. Não atribuímos vigência às normas.</p>
</article>
</main>
<div id="footer-placeholder"></div>
<script src="/global-scripts.js" defer></script>
</body>
</html>
"""
