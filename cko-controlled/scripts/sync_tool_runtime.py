#!/usr/bin/env python3
"""Sync PT-BR tool/library runtimes from reference-website into the hosted public root.

Wave2 institutional pages stay in place. Asset trees are copied (or refreshed)
from reference-website. This script also writes the known-universe inventory
used by policy-as-code and generates the missing escalas-de-enfermagem hubs.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "public"
SRC = ROOT.parent / "reference-website"

WAVE2_PAGES = {
    "index.html",
    "missao.html",
    "objetivo.html",
    "ecossistema.html",
    "acessibilidade.html",
    "tecnologiaverde.html",
    "privacidade.html",
    "politica-editorial.html",
    "notificacoes-legais.html",
    "fale.html",
    "forum-enfermagem.html",
    "mapa-do-site.html",
}

SKIP_HTML = {
    "cko-relatorio-tecnico-final.html",
    "grafo-clinico.html",
}

TOOL_CANARIES = [
    "aldrete.html",
    "imc.html",
    "gotejamento.html",
    "braden.html",
    "news.html",
    "gasometria.html",
]
LIBRARY_CANARIES = [
    "biblioteca.html",
    "downloads.html",
    "biblioteca-provas.html",
    "biblioteca-cirurgica.html",
    "biblioteca-curativo.html",
    "biblioteca-seringa.html",
    "biblioteca-carinho-de-emergencia.html",
]
ENGINE_LIBS = [
    "js/calc-engine.js",
    "js/calc-engine-v2.js",
    "js/ce-calculadora-padrao.js",
    "js/modules/data/biblioteca.json",
    "js/modules/catalog-page.js",
]

CALC_MARKERS = (
    "btnCalcular",
    "scoreValor",
    "calcularIMC",
    "calcularGotejamento",
    'id="tool-config"',
    "calc-engine.js",
    "data-calc-input",
)

ASSET_TREES = (
    "js",
    "css",
    "fonts",
    "img",
    "images",
    "assets",
    "biblioteca",
    "blog",
    "downloads",
    "partials",
)

HUBS = [
    ("centro-cirurgico", "Centro Cirúrgico", ("cirúrg", "anestesi", "srpa", "perioper", "elpo", "aldrete", "asa")),
    ("dor", "Dor", ("dor", "pain", "bps", "flacc", "cries", "lanss", "wong", "nips", "numéric", "numeric")),
    ("funcionalidade", "Funcionalidade", ("barthel", "katz", "lawton", "berg", "tug", "tinetti", "funcional", "ecog", "karnofsky")),
    ("geriatria", "Geriatria", ("geriatr", "meem", "moca", "gds", "zarit", "edmonton", "fragilidade", "cam")),
    ("gestao", "Gestão", ("fugulin", "dimensionamento", "gestão", "gestao", "ferias", "rescisão", "hora-extra", "noturno")),
    ("lesao-por-pressao", "Lesão por Pressão", ("braden", "norton", "waterlow", "push", "gosnell", "pressão", "pressao", "elpo")),
    ("neonatologia", "Neonatologia", ("neo", "apgar", "ballard", "capurro", "downes", "silverman", "nips", "recém")),
    ("neurologia", "Neurologia", ("glasgow", "nihss", "four", "rass", "cam", "fast", "cincinnati", "pupila", "rancholosamigos")),
    ("obstetricia", "Obstetrícia", ("obstetr", "bishop", "meows", "gestacional", "apgar")),
    ("pneumologia", "Pneumologia", ("pneum", "curb", "downes", "sofa", "qsofa")),
    ("seguranca-do-paciente", "Segurança do Paciente", ("morse", "hendrich", "humpty", "downton", "johns", "news", "mews", "braden", "manchester")),
    ("terapia-intensiva", "Terapia Intensiva", ("uti", "sofa", "qsofa", "apache", "rass", "bps", "ramsay", "news")),
    ("urgencia-emergencia", "Urgência/Emergência", ("urgên", "emerg", "manchester", "heart", "news", "mews", "alvarado", "abcd2", "wells")),
]


def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def sync_from_reference() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"reference-website not found: {SRC}")
    copied = 0
    skipped = 0
    for html in SRC.glob("*.html"):
        if html.name in WAVE2_PAGES or html.name in SKIP_HTML:
            skipped += 1
            continue
        shutil.copy2(html, PUB / html.name)
        copied += 1
    for name in SKIP_HTML:
        stale = PUB / name
        if stale.exists():
            stale.unlink()
    for name in ASSET_TREES:
        src = SRC / name
        if src.is_dir():
            copy_tree(src, PUB / name)
    src_data = SRC / "data"
    if src_data.is_dir():
        copy_tree(src_data, PUB / "data")
    (PUB / "public").mkdir(parents=True, exist_ok=True)
    for rel in (
        "public/output.css",
        "global-styles.css",
        "global-scripts.js",
        "lang-selector.js",
        "favicon.ico",
        "favicon.svg",
        "apple-touch-icon.png",
        "site.webmanifest",
    ):
        src = SRC / rel
        if src.exists():
            dest = PUB / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    print(f"html_copied={copied} wave2_preserved={skipped}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def is_calc_html(html: str) -> bool:
    return any(m in html for m in CALC_MARKERS)


def home_local_hrefs() -> list[str]:
    index = read_text(PUB / "index.html")
    hrefs = []
    for raw in re.findall(r'href="([^"]+)"', index):
        if raw.startswith(("http://", "https://", "mailto:", "tel:", "#", "//")):
            continue
        path = raw.split("#", 1)[0].split("?", 1)[0]
        if not path:
            continue
        hrefs.append(path.lstrip("/"))
    return sorted(set(hrefs))


def load_tool_jsons() -> list[dict]:
    tools = []
    tools_dir = PUB / "data" / "tools"
    if not tools_dir.is_dir():
        return tools
    for path in sorted(tools_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        tools.append(
            {
                "slug": data.get("slug") or path.stem,
                "name": (data.get("overview") or {}).get("name") or path.stem,
                "json": f"data/tools/{path.name}",
                "html": f"{data.get('slug') or path.stem}.html",
                "specialty": (data.get("overview") or {}).get("specialty") or [],
                "category": (data.get("breadcrumb") or {}).get("category"),
            }
        )
    return tools


def resolve_tool_html(slug: str) -> str | None:
    candidates = [f"{slug}.html"]
    if slug.startswith("escala-de-"):
        candidates.append(f"{slug.replace('escala-de-', '')}.html")
    if slug == "escala-de-braden":
        candidates.append("braden.html")
    if slug == "escala-de-morse":
        candidates.append("morse.html")
    if slug == "escala-de-glasgow":
        candidates.append("glasgow.html")
    for name in candidates:
        if (PUB / name).is_file():
            return name
    return None


def build_inventory() -> dict:
    tools = load_tool_jsons()
    for tool in tools:
        html = resolve_tool_html(tool["slug"])
        tool["html"] = html
        tool["present"] = bool(html and (PUB / html).is_file())
        if html:
            tool["has_calc_runtime"] = is_calc_html(read_text(PUB / html))
        else:
            tool["has_calc_runtime"] = False

    library_pages = [name for name in LIBRARY_CANARIES if (PUB / name).is_file()]
    biblioteca_articles = sorted(
        str(p.relative_to(PUB)).replace("\\", "/")
        for p in (PUB / "biblioteca").rglob("*.html")
        if p.is_file()
    )
    libs = [rel for rel in ENGINE_LIBS if (PUB / rel).is_file()]
    hrefs = home_local_hrefs()
    missing_home = []
    for h in hrefs:
        target = PUB / h
        if target.exists():
            continue
        if h.endswith("/") and (PUB / h / "index.html").exists():
            continue
        missing_home.append(h)
    canary_tools = [n for n in TOOL_CANARIES if (PUB / n).is_file() and is_calc_html(read_text(PUB / n))]
    return {
        "id": "CKO-TOOL-LIBRARY-RUNTIME-1.0.0",
        "kind": "tool-library-runtime",
        "root": "policy-as-code",
        "release": "HOLD / NOT_RELEASED",
        "wave2_pages": sorted(WAVE2_PAGES),
        "tool_canaries": canary_tools,
        "library_canaries": library_pages,
        "engine_libraries": libs,
        "tools": tools,
        "tools_n": len(tools),
        "tools_with_html": sum(1 for t in tools if t["present"]),
        "tools_with_calc_runtime": sum(1 for t in tools if t["has_calc_runtime"]),
        "biblioteca_articles_n": len(biblioteca_articles),
        "home_local_hrefs": hrefs,
        "home_missing_hrefs": missing_home,
        "hubs": [f"escalas-de-enfermagem/{slug}/index.html" for slug, _, _ in HUBS],
    }


def write_home_aliases() -> None:
    """Fill Wave2 home hrefs that do not exist as dedicated files in the source tree."""
    aliases = {
        "classificacao_intervencoes-enfermagem.html": "nanda.html",
        "dimensionamento-cofen.html": "dimensionamento.html",
    }
    for dest_name, src_name in aliases.items():
        src = PUB / src_name
        dest = PUB / dest_name
        if src.is_file():
            shutil.copy2(src, dest)
    hub = PUB / "concurso_publico" / "index.html"
    hub.parent.mkdir(parents=True, exist_ok=True)
    sims = sorted(p.name for p in PUB.glob("simulado*.html"))
    extra = [n for n in ("biblioteca-provas.html", "simulados.html") if (PUB / n).is_file()]
    items = "\n".join(
        f'<li><a class="block rounded-2xl border border-blue-100 bg-white p-5 hover:shadow-lg" href="../{name}"><strong class="text-[#1A3E74]">{name.replace(".html","").replace("_"," ").replace("-"," ")}</strong></a></li>'
        for name in extra + sims
    )
    hub.write_text(
        f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="robots" content="noindex, nofollow"/>
<title>Concurso público — guias e simulados</title>
<link rel="stylesheet" href="../public/output.css"/>
</head>
<body class="bg-[#F8FAFC] text-slate-800">
<main class="max-w-5xl mx-auto px-4 py-10">
<p class="text-sm text-[#1A3E74] font-semibold uppercase tracking-wide"><a href="../index.html">Calculadoras de Enfermagem</a></p>
<h1 class="text-3xl font-black text-[#1A3E74] mt-2">Concurso público</h1>
<p class="text-slate-600 mt-2">Simulados e biblioteca de provas. Estado: HOLD / NOT_RELEASED.</p>
<ul class="grid gap-3 sm:grid-cols-2 mt-8">
{items}
</ul>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_hubs(inventory: dict) -> None:
    tools = inventory["tools"]
    for slug, title, needles in HUBS:
        dest = PUB / "escalas-de-enfermagem" / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        matched = []
        for tool in tools:
            blob = " ".join(
                [tool["slug"], tool["name"], tool.get("category") or "", " ".join(tool.get("specialty") or [])]
            ).lower()
            if any(n in blob for n in needles) and tool.get("html"):
                matched.append(tool)
        seen = set()
        unique = []
        for tool in matched:
            if tool["html"] in seen:
                continue
            seen.add(tool["html"])
            unique.append(tool)
        unique.sort(key=lambda t: t["name"])
        items = "\n".join(
            f'<li><a class="block rounded-2xl border border-blue-100 bg-white p-5 hover:shadow-lg" href="../../{t["html"]}"><strong class="text-[#1A3E74]">{t["name"]}</strong><span class="block text-sm text-slate-600 mt-1">{t["slug"]}</span></a></li>'
            for t in unique
        )
        dest.write_text(
            f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="robots" content="noindex, nofollow"/>
<title>Escalas de Enfermagem — {title}</title>
<link rel="stylesheet" href="../../public/output.css"/>
</head>
<body class="bg-[#F8FAFC] text-slate-800">
<main class="max-w-5xl mx-auto px-4 py-10">
<p class="text-sm text-[#1A3E74] font-semibold uppercase tracking-wide"><a href="../../index.html">Calculadoras de Enfermagem</a></p>
<h1 class="text-3xl font-black text-[#1A3E74] mt-2">{title}</h1>
<p class="text-slate-600 mt-2">Hub de escalas e ferramentas desta especialidade. Estado: HOLD / NOT_RELEASED.</p>
<ul class="grid gap-3 sm:grid-cols-2 mt-8">
{items or '<li class="text-slate-600">Nenhuma ferramenta classificada neste hub.</li>'}
</ul>
</main>
</body>
</html>
""",
            encoding="utf-8",
        )


def write_inventory(inventory: dict) -> Path:
    slim = dict(inventory)
    slim.pop("home_local_hrefs", None)
    out = PUB / "data" / "tool-library-runtime.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(slim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def assert_canaries(inventory: dict) -> None:
    missing = [n for n in TOOL_CANARIES if n not in inventory["tool_canaries"]]
    missing += [n for n in LIBRARY_CANARIES if n not in inventory["library_canaries"]]
    missing += [n for n in ENGINE_LIBS if n not in inventory["engine_libraries"]]
    if inventory["home_missing_hrefs"]:
        missing.extend(f"home:{h}" for h in inventory["home_missing_hrefs"])
    if missing:
        raise SystemExit("tool/library runtime missing: " + ", ".join(missing[:40]))


def main() -> None:
    inventory_only = "--inventory-only" in sys.argv
    if not inventory_only:
        sync_from_reference()
    write_home_aliases()
    inventory = build_inventory()
    write_hubs(inventory)
    inventory = build_inventory()
    path = write_inventory(inventory)
    assert_canaries(inventory)
    print(
        json.dumps(
            {
                "inventory": str(path.relative_to(ROOT)),
                "tools_n": inventory["tools_n"],
                "tools_with_html": inventory["tools_with_html"],
                "tools_with_calc_runtime": inventory["tools_with_calc_runtime"],
                "biblioteca_articles_n": inventory["biblioteca_articles_n"],
                "tool_canaries": inventory["tool_canaries"],
                "library_canaries": inventory["library_canaries"],
                "engine_libraries": inventory["engine_libraries"],
                "home_missing_hrefs": inventory["home_missing_hrefs"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
