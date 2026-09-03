#!/usr/bin/env python3
"""Converge the CKO overlay into the CALENF (reference-website) structure.

The hosted site is CALENF: data/tools/*.json → HTML, js/calc-engine.js,
js/nurse-palm.js, js/knowledge-graph.js, NIFS-600-15 digital twin (HOLD).
Wave2 institutional pages are overlaid onto that tree. The script does not
copy CALENF into cko-controlled/public.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
WAVE2 = GATE / "public"

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
    "js/nurse-palm.js",
    "js/knowledge-graph.js",
    "js/modules/data/biblioteca.json",
]
CALENF_STRUCTURE = [
    "data/schemas/tool.schema.json",
    "data/tools",
    "scripts/generate_tool_page.py",
    "js/calc-engine.js",
    "js/calc-engine-v2.js",
    "js/nurse-palm.js",
    "js/knowledge-graph.js",
    "js/partials-loader.js",
    "partials/header.html",
]
NURSE_PALM_V9_LAYERS = [
    "Clinical Reasoning",
    "Episodic Memory",
    "Temporal Graph",
    "World Model",
    "Clinical Attention",
    "Uncertainty Model",
    "Planner",
    "Feedback Learning",
    "Simulation Engine",
    "Multi-Agent Council",
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
TOOL_REQUIRED = ("id", "slug", "code", "overview", "calculator", "interpretation")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def is_calc_html(html: str) -> bool:
    return any(m in html for m in CALC_MARKERS)


def overlay_wave2_into_calenf() -> None:
    if not SITE.is_dir():
        raise SystemExit(f"CALENF root missing: {SITE}")
    copied = []
    for name in sorted(WAVE2_PAGES):
        src = WAVE2 / name
        if not src.is_file():
            raise SystemExit(f"Wave2 page missing in overlay source: {name}")
        shutil.copy2(src, SITE / name)
        copied.append(name)
    robots = WAVE2 / "robots.txt"
    if robots.is_file():
        shutil.copy2(robots, SITE / "robots.txt")
    print("wave2_overlaid", ",".join(copied))


def validate_tool_schema(data: dict) -> list[str]:
    errors = []
    for key in TOOL_REQUIRED:
        if key not in data:
            errors.append(f"missing {key}")
    overview = data.get("overview") or {}
    if "name" not in overview or "objective" not in overview:
        errors.append("overview.name/objective")
    calc = data.get("calculator") or {}
    if "inputs" not in calc or "formula" not in calc:
        errors.append("calculator.inputs/formula")
    return errors


def load_tool_jsons() -> list[dict]:
    tools = []
    tools_dir = SITE / "data" / "tools"
    for path in sorted(tools_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        schema_errors = validate_tool_schema(data)
        tools.append(
            {
                "slug": data.get("slug") or path.stem,
                "name": (data.get("overview") or {}).get("name") or path.stem,
                "json": f"data/tools/{path.name}",
                "html": f"{data.get('slug') or path.stem}.html",
                "specialty": (data.get("overview") or {}).get("specialty") or [],
                "category": (data.get("breadcrumb") or {}).get("category"),
                "schema_ok": len(schema_errors) == 0,
                "schema_errors": schema_errors,
            }
        )
    return tools


def resolve_tool_html(slug: str) -> str | None:
    """Prefer a calculator HTML over a redirect alias for the same slug."""
    candidates = [f"{slug}.html"]
    if slug.startswith("escala-de-"):
        candidates.append(f"{slug.replace('escala-de-', '')}.html")
    if slug == "escala-de-braden":
        candidates.append("braden.html")
    if slug == "escala-de-morse":
        candidates.append("morse.html")
    if slug == "escala-de-glasgow":
        candidates.append("glasgow.html")
    scored: list[tuple[int, str]] = []
    seen: set[str] = set()
    for name in candidates:
        if name in seen or not (SITE / name).is_file():
            continue
        seen.add(name)
        html = read_text(SITE / name)
        rank = 2 if is_calc_html(html) else 1
        if 'http-equiv="refresh"' in html or "meta http-equiv='refresh'" in html:
            rank = 0
        scored.append((rank, name))
    if not scored:
        return None
    scored.sort(key=lambda row: (-row[0], row[1]))
    return scored[0][1]


def home_local_hrefs() -> list[str]:
    index = read_text(SITE / "index.html")
    hrefs = []
    for raw in re.findall(r'href="([^"]+)"', index):
        if raw.startswith(("http://", "https://", "mailto:", "tel:", "#", "//")):
            continue
        path = raw.split("#", 1)[0].split("?", 1)[0]
        if not path:
            continue
        hrefs.append(path.lstrip("/"))
    return sorted(set(hrefs))


def build_inventory() -> dict:
    tools = load_tool_jsons()
    for tool in tools:
        html = resolve_tool_html(tool["slug"])
        tool["html"] = html
        tool["present"] = bool(html and (SITE / html).is_file())
        tool["has_calc_runtime"] = bool(html and is_calc_html(read_text(SITE / html)))
    library_pages = [name for name in LIBRARY_CANARIES if (SITE / name).is_file()]
    biblioteca_n = sum(1 for _ in (SITE / "biblioteca").rglob("*.html")) if (SITE / "biblioteca").is_dir() else 0
    libs = [rel for rel in ENGINE_LIBS if (SITE / rel).exists()]
    hrefs = home_local_hrefs()
    missing_home = []
    for h in hrefs:
        target = SITE / h
        if target.exists() or (h.endswith("/") and (SITE / h / "index.html").exists()):
            continue
        missing_home.append(h)
    canary_tools = [n for n in TOOL_CANARIES if (SITE / n).is_file() and is_calc_html(read_text(SITE / n))]
    structure = [rel for rel in CALENF_STRUCTURE if (SITE / rel).exists()]
    return {
        "id": "CKO-TOOL-LIBRARY-RUNTIME-1.0.0",
        "kind": "tool-library-runtime",
        "root": "policy-as-code",
        "structure": "calenf",
        "release": "HOLD / NOT_RELEASED",
        "wave2_pages": sorted(WAVE2_PAGES),
        "tool_canaries": canary_tools,
        "library_canaries": library_pages,
        "engine_libraries": libs,
        "calenf_structure": structure,
        "tools": tools,
        "tools_n": len(tools),
        "tools_with_html": sum(1 for t in tools if t["present"]),
        "tools_with_calc_runtime": sum(1 for t in tools if t["has_calc_runtime"]),
        "tools_schema_ok": sum(1 for t in tools if t["schema_ok"]),
        "biblioteca_articles_n": biblioteca_n,
        "home_local_hrefs": hrefs,
        "home_missing_hrefs": missing_home,
        "hubs": [f"escalas-de-enfermagem/{slug}/index.html" for slug, _, _ in HUBS],
    }


def write_home_aliases() -> None:
    aliases = {
        "classificacao_intervencoes-enfermagem.html": "nanda.html",
        "dimensionamento-cofen.html": "dimensionamento.html",
    }
    for dest_name, src_name in aliases.items():
        src = SITE / src_name
        dest = SITE / dest_name
        if src.is_file():
            shutil.copy2(src, dest)
    hub = SITE / "concurso_publico" / "index.html"
    hub.parent.mkdir(parents=True, exist_ok=True)
    sims = sorted(p.name for p in SITE.glob("simulado*.html"))
    extra = [n for n in ("biblioteca-provas.html", "simulados.html") if (SITE / n).is_file()]
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
        dest = SITE / "escalas-de-enfermagem" / slug / "index.html"
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


def build_governance(inventory: dict) -> dict:
    nodes = [
        {"id": "B5", "type": "DigitalTwin", "nifs": "NIFS-600-15", "observed": False, "deployed": False},
        {"id": "B6.1", "type": "ClinicalVertical"},
        {"id": "B6.2", "type": "KnowledgeLibraries"},
        {"id": "B9", "type": "ReleaseFanIn", "release": "NOT_RELEASED"},
        {"id": "B10", "type": "NursePaLM", "operational": "NOT_ASSERTED", "engine": "js/nurse-palm.js", "layers": NURSE_PALM_V9_LAYERS},
        {"id": "SCHEMA-TOOL", "type": "Schema", "path": "data/schemas/tool.schema.json"},
        {"id": "GRAPH-KG", "type": "KnowledgeGraph", "path": "js/knowledge-graph.js"},
    ]
    edges = [
        ["B5", "B9", "fanIn"],
        ["B6.1", "B9", "fanIn"],
        ["B6.2", "B9", "fanIn"],
        ["B10", "B9", "fanIn"],
        ["B5", "B10", "feeds"],
    ]
    for tool in inventory["tools"]:
        node_id = f"TOOL-{tool['slug']}"
        twin_id = f"TWIN-{tool['slug']}"
        nodes.append(
            {
                "id": node_id,
                "type": "ToolRuntime",
                "slug": tool["slug"],
                "schema": "data/schemas/tool.schema.json",
                "schema_ok": tool["schema_ok"],
                "html": tool.get("html"),
                "nursePalm": {"engine": "js/nurse-palm.js", "layers": 10, "operational": "NOT_ASSERTED"},
            }
        )
        nodes.append(
            {
                "id": twin_id,
                "type": "TwinProjection",
                "of": node_id,
                "governedBy": "B5",
                "nifs": "NIFS-600-15",
                "observed": False,
                "deployed": False,
            }
        )
        edges.extend(
            [
                [node_id, "SCHEMA-TOOL", "instanceOf"],
                [node_id, twin_id, "projectedAs"],
                [twin_id, "B5", "governedBy"],
                [node_id, "B10", "boundTo"],
                [node_id, "GRAPH-KG", "inGraph"],
                [node_id, "B6.1", "clinicalVertical"],
                [node_id, "B9", "fanIn"],
            ]
        )
    for lib in inventory["library_canaries"]:
        node_id = f"LIB-{Path(lib).stem}"
        nodes.append({"id": node_id, "type": "LibraryRuntime", "html": lib, "schema": "js/modules/data/biblioteca.json"})
        edges.extend([[node_id, "B6.2", "governedBy"], [node_id, "B9", "fanIn"], [node_id, "B10", "boundTo"]])
    return {
        "id": "CKO-CALENF-GOVERNANCE-1.0.0",
        "kind": "calenf-runtime-governance",
        "root": "policy-as-code",
        "structure": "NIFS-900-03",
        "release": "HOLD / NOT_RELEASED",
        "nursePalm": {
            "engine": "js/nurse-palm.js",
            "layers": NURSE_PALM_V9_LAYERS,
            "operational": "NOT_ASSERTED",
            "audit": "NURSE_PALM_21_LAYER_COMPLETENESS_AUDIT_v6_4_0",
        },
        "digitalTwin": {
            "nifs": "NIFS-600-15",
            "block": "B5",
            "observed": False,
            "deployed": False,
            "classified_nodes": 137,
            "classified_edges": 136,
        },
        "schema": "data/schemas/tool.schema.json",
        "graph": "js/knowledge-graph.js",
        "ssg": "scripts/generate_tool_page.py",
        "nodes": nodes,
        "edges": edges,
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "tools_schema_ok": inventory["tools_schema_ok"],
        "tools_n": inventory["tools_n"],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


KEEP_OVERLAY = {
    "404.html",
    "footer.html",
    "engine",
    "policies",
    "schemas",
    "graph",
    "drive",
    "institucional",
    "data",
    "fonts",
    "public",
    "robots.txt",
    "global-scripts.js",
    "global-styles.css",
    "lang-selector.js",
} | set(WAVE2_PAGES)
KEEP_DATA = {
    "drive-immutable.json",
    "evidence-index.json",
    "gate-report.json",
    "pendencies.json",
    "remediation-plan.json",
    "residual-uncertainty.json",
    "tool-library-runtime.json",
    "universe.json",
    "unknown-universe.json",
}


def drop_duplicate_cko_copies() -> None:
    """Remove one-way CALENF copies from the CKO overlay. The site is reference-website."""
    removed = 0
    for path in list(WAVE2.iterdir()):
        if path.name in KEEP_OVERLAY or path.name.startswith("."):
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        removed += 1
    data = WAVE2 / "data"
    if data.is_dir():
        for path in list(data.iterdir()):
            if path.name in KEEP_DATA:
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed += 1
    fonts = WAVE2 / "fonts"
    if fonts.is_dir():
        for path in list(fonts.iterdir()):
            if path.name == "inter":
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed += 1
    print(f"cko_public_duplicates_removed={removed}")


def assert_canaries(inventory: dict, governance: dict) -> None:
    missing = [n for n in TOOL_CANARIES if n not in inventory["tool_canaries"]]
    missing += [n for n in LIBRARY_CANARIES if n not in inventory["library_canaries"]]
    missing += [n for n in ENGINE_LIBS if n not in inventory["engine_libraries"]]
    missing += [rel for rel in CALENF_STRUCTURE if rel not in inventory["calenf_structure"]]
    if inventory["home_missing_hrefs"]:
        missing.extend(f"home:{h}" for h in inventory["home_missing_hrefs"])
    if governance["nursePalm"]["operational"] != "NOT_ASSERTED":
        missing.append("nursePalm.operational")
    if governance["digitalTwin"]["observed"] or governance["digitalTwin"]["deployed"]:
        missing.append("digitalTwin.observed/deployed")
    if inventory["tools_schema_ok"] < len(TOOL_CANARIES):
        missing.append("tools_schema_ok")
    if missing:
        raise SystemExit("CALENF runtime missing: " + ", ".join(missing[:40]))


def main() -> None:
    overlay_wave2_into_calenf()
    write_home_aliases()
    inventory = build_inventory()
    write_hubs(inventory)
    inventory = build_inventory()
    slim = dict(inventory)
    slim.pop("home_local_hrefs", None)
    governance = build_governance(slim)
    write_json(SITE / "data" / "cko" / "tool-library-runtime.json", slim)
    write_json(SITE / "data" / "cko" / "governance.json", governance)
    write_json(WAVE2 / "data" / "tool-library-runtime.json", slim)
    if "--inventory-only" not in sys.argv:
        drop_duplicate_cko_copies()
    assert_canaries(slim, governance)
    print(
        json.dumps(
            {
                "site": "reference-website",
                "structure": "NIFS-900-03",
                "tools_n": slim["tools_n"],
                "tools_schema_ok": slim["tools_schema_ok"],
                "tools_with_calc_runtime": slim["tools_with_calc_runtime"],
                "biblioteca_articles_n": slim["biblioteca_articles_n"],
                "governance_nodes": governance["nodeCount"],
                "nursePalm": governance["nursePalm"]["operational"],
                "digitalTwin_observed": governance["digitalTwin"]["observed"],
                "home_missing_hrefs": slim["home_missing_hrefs"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
