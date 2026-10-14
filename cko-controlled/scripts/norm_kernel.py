#!/usr/bin/env python3
"""Fail-closed kernel for normative instruments.

Does not ingest HTTP. Does not assign Vigente. Does not publish.
Empty atoms fail. HTML is a derived projection of one template.
"""
from __future__ import annotations

import hashlib
import html as htmlmod
import json
import re
from pathlib import Path

STATUS_ALLOWED = {"VERIFY_PENDING", "HOLD", "QUARANTINE"}
FORBIDDEN_STATUS = {"Vigente", "publicado", "RELEASED", "ACTIVE"}
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
OPINION_IN_OUR_VOICE = ("recomenda-se que o leitor", "sugerimos", "infelizmente")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_instrument(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("kind") != "normative_instrument":
        errors.append("kind must be normative_instrument")
    if doc.get("template_id") != "norm-instrument":
        errors.append("one template only: norm-instrument")
    if doc.get("release_allowed") is not False:
        errors.append("release_allowed must be false")
    if doc.get("assigns_vigencia") is not False:
        errors.append("assigns_vigencia must be false")
    if doc.get("status") not in STATUS_ALLOWED:
        errors.append("instrument status must be VERIFY_PENDING|HOLD|QUARANTINE")
    if doc.get("status") in FORBIDDEN_STATUS:
        errors.append("instrument must not carry Vigente/publicado")
    atoms = doc.get("atoms")
    if not isinstance(atoms, list) or len(atoms) < 1:
        errors.append("empty corpus is FAIL")
        return errors
    seen = set()
    for i, atom in enumerate(atoms, start=1):
        aid = atom.get("id")
        if not aid or aid in seen:
            errors.append(f"atom {i}: id missing or duplicated")
        seen.add(aid)
        if atom.get("status") not in STATUS_ALLOWED:
            errors.append(f"{aid}: status must stay VERIFY_PENDING|HOLD|QUARANTINE")
        if atom.get("status") == "Vigente" or "Vigente" in str(atom.get("status")):
            errors.append(f"{aid}: Vigente is forbidden on process")
        text = atom.get("text") or ""
        if len(text.strip()) < 3:
            errors.append(f"{aid}: empty text")
        digest = atom.get("sha256") or ""
        if not SHA_RE.match(digest):
            errors.append(f"{aid}: sha256 required")
        elif digest != sha256_text(text):
            errors.append(f"{aid}: sha256 does not match text")
        lower = text.lower()
        for phrase in OPINION_IN_OUR_VOICE:
            if phrase in lower:
                errors.append(f"{aid}: commentary voice is forbidden; keep literal act text")
    fechamento = doc.get("fechamento") or {}
    if fechamento.get("apto") is True:
        errors.append("fechamento.apto true is forbidden while C001/C002 are open")
    return errors


def render_instrument(doc: dict) -> str:
    errors = validate_instrument(doc)
    if errors:
        raise ValueError("cannot render invalid instrument: " + "; ".join(errors))
    esc = htmlmod.escape
    rows = []
    for atom in doc["atoms"]:
        rows.append(
            "<tr>"
            f"<td><code>{esc(atom['id'])}</code></td>"
            f"<td>{esc(atom.get('type', ''))}</td>"
            f"<td>{esc(atom.get('locator', ''))}</td>"
            f"<td>{esc(atom['text'])}</td>"
            f"<td>{esc(atom['status'])}</td>"
            "</tr>"
        )
    findings = ", ".join(doc.get("fechamento", {}).get("findings") or [])
    title = esc(doc.get("title") or doc["id"])
    source = doc.get("source") or {}
    source_url = esc(source.get("url") or "")
    return f"""<!doctype html>
<html lang="pt-BR" data-cko-md="CKO-MD" data-cko-reg="CKO-REG" data-cko-norm="NIFS-900-03" data-cko-evidence="HOLD" data-cko-chain="MD / REG / Schema / Engine / Validator / Renderer / Runtime / Frontend" data-cko-template="norm-instrument">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | HOLD</title>
<meta name="description" content="Instrumento normativo em HOLD. Átomos VERIFY_PENDING. Não é vigência nem release.">
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
.hero-content{{padding:clamp(2rem,6vw,4rem);max-width:820px}}
.eyebrow{{font-weight:800;text-transform:uppercase;letter-spacing:.14em;font-size:.75rem;color:#bfdbfe}}
.hero h1{{font-family:'Nunito Sans',Inter,sans-serif;font-size:clamp(1.6rem,4vw,2.6rem);line-height:1.1;margin:.5rem 0 1rem}}
.card{{background:white;border:1px solid #dbeafe;border-radius:1rem;padding:1.25rem;margin-bottom:1rem}}
.hold{{border-left:4px solid #7c3aed;background:#f5f3ff}}.warn{{border-left:4px solid #b45309;background:#fffbeb}}
table{{width:100%;border-collapse:collapse;font-size:.88rem}}th,td{{text-align:left;padding:.45rem .3rem;border-bottom:1px solid #e2e8f0;vertical-align:top}}
.label{{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;background:#e0e7ff;color:#3730a3;padding:.25rem .5rem;border-radius:999px}}
.small{{font-size:.88rem;color:var(--cko-muted)}}code{{font-size:.86em;background:#f1f5f9;padding:.1rem .3rem;border-radius:.3rem}}
</style>
</head>
<body data-cko-status="CANDIDATE_HOLD_RELEASE" data-cko-scope="NORM_INSTRUMENT_HOLD">
<a class="skip" href="#main-content">Pular para o conteúdo principal</a>
<div id="global-header-container"></div>
<main id="main-content" class="shell">
<nav class="crumbs" aria-label="Breadcrumb" data-cko-static="breadcrumb"><a href="/">Início</a> <span aria-hidden="true">›</span> <a href="/cko-governanca.html">Governação</a> <span aria-hidden="true">›</span> <span aria-current="page">Norma HOLD</span></nav>
<section class="hero" data-cko-static="hero"><div class="hero-content">
  <div class="eyebrow">HOLD · norma · um template · {len(doc["atoms"])} átomos</div>
  <h1>{title}</h1>
  <p>Esta página é a projecção do instrumento. O original são os átomos. Não há HTML artesanal por dispositivo. Vigência automática está proibida.</p>
</div></section>
<article class="card hold">
  <span class="label">Estado</span>
  <h2>VERIFY_PENDING · fechamento.apto = false</h2>
  <p>release_allowed = false<br>assigns_vigencia = false<br>achados: {esc(findings) or "nenhum"}</p>
  <p class="small">Fonte observada no Drive (read-only). Não copiámos o HTML de 446 KB do Cofen. URL: {source_url}</p>
</article>
<article class="card">
  <h2>Átomos</h2>
  <table>
    <thead><tr><th>ID</th><th>Tipo</th><th>Local</th><th>Texto literal</th><th>Estado</th></tr></thead>
    <tbody>
{''.join(rows)}
    </tbody>
  </table>
</article>
<article class="card warn">
  <h2>O que esta página não é</h2>
  <p>Não é vigência. Não é publicação. Não é a 13.ª página institucional. Não fecha C001 nem C002. Não alimenta calculadora.</p>
</article>
</main>
<div id="footer-placeholder"></div>
<script src="/global-scripts.js" defer></script>
</body>
</html>
"""


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
