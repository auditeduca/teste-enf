#!/usr/bin/env python3
"""Build a 100% client-side HOLD preview (localStorage) of the CALENF site.

Opens as a single HTML file — no deploy, no server required after the file
is downloaded. Seeds localStorage with the snapshot and renders homepage,
institutional pages, calculator canaries and the 44 layers in site chrome.

Does not close B9. Does not authorize production release.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
OUT_HTML = SITE / "cko-hold-preview.html"
OUT_JSON = SITE / "data" / "cko" / "hold-preview.json"

INSTITUTIONAL = [
    ("home", "/", "Início", "index.html"),
    ("missao", "/missao.html", "Sobre nós", "missao.html"),
    ("objetivo", "/objetivo.html", "Objetivos", "objetivo.html"),
    ("ecossistema", "/ecossistema.html", "Ecossistema", "ecossistema.html"),
    ("camadas", "/camadas/", "44 camadas", "camadas/index.html"),
    ("mapa", "/mapa-do-site.html", "Mapa do site", "mapa-do-site.html"),
    ("acessibilidade", "/acessibilidade.html", "Acessibilidade", "acessibilidade.html"),
    ("tecnologiaverde", "/tecnologiaverde.html", "Sustentabilidade", "tecnologiaverde.html"),
    ("privacidade", "/privacidade.html", "Privacidade", "privacidade.html"),
    ("politica", "/politica-editorial.html", "Política editorial", "politica-editorial.html"),
    ("fale", "/fale.html", "Fale conosco", "fale.html"),
]
TOOLS = [
    ("aldrete", "/aldrete.html", "aldrete.html"),
    ("imc", "/imc.html", "imc.html"),
    ("gotejamento", "/gotejamento.html", "gotejamento.html"),
    ("braden", "/braden.html", "braden.html"),
    ("news", "/news.html", "news.html"),
    ("biblioteca", "/biblioteca.html", "biblioteca.html"),
]
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
CHIP_RE = re.compile(
    r'href="escalas-de-enfermagem/([^"/]+)(?:/index\.html)?"[^>]*>([^<]+)</a>',
    re.I,
)
HUB_TOOL_RE = re.compile(
    r'href="(?:\.\./)+([a-z0-9-]+)\.html"[^>]*>.*?<strong[^>]*>([^<]+)</strong>',
    re.I | re.S,
)


def text_of(html_fragment: str) -> str:
    return re.sub(r"<[^>]+>", "", html_fragment).strip()


def first_h1(path: Path) -> str:
    if not path.is_file():
        return path.stem
    m = H1_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    return text_of(m.group(1)) if m else path.stem


def lead_paragraph(path: Path) -> str:
    if not path.is_file():
        return ""
    html = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<p class=\"hero[^\"]*\"[^>]*>(.*?)</p>|<p>(.{40,280})</p>", html, re.I | re.S)
    return text_of(m.group(1) or m.group(2) or "") if m else ""


def build_snapshot() -> dict:
    layers_doc = json.loads((SITE / "data" / "cko" / "layers.json").read_text(encoding="utf-8"))
    index_html = (SITE / "index.html").read_text(encoding="utf-8", errors="replace")
    chips = [{"id": href.strip("/"), "label": label.strip()} for href, label in CHIP_RE.findall(index_html)]
    specialties = []
    hubs = SITE / "escalas-de-enfermagem"
    if hubs.is_dir():
        for hub in sorted(hubs.iterdir()):
            page = hub / "index.html"
            if not page.is_file():
                continue
            body = page.read_text(encoding="utf-8", errors="replace")
            tools = [
                {"id": tid, "title": title.strip()}
                for tid, title in HUB_TOOL_RE.findall(body)[:8]
            ]
            specialties.append(
                {
                    "id": hub.name,
                    "href": f"/escalas-de-enfermagem/{hub.name}/",
                    "label": first_h1(page),
                    "title": first_h1(page),
                    "lead": lead_paragraph(page),
                    "tools": tools,
                }
            )
    pages = []
    for pid, href, label, file in INSTITUTIONAL:
        src = SITE / file
        pages.append(
            {
                "id": pid,
                "href": href,
                "label": label,
                "title": first_h1(src) if pid != "home" else "Calculadoras de Enfermagem",
                "lead": lead_paragraph(src)
                if pid != "home"
                else "Ferramentas, escalas, protocolos e recursos digitais para apoiar o estudo e a prática da enfermagem.",
                "kind": "institutional",
            }
        )
    tools = []
    for pid, href, file in TOOLS:
        src = SITE / file
        tools.append(
            {
                "id": pid,
                "href": href,
                "label": first_h1(src),
                "title": first_h1(src),
                "kind": "tool",
                "file": file,
            }
        )
    layers = [
        {
            "id": row["id"],
            "name": row.get("name") or row["id"],
            "seq": row.get("seq"),
            "holds_n": row.get("holds_n", 0),
            "release": row.get("release", "HOLD / NOT_RELEASED"),
        }
        for row in layers_doc["layers"]
    ]
    return {
        "id": "CKO-HOLD-PREVIEW-1.0.0",
        "kind": "hold-localstorage-preview",
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "deploy": False,
        "render": "100% client / localStorage",
        "policy": "CKO-MD + CKO-REG",
        "home": {
            "eyebrow": "Plataforma Clínica",
            "title": "Calculadoras de Enfermagem",
            "lead": "Ferramentas, escalas, protocolos e recursos digitais para apoiar o estudo e a prática da enfermagem, com fontes e contexto apresentados em cada conteúdo.",
            "library": "Acervo em expansão",
            "chips": chips or [
                {"id": "centro-cirurgico", "label": "Centro Cirúrgico"},
                {"id": "dor", "label": "Dor"},
            ],
        },
        "pages": pages,
        "tools": tools,
        "specialties": specialties,
        "layers": layers,
        "layer_count": len(layers),
    }


HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Preview HOLD · Calculadoras de Enfermagem</title>
<style>
:root { --navy:#1A3E74; --navy2:#1E4D8C; --navy3:#163269; --ice:#e0e7ff; --bg:#f8fafc; --text:#1f2937; --muted:#475569; }
* { box-sizing:border-box; }
body { margin:0; font-family: Inter, system-ui, Segoe UI, sans-serif; background:var(--bg); color:var(--text); }
a { color:var(--navy); }
header { background:var(--navy); color:#fff; }
.top { display:flex; justify-content:space-between; align-items:center; padding:.55rem 1.25rem; font-size:.78rem; background:#12305c; }
.holdchip { background:#fde68a; color:#78350f; font-weight:800; font-size:.68rem; letter-spacing:.06em; padding:.2rem .5rem; border-radius:999px; }
nav.main { display:flex; flex-wrap:wrap; gap:.75rem 1.1rem; padding:.85rem 1.25rem; align-items:center; }
nav.main a { color:#fff; text-decoration:none; font-weight:700; font-size:.92rem; }
nav.main a.brand { font-size:1.05rem; }
main { width:min(1120px, calc(100% - 2rem)); margin:1.25rem auto 3rem; }
.hero { background:linear-gradient(135deg,var(--navy),var(--navy2) 60%,var(--navy3)); color:#fff; border-radius:1.4rem; padding:clamp(1.6rem,4vw,3rem); min-height:280px; position:relative; overflow:hidden; }
.hero .eye { text-transform:uppercase; letter-spacing:.14em; font-size:.75rem; font-weight:800; color:#bfdbfe; }
.hero h1 { font-size:clamp(1.8rem,5vw,2.7rem); line-height:1.1; margin:.4rem 0 1rem; }
.hero p { color:#dbeafe; max-width:36rem; }
.chips { display:flex; flex-wrap:wrap; gap:.4rem; margin-top:1rem; }
.chips button, .chip { border:0; background:#fff; color:var(--navy); font-weight:800; font-size:.72rem; padding:.35rem .65rem; border-radius:999px; cursor:pointer; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr)); gap:.75rem; margin-top:1.25rem; }
.card { background:#fff; border:1px solid #dbeafe; border-radius:1rem; padding:1rem 1.1rem; text-decoration:none; color:inherit; display:block; }
.card h2, .card h3 { color:var(--navy); margin:.2rem 0 .4rem; font-size:1.05rem; }
.card .meta { font-size:.78rem; color:var(--muted); }
.banner { background:#fffbeb; border-left:4px solid #b45309; padding:.75rem 1rem; border-radius:.6rem; margin:0 0 1rem; font-size:.9rem; }
.layer { border-top:4px solid var(--navy); }
.layer .hold { color:#b91c1c; font-size:.72rem; font-weight:800; }
.crumbs { font-size:.88rem; color:var(--muted); margin:0 0 .8rem; }
.crumbs a { color:var(--navy); font-weight:700; text-decoration:none; }
.tool-hero { background:var(--navy); color:#fff; border-radius:1.1rem; padding:1.5rem 1.6rem; }
.tool-hero h1 { margin:.3rem 0; }
.criteria { display:grid; gap:.6rem; margin-top:1rem; }
.criteria div { background:#fff; border:1px solid #dbeafe; border-radius:.8rem; padding:.8rem 1rem; }
button.linkish { background:none; border:0; color:#fff; font:inherit; font-weight:700; cursor:pointer; }
footer { text-align:center; color:var(--muted); font-size:.8rem; padding:2rem 1rem; }
</style>
</head>
<body>
<header>
  <div class="top"><span>Calculadoras de Enfermagem · candidato controlado</span><span class="holdchip">HOLD / NOT_RELEASED · preview 100% localStorage</span></div>
  <nav class="main" id="nav"></nav>
</header>
<main id="app"></main>
<footer>Preview client-side. Não é deploy. Não fecha B9. Nurse-PaLM NOT_ASSERTED. Policy = CKO-MD + CKO-REG.</footer>
<script>
const KEY = "CKO_HOLD_PREVIEW_V1";
const SNAPSHOT = __SNAPSHOT__;
function loadState() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && parsed.id === SNAPSHOT.id && Array.isArray(parsed.layers) && parsed.layers.length === SNAPSHOT.layer_count) {
        return parsed;
      }
    }
  } catch (e) {}
  localStorage.setItem(KEY, JSON.stringify(SNAPSHOT));
  return SNAPSHOT;
}
const state = loadState();
function go(hash) { location.hash = hash; }
function route() { return (location.hash || "#/").replace(/^#/, "") || "/"; }
function navHtml() {
  const items = [
    ["#/", "Início"],
    ["#/mapa", "Mapa"],
    ["#/camadas", "Camadas"],
    ["#/ecossistema", "Ecossistema"],
    ["#/aldrete", "Aldrete"],
    ["#/imc", "IMC"],
  ];
  return '<a class="brand" href="#/">Calculadoras de Enfermagem</a>' +
    items.map(([h,l]) => '<a href="'+h+'">'+l+'</a>').join("");
}
function crumbs(items) {
  return '<nav class="crumbs">' + items.map(function (c, i) {
    if (typeof c === "string") return (i ? " › " : "") + "<span>" + c + "</span>";
    return (i ? " › " : "") + '<a href="' + c[0] + '">' + c[1] + "</a>";
  }).join("") + "</nav>";
}
function home() {
  const h = state.home;
  return '<section class="hero"><p class="eye">'+h.eyebrow+'</p><h1>'+h.title+'</h1><p>'+h.lead+'</p>' +
    '<p class="eye" style="margin-top:1.2rem">Escalas por especialidade</p><div class="chips">' +
    h.chips.map(c => '<a class="chip" href="#/especialidade/'+c.id+'">'+c.label+'</a>').join("") + '</div></section>' +
    '<div class="grid">' +
    state.tools.map(t => '<a class="card" href="#/'+t.id+'"><h3>'+t.title+'</h3><p class="meta">Runtime CALENF · HOLD</p></a>').join("") +
    state.pages.filter(p => p.id!=="home").map(p => '<a class="card" href="#/'+p.id+'"><h3>'+p.label+'</h3><p class="meta">'+p.title+'</p></a>').join("") +
    '</div>';
}
function pageView(id) {
  const p = state.pages.find(x => x.id===id);
  if (!p) return home();
  return crumbs([["#/","Início"], p.label]) +
    '<section class="hero"><p class="eye">Página institucional</p><h1>'+p.title+'</h1><p>'+(p.lead||"Candidato HOLD no padrão do site.")+'</p></section>' +
    '<p class="meta">Rota real quando servido: <code>'+p.href+'</code></p>';
}
function layersView() {
  return crumbs([["#/","Início"],["#/ecossistema","Ecossistema"],"Camadas"]) +
    '<section class="hero"><p class="eye">44/44</p><h1>Camadas classificadas do PDF</h1><p>Grelha do runtime CALENF. Estado HOLD / NOT_RELEASED. Sem publicação.</p></section>' +
    '<div class="grid">' + state.layers.map(l =>
      '<article class="card layer"><p class="meta">'+l.seq+' · '+l.id+'</p><h3>'+l.name+'</h3><p class="hold">'+l.release+' · holds '+l.holds_n+'</p></article>'
    ).join("") + '</div>';
}
function toolView(id) {
  const t = state.tools.find(x => x.id===id) || {title:id, href:"/"+id+".html"};
  const extra = id==="aldrete"
    ? '<div class="criteria"><div>Atividade (Motricidade)</div><div>Respiração</div><div>Circulação (PA)</div><div>Nível de Consciência</div><div>Saturação</div></div><p class="meta">Formulário completo vive em aldrete.html no runtime servido. Preview não executa cálculo clínico.</p>'
    : '<p>Canário do runtime CALENF. Ficheiro <code>'+t.file+'</code> quando o site é servido por HTTP.</p>';
  return crumbs([["#/","Início"], t.title]) +
    '<section class="tool-hero"><p class="eye">Ferramenta · HOLD</p><h1>'+t.title+'</h1><p>Preview visual no padrão do site. CKO-POL-UT-001: calculadoras PAUSED na policy; isto não é promoção clínica.</p></section>' + extra;
}
function specialtyView(id) {
  const s = (state.specialties || []).find(x => x.id===id);
  if (!s) return home();
  const listed = (s.tools || []).map(t =>
    state.tools.some(c => c.id===t.id)
      ? '<a class="card" href="#/'+t.id+'"><h3>'+t.title+'</h3><p class="meta">Canário HOLD</p></a>'
      : '<article class="card"><h3>'+t.title+'</h3><p class="meta">'+t.id+' · listado no hub; UT PAUSED</p></article>'
  ).join("");
  return crumbs([["#/","Início"],["#/","Especialidades"], s.label]) +
    '<section class="hero"><p class="eye">Escalas por especialidade</p><h1>'+s.title+'</h1><p>'+(s.lead||"Hub de escalas desta especialidade. HOLD / NOT_RELEASED.")+'</p></section>' +
    '<div class="grid">'+listed+'</div>';
}
function mapaView() {
  return crumbs([["#/","Início"],"Mapa do site"]) +
    '<section class="hero"><p class="eye">Navegação</p><h1>Mapa do site</h1><p>Destinos do candidato HOLD no padrão CALENF.</p></section>' +
    '<div class="grid">' +
    state.pages.concat(state.tools).map(p => '<a class="card" href="#/'+p.id+'"><h3>'+p.label+'</h3><p class="meta">'+p.href+'</p></a>').join("") +
    (state.specialties||[]).map(s => '<a class="card" href="#/especialidade/'+s.id+'"><h3>'+s.label+'</h3><p class="meta">'+s.href+'</p></a>').join("") +
    '</div>';
}
function render() {
  document.getElementById("nav").innerHTML = navHtml();
  const r = route();
  const app = document.getElementById("app");
  app.innerHTML = '<div class="banner">Preview 100% no browser. Snapshot gravado em <code>localStorage.'+KEY+'</code> ('+state.layer_count+' camadas, '+state.tools.length+' canários, '+state.pages.length+' páginas). Não autoriza deploy.</div>';
  if (r==="/" || r==="") app.innerHTML += home();
  else if (r==="/camadas") app.innerHTML += layersView();
  else if (r==="/mapa") app.innerHTML += mapaView();
  else if (r.indexOf("/especialidade/")===0) app.innerHTML += specialtyView(r.slice("/especialidade/".length));
  else if (state.tools.some(t => "/"+t.id===r)) app.innerHTML += toolView(r.slice(1));
  else if (state.pages.some(p => "/"+p.id===r)) app.innerHTML += pageView(r.slice(1));
  else app.innerHTML += home();
}
window.addEventListener("hashchange", render);
render();
</script>
</body>
</html>
"""


def main() -> None:
    snap = build_snapshot()
    if snap["layer_count"] != 44:
        raise SystemExit(f"preview snapshot must have 44 layers, got {snap['layer_count']}")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    embedded = json.dumps(snap, ensure_ascii=False).replace("<", "\\u003c")
    html = HTML.replace("__SNAPSHOT__", embedded)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(
        {
            "html": str(OUT_HTML),
            "json": str(OUT_JSON),
            "layers": snap["layer_count"],
            "tools": len(snap["tools"]),
            "pages": len(snap["pages"]),
            "release": snap["release"],
        }
    )


if __name__ == "__main__":
    main()
