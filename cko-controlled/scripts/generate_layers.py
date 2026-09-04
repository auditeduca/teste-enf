#!/usr/bin/env python3
"""Convert the PDF 44-layer packages into the hosted final site structure.

Source of identity: the files listed in CKO Relatorio Tecnico Final Controlado
(Anexo A snapshot + ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE). CALENF paths
are runtime bindings only. Release remains HOLD / NOT_RELEASED.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cko_md_norm import MD_NORM_CHAIN
from generate_design_system import generate as generate_design_system
from generate_universal_tool import generate as generate_universal_tool
from generate_policy_master import generate as generate_policy_master
from generate_visual_assets import generate as generate_visual_assets
from generate_platform_closure import generate as generate_platform_closure
from generate_layer_policies import generate as generate_layer_policies
from generate_extraction import generate as generate_extraction
from generate_api_catalog import generate as generate_api_catalog
from generate_governed_fabric import generate as generate_governed_fabric
from cko_policy_contract import layer_policy_id

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
WAVE2 = GATE / "public"
CLOSURE = GATE / "control-plane" / "drive-html" / "CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE.html"
CANON = Path(__file__).resolve().parent / "cko_44_layers.json"
LAYERS_DIR = SITE / "data" / "cko" / "layers"
CAMADAS = SITE / "camadas"
SNAPSHOT_MANIFEST = GATE / "public" / "drive" / "ALL-SHA256-MANIFEST-20260902.json"
ZIP_CANDIDATES = [
    Path("/tmp/cko-layers"),
    GATE / "control-plane" / "layer-zips",
]
CLOSURE_SHA_PREFIX = "3dd61cd50883"
MARKER_BEGIN = "<!-- CKO-44-LAYERS:BEGIN -->"
MARKER_END = "<!-- CKO-44-LAYERS:END -->"
SNAPSHOT_RULES = (
    ("aldrete_a11y", "LYR-A11Y-001"),
    ("aldrete_asset_derivation", "LYR-DERIVE-001"),
    ("aldrete_ds", "LYR-DS-001"),
    ("aldrete_i18n", "LYR-I18N-001"),
    ("aldrete_media", "LYR-MEDIA-001"),
    ("aldrete_og", "LYR-OG-001"),
    ("aldrete_pdf", "LYR-EXPORT-001"),
    ("aldrete_routes", "LYR-ROUTE-001"),
    ("aldrete_reliability", "LYR-REL-001"),
    ("aldrete_hcd", "LYR-HCD-001"),
    ("FLASHCARDS", "LYR-LEARN-001"),
    ("CKO_DESIGN_SYSTEM", "LYR-DS-001"),
    ("CKO-POL-UT", "LYR-CLIN-CALC-001"),
    ("aldrete", "LYR-CLIN-SCALE-001"),
)

BINDINGS: dict[str, list[str]] = {
    "CKO-MD": ["data/schemas/tool.schema.json"],
    "CKO-REG": ["legislacoes.html"],
    "LYR-CLIN-CALC-001": ["data/tools", "js/calc-engine.js", "aldrete.html"],
    "LYR-CLIN-SCALE-001": ["braden.html", "escalas-de-enfermagem"],
    "LYR-CLIN-RULE-001": ["js/calc-engine.js"],
    "LYR-LIB-001": ["biblioteca.html", "biblioteca", "js/modules/data/biblioteca.json"],
    "LYR-MED-001": ["medicamentos.html"],
    "LYR-LAB-001": ["exames_laboratoriais.html"],
    "LYR-ANAT-001": ["album_enfermagem.html"],
    "LYR-COND-001": ["lista-de-doencas-de-notificacao-compulsoria.html"],
    "LYR-PROC-001": ["protocolos.html"],
    "LYR-TERM-001": ["nanda.html"],
    "LYR-EDU-001": ["concurso_publico/index.html"],
    "LYR-REF-001": ["downloads.html", "biblioteca.html"],
    "LYR-CONTENT-001": ["biblioteca.html", "biblioteca"],
    "LYR-LEARN-001": ["flashcards.html", "js/cko-flashcards-srs.js", "data/flashcards-deck.json"],
    "LYR-PAGE-TPL-001": ["js/cko-page-templates.js", "data/cko-page-templates.json"],
    "LYR-DOC-TPL-001": ["data/cko-page-templates.json"],
    "LYR-MEDIA-001": ["img"],
    "LYR-DERIVE-001": ["scripts/generate_tool_page.py"],
    "LYR-HCD-001": ["partials/header.html"],
    "LYR-A11Y-001": ["acessibilidade.html"],
    "LYR-DS-001": [
        "global-styles.css",
        "public/output.css",
        "css/cko-ds-tokens.css",
        "css/cko-ds.css",
        "js/cko-ds-render.js",
        "data/cko/design-system.json",
    ],
    "LYR-UI-001": [
        "partials/header.html",
        "js/partials-loader.js",
        "css/cko-ds.css",
        "js/cko-ds-render.js",
    ],
    "LYR-PRV-001": ["privacidade.html"],
    "LYR-SEC-001": ["firebase.json"],
    "LYR-ROUTE-001": ["index.html", "sitemap.xml"],
    "LYR-SEO-001": ["sitemap.xml"],
    "LYR-OG-001": ["index.html"],
    "LYR-SEM-001": ["index.html"],
    "LYR-I18N-001": ["i18n"],
    "LYR-SEARCH-001": ["js/cko-global-search.js"],
    "LYR-REC-001": ["js/profile-personalization.js"],
    "LYR-USERSTATE-001": ["js/profile-personalization.js"],
    "LYR-ANL-001": ["global-scripts.js"],
    "LYR-PERF-001": ["public/output.css"],
    "LYR-REL-001": ["js/calc-engine.js"],
    "LYR-OBS-001": ["data/cko/governance.json"],
    "LYR-SUS-001": ["tecnologiaverde.html"],
    "LYR-RND-001": ["scripts/generate_tool_page.py"],
    "LYR-RUN-001": ["js/calc-engine.js", "aldrete.html"],
    "LYR-EXPORT-001": ["asa.html"],
    "LYR-PUB-001": ["notificacoes-legais.html"],
    "LYR-MON-001": ["data/cko/governance.json"],
}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def closure_layer_ids() -> list[str]:
    html = CLOSURE.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</p>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    ids = re.findall(r"\b(?:CKO-MD|CKO-REG|LYR-[A-Z0-9-]+)\b", text)
    out: list[str] = []
    for layer_id in ids:
        if layer_id not in out:
            out.append(layer_id)
    return out


def resolve_runtime(rel: str) -> Path:
    if rel == "firebase.json":
        return SITE.parent / "firebase.json"
    return SITE / rel


def find_zip(layer_id: str) -> Path | None:
    for root in ZIP_CANDIDATES:
        candidate = root / f"{layer_id}.zip"
        if candidate.is_file():
            return candidate
    return None


def materialize_layer(row: dict) -> dict:
    layer_id = row["id"]
    dest = LAYERS_DIR / layer_id
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    payload = dest / "payload"
    payload.mkdir(parents=True, exist_ok=True)

    runtime_paths = BINDINGS[layer_id]
    missing = [p for p in runtime_paths if not resolve_runtime(p).exists()]
    zip_path = find_zip(layer_id)
    zip_verified = False
    zip_sha = None
    extracted = []
    if zip_path is not None:
        raw = zip_path.read_bytes()
        zip_sha = hashlib.sha256(raw).hexdigest()
        zip_verified = zip_sha == row["sha256"] and len(raw) == int(row["bytes"])
        if zip_verified:
            hosted_zip = dest / "package.zip"
            hosted_zip.write_bytes(raw)
            if zipfile.is_zipfile(hosted_zip):
                with zipfile.ZipFile(hosted_zip) as zf:
                    zf.extractall(dest / "package")
                    extracted = zf.namelist()

    manifest = {
        "id": layer_id,
        "name": row["name"],
        "artifact": row["artifact"],
        "version": row["version"],
        "seq": row["seq"],
        "classified_sha256": row["sha256"],
        "drive_id": row["drive_id"],
        "bytes": row["bytes"],
        "readback": row["readback"],
        "holds_n": row["holds_n"],
        "release": "HOLD / NOT_RELEASED",
        "operational": "NOT_ASSERTED",
        "published": False,
        "source": "ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE",
        "closure_sha256_prefix": CLOSURE_SHA_PREFIX,
        "runtime_paths": runtime_paths,
        "zip_verified": zip_verified,
    }
    write_json(dest / "FINAL_MANIFEST.json", manifest)
    write_json(
        dest / "SHA256SUMS.json",
        {
            "classified_zip_sha256": row["sha256"],
            "hosted_zip_sha256": zip_sha,
            "zip_verified": zip_verified,
            "bytes": row["bytes"],
        },
    )
    write_json(
        dest / "lineage.json",
        {
            "work_item": "WI-CROSS-GLOBAL-44-LAYER-FANIN-20260902",
            "artifact": row["artifact"],
            "version": row["version"],
            "drive_id": row["drive_id"],
            "closure": "CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE-v1.0.0",
        },
    )
    write_json(
        dest / "holds.json",
        {
            "n": row["holds_n"],
            "release": "HOLD / NOT_RELEASED",
            "pending_is_not_ack": True,
        },
    )
    (payload / "README.txt").write_text(
        (
            f"Layer {layer_id} — {row['name']}\n"
            f"Classified package from ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE.\n"
            f"Release: HOLD / NOT_RELEASED. Operational: NOT_ASSERTED.\n"
            f"CALENF runtime: {', '.join(runtime_paths)}\n"
        ),
        encoding="utf-8",
    )
    write_json(
        payload / "runtime.json",
        {
            "paths": runtime_paths,
            "missing": missing,
            "present": len(missing) == 0,
            "operational": "NOT_ASSERTED",
            "published": False,
            "governed_by": {
                "graph": "js/knowledge-graph.js",
                "twin": "B5",
                "agentic": "B1",
                "nursePalm": "B10",
                "master_data": "CKO-MD",
                "regulatory": "CKO-REG",
                "evidence": "HOLD",
            },
            "master_data": "CKO-MD",
            "regulatory": "CKO-REG",
            "norm": "NIFS-900-03",
            "evidence": {
                "status": "HOLD",
                "no_fact_without_evidence": True,
                "discovery_is_not_evidence": True,
            },
        },
    )
    href = f"camadas/{layer_id}/"
    write_layer_page(row, runtime_paths, zip_verified, href)
    present = (
        len(missing) == 0
        and zip_verified
        and (dest / "package.zip").is_file()
        and (dest / "package" / "FINAL_MANIFEST.json").is_file()
        and (CAMADAS / layer_id / "index.html").is_file()
    )
    return {
        "seq": row["seq"],
        "id": layer_id,
        "name": row["name"],
        "artifact": row["artifact"],
        "version": row["version"],
        "sha256": row["sha256"],
        "drive_id": row["drive_id"],
        "bytes": row["bytes"],
        "readback": row["readback"],
        "holds_n": row["holds_n"],
        "release": "HOLD / NOT_RELEASED",
        "operational": "NOT_ASSERTED",
        "published": False,
        "present": present,
        "runtime_paths": runtime_paths,
        "package": f"data/cko/layers/{layer_id}/",
        "href": f"/{href}",
        "zip_verified": zip_verified,
        "extracted_n": len(extracted),
        "missing_runtime": missing,
        "governed_by": {
            "graph": "js/knowledge-graph.js",
            "twin": "B5",
            "agentic": "B1",
            "nursePalm": "B10",
            "master_data": "CKO-MD",
            "regulatory": "CKO-REG",
            "evidence": "HOLD",
        },
        "master_data": "CKO-MD",
        "regulatory": "CKO-REG",
        "norm": "NIFS-900-03",
        "evidence": {
            "status": "HOLD",
            "no_fact_without_evidence": True,
            "discovery_is_not_evidence": True,
        },
        "semantic": {
            "CKO-MD": "master-data",
            "CKO-REG": "regulatory",
            "LYR-CONTENT-001": "content",
            "LYR-EDU-001": "educational",
            "LYR-LEARN-001": "learning",
        }.get(layer_id),
        "policy_id": layer_policy_id(layer_id),
        "specializes": "POL-CKO-POLICY-MASTER-CONTRACT-1.0.0",
        "policy_status": "CONTROLLED_LAYER_HOLD",
    }


def map_snapshot_layer(path: str) -> str:
    blob = path.replace("\\", "/").lower()
    for needle, layer_id in SNAPSHOT_RULES:
        if needle.lower() in blob:
            return layer_id
    return "LYR-CLIN-SCALE-001"


def write_snapshot_index() -> dict:
    data = json.loads(SNAPSHOT_MANIFEST.read_text(encoding="utf-8"))
    files = data.get("files") or []
    mapped = []
    counts: dict[str, int] = {}
    for row in files:
        path = row["path"]
        layer_id = map_snapshot_layer(path)
        counts[layer_id] = counts.get(layer_id, 0) + 1
        mapped.append(
            {
                "path": path,
                "sha256": row["sha256"],
                "bytes": row["bytes"],
                "layer_id": layer_id,
            }
        )
    catalog = {
        "id": "CKO-PDF-ANEXO-A-SNAPSHOT-1.0.0",
        "kind": "pdf-anexo-a-snapshot",
        "source": "ALL-SHA256-MANIFEST-20260902.json",
        "file_count": len(mapped),
        "gold": 449,
        "release": "HOLD / NOT_RELEASED",
        "converted_to": "camadas/",
        "layer_file_counts": counts,
        "files": mapped,
    }
    write_json(SITE / "data" / "cko" / "snapshot-index.json", catalog)
    write_json(WAVE2 / "data" / "snapshot-index.json", catalog)
    if catalog["file_count"] != 449:
        raise SystemExit(f"Anexo A snapshot must be 449 files, got {catalog['file_count']}")
    return catalog


def write_layer_page(row: dict, runtime_paths: list[str], zip_verified: bool, href: str) -> None:
    dest = CAMADAS / row["id"]
    dest.mkdir(parents=True, exist_ok=True)
    runtime_links = "".join(
        f'<li><a href="/{p}">{p}</a></li>' for p in runtime_paths
    )
    render_mode = {
        "LYR-DS-001": ("catalog", "/data/cko/design-system.json"),
        "LYR-UI-001": ("states", "/data/cko/design-system.json"),
        "LYR-PAGE-TPL-001": ("templates", "/data/cko/design-system.json"),
        "LYR-CLIN-CALC-001": ("universal-tool", "/data/cko/universal-tool.json"),
    }.get(row["id"])
    render_block = ""
    if render_mode:
        mode, src = render_mode
        render_block = f"""
<section class="cko-ds-section" aria-label="Catálogo renderizado">
  <div id="cko-ds-root" data-cko-ds-render="{mode}" data-cko-ds-src="{src}"></div>
</section>
<script type="module" src="/js/cko-ds-render.js?v=pmc-1"></script>
"""
    identity_link = (
        '<p><a class="cko-ds-link" href="/cko-identidade.html">Manual de identidade v10 no cluster</a> · '
        '<a class="cko-ds-link" href="/escala-padrao.html">Espécime de escala</a></p>'
        if row["id"] == "LYR-DS-001"
        else ""
    )
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{row['id']} — {row['name']} | Calculadoras de Enfermagem</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1A3E74">
<link rel="stylesheet" href="/global-styles.css">
<link rel="stylesheet" href="/css/pages/cart-emergencia.css">
<link rel="stylesheet" href="/css/pages/cko-page-shell.css">
<link rel="stylesheet" href="/css/cko-ds.css">
<script src="/global-scripts.js" defer></script>
<script src="/lang-selector.js" defer></script>
</head>
<body class="cko-ds-body cko-cart-page" data-cko-status="CANDIDATE_HOLD_RELEASE" data-cko-layer="{row['id']}" data-cko-release="HOLD_NOT_RELEASED" data-cko-ds="1">
<a class="cko-ds-skip" href="#main-content">Pular para o conteúdo principal</a>
<div id="global-header-container"></div>
<div id="language-selector-placeholder"></div>
<main id="main-content" class="cko-ds-page">
<nav class="cko-ds-crumbs" aria-label="Breadcrumb"><a href="/">Início</a> › <a href="/ecossistema.html">Ecossistema</a> › <a href="/camadas/">Camadas</a> › <span aria-current="page">{row['id']}</span></nav>
<article class="cko-ds-card cko-ds-card--hold">
  <p class="cko-ds-badge cko-ds-badge--hold">Camada {row['seq']} · HOLD / NOT_RELEASED</p>
  <h1 class="cko-ds-title">{row['name']}</h1>
  <p>Pacote classificado do PDF <code>{row['artifact']}</code> convertido para a estrutura final do site. SHA-256 <code>{row['sha256'][:16]}…</code>. Zip verificado: <strong>{'sim' if zip_verified else 'não'}</strong>. Nurse-PaLM operacional: <strong>NOT_ASSERTED</strong>.</p>
  <p>Runtime CALENF (base de implementação, não a estrutura final):</p>
  <ul>{runtime_links}</ul>
  {identity_link}
  <p><a class="cko-ds-link" href="/data/cko/layers/{row['id']}/package.zip">Pacote original do PDF</a> · <a class="cko-ds-link" href="/data/cko/layers/{row['id']}/package/FINAL_MANIFEST.json">Manifesto original</a></p>
</article>
{render_block}
</main>
<div id="footer-placeholder"></div>
</body>
</html>
"""
    (dest / "index.html").write_text(html, encoding="utf-8")


def write_camadas_index(catalog: dict) -> None:
    CAMADAS.mkdir(parents=True, exist_ok=True)
    items = "".join(
        f'<li><a href="/camadas/{layer["id"]}/"><code>{layer["id"]}</code> — {layer["name"]}</a></li>'
        for layer in catalog["layers"]
    )
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>44 camadas do PDF | Calculadoras de Enfermagem</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1A3E74">
<link rel="stylesheet" href="/global-styles.css">
<link rel="stylesheet" href="/css/pages/cart-emergencia.css">
<link rel="stylesheet" href="/css/pages/cko-page-shell.css">
<link rel="stylesheet" href="/css/cko-ds.css">
<script src="/global-scripts.js" defer></script>
<script src="/lang-selector.js" defer></script>
</head>
<body class="cko-ds-body cko-cart-page" data-cko-status="CANDIDATE_HOLD_RELEASE" data-cko-layers="44" data-cko-ds="1">
<a class="cko-ds-skip" href="#main-content">Pular para o conteúdo principal</a>
<div id="global-header-container"></div>
<div id="language-selector-placeholder"></div>
<main id="main-content" class="cko-ds-page">
<nav class="cko-ds-crumbs" aria-label="Breadcrumb"><a href="/">Início</a> › <a href="/ecossistema.html">Ecossistema</a> › <span>Camadas</span></nav>
<div id="cko-ds-root" data-cko-ds-render="layers" data-cko-ds-src="/data/cko/design-system.json" data-cko-layers-src="/data/cko/layers.json"></div>
<noscript>
<h1>44 camadas classificadas do PDF</h1>
<p>Estrutura final convertida dos pacotes do relatório técnico. Cobertura <strong>44/44</strong>. Estado: <strong>HOLD / NOT_RELEASED</strong>.</p>
<ol>{items}</ol>
</noscript>
</main>
<div id="footer-placeholder"></div>
<script type="module" src="/js/cko-ds-render.js?v=pmc-1"></script>
</body>
</html>
"""
    (CAMADAS / "index.html").write_text(html, encoding="utf-8")


def layers_section_html(catalog: dict) -> str:
    rows = []
    for layer in catalog["layers"]:
        sha = layer["sha256"][:12]
        runtime = ", ".join(layer["runtime_paths"][:2])
        rows.append(
            "<tr>"
            f"<td>{layer['seq']}</td>"
            f"<td><a href=\"/camadas/{layer['id']}/\"><code data-layer-id=\"{layer['id']}\">{layer['id']}</code></a></td>"
            f"<td>{layer['name']}</td>"
            f"<td><code>{sha}…</code></td>"
            f"<td>{runtime}</td>"
            f"<td>{layer['holds_n']}</td>"
            f"<td>{layer['release']}</td>"
            "</tr>"
        )
    ids_list = "".join(f"<li><code>{layer['id']}</code> — {layer['name']}</li>" for layer in catalog["layers"])
    return f"""{MARKER_BEGIN}
<article class="card hold" id="cko-md-norm-evidence" data-cko-md="CKO-MD" data-cko-reg="CKO-REG" data-cko-norm="NIFS-900-03" data-cko-evidence="HOLD" data-cko-chain="MD / REG / Schema / Engine / Validator / Renderer / Runtime / Frontend">
  <span class="label">Evidência e norma</span>
  <h2>Master data → norma → evidência → frontend</h2>
  <p>A amarração parte de <strong>CKO-MD</strong>
  (<code>ART-CKO-MASTER-DATA-FINAL-CONTROLLED</code>, 2496 campos classificados)
  para <strong>CKO-REG</strong> (10913 amarrações normativas classificadas),
  schema, engine, validator, renderer, runtime e frontend.
  Cada objeto tem evidência <code>HOLD</code>.
  <strong>NO_FACT_WITHOUT_EVIDENCE</strong>. Discovery ≠ evidence. PENDING ≠ ACK.
  Contagens 2496/10913 permanecem classificadas — não materializadas campo a campo.
  Estado: <strong>HOLD / NOT_RELEASED</strong>.</p>
  <ol class="list-clean">
    <li>MD</li><li>REG</li><li>Schema</li><li>Engine</li>
    <li>Validator</li><li>Renderer</li><li>Runtime</li><li>Frontend</li>
  </ol>
</article>
<article class="card hold" id="cko-governed-runtime" data-cko-graph="js/knowledge-graph.js" data-cko-twin="B5" data-cko-agentic="B1" data-cko-nursepalm="B10">
  <span class="label">Governança</span>
  <h2>Grafo, digital twin, IA agêntica e Nurse-PaLM</h2>
  <p>Tudo no runtime CALENF é governado por <strong>grafo</strong> (<code>js/knowledge-graph.js</code>),
  <strong>digital twin</strong> B5 NIFS-600-15, <strong>IA agêntica</strong> B1
  (Maker ≠ Checker ≠ Auditor) e <strong>Nurse-PaLM</strong> B10.
  Twin permanece <code>observed:false</code> / <code>deployed:false</code>.
  Nurse-PaLM e B1 permanecem <strong>NOT_ASSERTED</strong>. Fan-in B9:
  <strong>HOLD / NOT_RELEASED</strong>.</p>
  <ul class="list-clean">
    <li>Content = conhecimento canônico e projeções governadas.</li>
    <li>Educational = motor pedagógico derivado de Content.</li>
    <li>Learning = Agent Continuous Learning Engine (o rótulo Flashcards/Quizzes é linhagem).</li>
    <li>CKO-MD e CKO-REG: freeze FROZEN do fan-in global do PDF.</li>
    <li>PENDING ≠ ACK. Sem homologação clínica. Sem reexecução das 44 camadas.</li>
  </ul>
</article>
<article class="card hold" id="cko-44-layers" data-cko-layers="44" data-cko-layers-release="HOLD_NOT_RELEASED">
  <span class="label">Camadas horizontais</span>
  <h2>44 camadas classificadas do PDF inicial</h2>
  <p>O site converte os <strong>arquivos do PDF</strong> — pacotes das 44 camadas
  e o inventário Anexo A de 449 arquivos — para a estrutura final em
  <a href="/camadas/"><code>/camadas/</code></a>.
  Artefato <code>ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE</code>
  (SHA prefixo <code>{CLOSURE_SHA_PREFIX}</code>). Cobertura <strong>44/44</strong>.
  A árvore CALENF é a base de implementação. Estado:
  <strong>HOLD / NOT_RELEASED</strong>. Nurse-PaLM operacional permanece
  <strong>NOT_ASSERTED</strong>. Nenhuma camada está publicada.</p>
  <p class="kpi">44/44</p>
  <p class="small">Fonte: fechamento técnico + global fan-in assurance. Maker ≠ Checker ≠ Auditor.</p>
  <div style="overflow:auto">
  <table class="small" style="width:100%;border-collapse:collapse">
    <thead><tr>
      <th align="left">seq</th><th align="left">id</th><th align="left">camada</th>
      <th align="left">sha256</th><th align="left">runtime CALENF</th>
      <th align="left">holds</th><th align="left">release</th>
    </tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  </div>
  <h3>Identificadores canônicos</h3>
  <ol class="list-clean">{ids_list}</ol>
</article>
<article class="card hold" id="cko-assurance-cascade" data-cko-cascade="policy-as-code" data-cko-release="HOLD_NOT_RELEASED">
  <span class="label">Cascata de garantia</span>
  <h2>policy-as-code → schemas → graph constraints → CI gates → runtime assertions → automatic evidence</h2>
  <p>Tudo inicia em <strong>policy-as-code</strong>. O estágio seguinte só corre se o predecessor PASS.
  Regras: cobertura = 100% do universo conhecido; evidence coverage = 100%;
  test pass = 100% dos testes definidos; incerteza residual = <code>X</code>;
  universo desconhecido = explicitado. Pacote de evidência em
  <a href="/data/cko/cascade/"><code>/data/cko/cascade/</code></a>.
  Estado: <strong>HOLD / NOT_RELEASED</strong>. <code>release_allowed: false</code>.
  Policy neste frontend = <strong>CKO-MD</strong> + <strong>CKO-REG</strong> até o stamp
  (<code>MD → REG → Schema → Engine → Validator → Renderer → Runtime → Frontend</code>).
  Decisões humanas permanecem <code>HOLD_HUMAN_NON_BLOCKING</code>: não bloqueiam inspect/CI; continuam a negar release.</p>
  <ol class="list-clean">
    <li>RDF/OWL + SHACL, ontologia formal, grafo temporal e de propriedades, constraints e reasoning.</li>
    <li>Verificação: property-based, mutation testing, contract testing, fuzzing, model checking.</li>
    <li>Evaluation science: golden set, precisão/recall, calibração, matriz de confusão, kappa, adversarial, drift (PSI).</li>
    <li>Sistemas distribuídos: EVENT → CHECKPOINT → ORQUESTRADOR, filas, idempotência, retries, DLQ, sagas, at-least-once.</li>
  </ol>
  <p class="small">Nurse-PaLM operacional permanece NOT_ASSERTED. Métricas sintéticas não são homologação clínica. Exactly-once não é afirmado.</p>
</article>
{MARKER_END}
"""


def inject_ecossistema(catalog: dict) -> None:
    section = layers_section_html(catalog)
    src = WAVE2 / "ecossistema.html"
    html = src.read_text(encoding="utf-8")
    if MARKER_BEGIN in html and MARKER_END in html:
        before, rest = html.split(MARKER_BEGIN, 1)
        _, after = rest.split(MARKER_END, 1)
        html = before + section + after
    else:
        needle = '<div class="grid">'
        if needle not in html:
            raise SystemExit("ecossistema.html missing grid landmark")
        html = html.replace(needle, section + "\n" + needle, 1)
    src.write_text(html, encoding="utf-8")
    shutil.copy2(src, SITE / "ecossistema.html")


def generate() -> dict:
    generate_design_system()
    generate_universal_tool()
    generate_policy_master()
    generate_visual_assets()
    generate_platform_closure()
    generate_layer_policies()
    generate_extraction()
    generate_api_catalog()
    generate_governed_fabric()
    if not CLOSURE.is_file():
        raise SystemExit(f"closure HTML missing: {CLOSURE}")
    rows = json.loads(CANON.read_text(encoding="utf-8"))
    if len(rows) != 44:
        raise SystemExit(f"canonical table must have 44 rows, got {len(rows)}")
    html_ids = closure_layer_ids()
    json_ids = [r["id"] for r in rows]
    if html_ids != json_ids:
        raise SystemExit(f"closure HTML ids != canonical table: {html_ids} vs {json_ids}")
    missing_bindings = [r["id"] for r in rows if r["id"] not in BINDINGS]
    if missing_bindings:
        raise SystemExit("missing bindings: " + ",".join(missing_bindings))
    LAYERS_DIR.mkdir(parents=True, exist_ok=True)
    layers = [materialize_layer(row) for row in rows]
    absent = [l["id"] for l in layers if not l["present"]]
    if absent:
        raise SystemExit("layers missing runtime: " + ",".join(absent))
    unverified = [l["id"] for l in layers if not l["zip_verified"]]
    if unverified:
        raise SystemExit("PDF layer zips not verified: " + ",".join(unverified))
    snapshot = write_snapshot_index()
    catalog = {
        "id": "CKO-44-LAYER-SITE-1.0.0",
        "kind": "cko-44-layers",
        "root": "policy-as-code",
        "source": "ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE",
        "version_id": "OV-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE-1.0.0",
        "closure_sha256_prefix": CLOSURE_SHA_PREFIX,
        "count": 44,
        "gold": "44/44",
        "release": "HOLD / NOT_RELEASED",
        "operational": "NOT_ASSERTED",
        "published": False,
        "pending_is_not_ack": True,
        "reexecution": False,
        "page": "camadas/index.html",
        "listing_page": "ecossistema.html",
        "governed_by": {
            "graph": "js/knowledge-graph.js",
            "twin": "B5",
            "agentic": "B1",
            "nursePalm": "B10",
            "master_data": "CKO-MD",
            "regulatory": "CKO-REG",
            "evidence": "HOLD",
        },
        "master_data_to_frontend": MD_NORM_CHAIN,
        "semantic_controls": {
            "content": "canonical knowledge/content and governed projections",
            "educational": "pedagogical projection engine derived from Content",
            "learning": "Agent Continuous Learning Engine; historical label Flashcards / Questions / Quizzes is lineage only",
            "l1_l4_char_limits": "NOT_ASSERTED",
        },
        "agentic": {
            "independence": "maker!=checker!=auditor",
            "operational": "NOT_ASSERTED",
        },
        "md_freeze": "FROZEN",
        "reg_freeze": "FROZEN",
        "policy": "POL-CKO-LAYER-CATALOG-1.0.0",
        "specializes": "POL-CKO-POLICY-MASTER-CONTRACT-1.0.0",
        "policy_status": "CONTROLLED_LAYER_HOLD",
        "layers": layers,
        "zip_verified_n": sum(1 for l in layers if l["zip_verified"]),
        "snapshot_files": snapshot["file_count"],
    }
    write_json(SITE / "data" / "cko" / "layers.json", catalog)
    write_json(WAVE2 / "data" / "layers.json", catalog)
    write_camadas_index(catalog)
    inject_ecossistema(catalog)
    print(
        json.dumps(
            {
                "layers": catalog["count"],
                "present": sum(1 for l in layers if l["present"]),
                "zip_verified_n": catalog["zip_verified_n"],
                "snapshot_files": catalog["snapshot_files"],
                "release": catalog["release"],
            },
            ensure_ascii=False,
        )
    )
    return catalog


if __name__ == "__main__":
    generate()
