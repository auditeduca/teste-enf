#!/usr/bin/env python3
"""Materialize the 44 classified horizontal layers onto the CALENF site.

Source of identity: ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE (Drive HTML copy,
immutable). Each layer is bound to an existing CALENF runtime path. Release
remains HOLD / NOT_RELEASED. Nurse-PaLM and publication stay unasserted.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
WAVE2 = GATE / "public"
CLOSURE = GATE / "control-plane" / "drive-html" / "CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE.html"
CANON = Path(__file__).resolve().parent / "cko_44_layers.json"
LAYERS_DIR = SITE / "data" / "cko" / "layers"
ZIP_CANDIDATES = [
    Path("/tmp/cko-layers"),
    GATE / "control-plane" / "layer-zips",
]
CLOSURE_SHA_PREFIX = "3dd61cd50883"
MARKER_BEGIN = "<!-- CKO-44-LAYERS:BEGIN -->"
MARKER_END = "<!-- CKO-44-LAYERS:END -->"

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
    "LYR-DS-001": ["global-styles.css", "public/output.css"],
    "LYR-UI-001": ["partials/header.html", "js/partials-loader.js"],
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
            },
        },
    )
    present = len(missing) == 0 and (dest / "FINAL_MANIFEST.json").is_file()
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
        "zip_verified": zip_verified,
        "extracted_n": len(extracted),
        "missing_runtime": missing,
        "governed_by": {
            "graph": "js/knowledge-graph.js",
            "twin": "B5",
            "agentic": "B1",
            "nursePalm": "B10",
        },
        "semantic": {
            "CKO-MD": "master-data",
            "CKO-REG": "regulatory",
            "LYR-CONTENT-001": "content",
            "LYR-EDU-001": "educational",
            "LYR-LEARN-001": "learning",
        }.get(layer_id),
    }


def layers_section_html(catalog: dict) -> str:
    rows = []
    for layer in catalog["layers"]:
        sha = layer["sha256"][:12]
        runtime = ", ".join(layer["runtime_paths"][:2])
        rows.append(
            "<tr>"
            f"<td>{layer['seq']}</td>"
            f"<td><code data-layer-id=\"{layer['id']}\">{layer['id']}</code></td>"
            f"<td>{layer['name']}</td>"
            f"<td><code>{sha}…</code></td>"
            f"<td>{runtime}</td>"
            f"<td>{layer['holds_n']}</td>"
            f"<td>{layer['release']}</td>"
            "</tr>"
        )
    ids_list = "".join(f"<li><code>{layer['id']}</code> — {layer['name']}</li>" for layer in catalog["layers"])
    return f"""{MARKER_BEGIN}
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
  <p>O site hospeda as <strong>44 camadas horizontais</strong> do artefato
  <code>ART-CKO-44-LAYER-FINAL-TECHNICAL-CLOSURE</code>
  (SHA prefixo <code>{CLOSURE_SHA_PREFIX}</code>). Cobertura <strong>44/44</strong>.
  Cada camada está no grafo, projetada no twin, ligada a B1 e a B10, e faz fan-in a B9.
  Estado: <strong>HOLD / NOT_RELEASED</strong>. Nurse-PaLM operacional permanece
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
        "page": "ecossistema.html",
        "governed_by": {
            "graph": "js/knowledge-graph.js",
            "twin": "B5",
            "agentic": "B1",
            "nursePalm": "B10",
        },
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
        "layers": layers,
        "zip_verified_n": sum(1 for l in layers if l["zip_verified"]),
    }
    write_json(SITE / "data" / "cko" / "layers.json", catalog)
    write_json(WAVE2 / "data" / "layers.json", catalog)
    inject_ecossistema(catalog)
    print(
        json.dumps(
            {
                "layers": catalog["count"],
                "present": sum(1 for l in layers if l["present"]),
                "zip_verified_n": catalog["zip_verified_n"],
                "release": catalog["release"],
            },
            ensure_ascii=False,
        )
    )
    return catalog


if __name__ == "__main__":
    generate()
