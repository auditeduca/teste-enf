#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoria completa: JSON pendentes, HTML pendentes, traduções pendentes."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INSTITUTIONAL = {
    "index.html", "mapa-do-site.html", "acessibilidade-digital.html",
    "privacidade.html", "sustentabilidade-digital.html", "institucional.html",
    "calculadora-template.html",
}


def extract_hrefs(html_path):
    content = html_path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r'href="([^"#?]+\.html)"', content))


def main():
    report = {
        "resumo": {},
        "json_pendentes": {},
        "html_pendentes": {},
        "traducoes_pendentes": {},
        "outras_pendencias": {},
    }

    # --- HTML calculators in root ---
    html_calcs = {
        f.stem: f.name
        for f in ROOT.glob("*.html")
        if f.name not in INSTITUTIONAL
    }

    # --- JSON tools ---
    tools_dir = ROOT / "data" / "tools"
    json_files = {}
    json_by_slug = {}
    json_errors = []
    json_incomplete = []

    required_top = ["id", "slug", "seo", "overview", "calculator"]

    for jf in sorted(tools_dir.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            slug = data.get("slug", jf.stem)
            json_files[jf.stem] = jf.name
            json_by_slug[slug] = {
                "file": jf.name,
                "stem": jf.stem,
                "status": data.get("status", "unknown"),
            }
            missing = [k for k in required_top if k not in data]
            if missing:
                json_incomplete.append({
                    "arquivo": jf.name,
                    "slug": slug,
                    "campos_faltando": missing,
                })
        except Exception as e:
            json_errors.append({"arquivo": jf.name, "erro": str(e)})

    json_slugs = set(json_by_slug.keys())

    # HTML sem JSON correspondente (por slug)
    html_sem_json = sorted(
        [{"html": html_calcs[s], "slug": s} for s in html_calcs if s not in json_slugs],
        key=lambda x: x["slug"],
    )

    # JSON sem HTML correspondente (por slug)
    json_sem_html = sorted(
        [
            {
                "json": json_by_slug[s]["file"],
                "slug": s,
                "nome_arquivo_json": json_by_slug[s]["stem"],
                "status": json_by_slug[s]["status"],
            }
            for s in json_by_slug if s not in html_calcs
        ],
        key=lambda x: x["slug"],
    )

    # Divergência nome arquivo JSON vs slug/HTML
    nome_divergente = sorted(
        [
            {
                "slug": slug,
                "json_file": info["file"],
                "html_esperado": f"{slug}.html",
                "html_existe": slug in html_calcs,
            }
            for slug, info in json_by_slug.items()
            if info["stem"] != slug
        ],
        key=lambda x: x["slug"],
    )

    # --- Links no index.html que apontam para HTML inexistente ---
    index_path = ROOT / "index.html"
    all_html_names = {f.name for f in ROOT.glob("*.html")}
    index_hrefs = extract_hrefs(index_path) if index_path.exists() else set()
    links_quebrados_index = sorted([
        href for href in index_hrefs
        if not (ROOT / href.split("/")[-1]).exists()
    ])

    # --- tool-config nos HTML ---
    sem_tool_config = []
    tool_config_invalido = []
    sem_partials_loader = []
    sem_calc_engine = []

    for stem, fname in sorted(html_calcs.items()):
        content = (ROOT / fname).read_text(encoding="utf-8", errors="replace")
        if 'id="tool-config"' not in content:
            sem_tool_config.append(fname)
        elif not re.search(
            r'<script type="application/json" id="tool-config">',
            content,
        ):
            tool_config_invalido.append(fname)
        if "partials-loader.js" not in content:
            sem_partials_loader.append(fname)
        if "calc-engine.js" not in content:
            sem_calc_engine.append(fname)

    # --- Sincronização JSON embutido vs arquivo JSON ---
    json_embed_desatualizado = []
    for slug in sorted(set(html_calcs) & json_slugs):
        html_path = ROOT / html_calcs[slug]
        content = html_path.read_text(encoding="utf-8", errors="replace")
        m = re.search(
            r'<script type="application/json" id="tool-config">(.*?)</script>',
            content,
            re.DOTALL,
        )
        if not m:
            continue
        try:
            embedded = json.loads(m.group(1))
            jf = tools_dir / json_by_slug[slug]["file"]
            source = json.loads(jf.read_text(encoding="utf-8"))
            if embedded.get("version") != source.get("version") or embedded != source:
                json_embed_desatualizado.append({
                    "html": html_calcs[slug],
                    "json": json_by_slug[slug]["file"],
                    "html_version": embedded.get("version"),
                    "json_version": source.get("version"),
                })
        except Exception as e:
            json_embed_desatualizado.append({
                "html": html_calcs[slug],
                "erro": str(e),
            })

    # --- Traduções i18n ---
    i18n_dir = ROOT / "i18n"
    manifest_path = i18n_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    en_path = i18n_dir / "en.json"
    es_path = i18n_dir / "es.json"
    en_keys = set(json.loads(en_path.read_text(encoding="utf-8")).keys()) if en_path.exists() else set()
    es_keys = set(json.loads(es_path.read_text(encoding="utf-8")).keys()) if es_path.exists() else set()

    # Chaves data-i18n no index.html
    index_content = index_path.read_text(encoding="utf-8", errors="replace") if index_path.exists() else ""
    index_i18n_keys = set(re.findall(r'data-i18n(?:-placeholder)?="([^"]+)"', index_content))

    chaves_index_sem_en = sorted(index_i18n_keys - en_keys)
    chaves_index_sem_es = sorted(index_i18n_keys - es_keys)
    chaves_en_sem_es = sorted(en_keys - es_keys)
    chaves_es_sem_en = sorted(es_keys - en_keys)

    # Idiomas planejados sem arquivo JSON
    planned = manifest.get("plannedNotYetIntegrated", [])
    idiomas_sem_arquivo = sorted([
        code for code in planned
        if not (i18n_dir / f"{code}.json").exists()
    ])

    # Idiomas no lang-selector.js sem tradução completa
    lang_selector = (ROOT / "js" / "lang-selector.js").read_text(encoding="utf-8", errors="replace")
    langs_no_selector = re.findall(r'\{ code: "([^"]+)"', lang_selector)
    available_codes = {"pt", "pt-BR", "en", "es"}
    for item in manifest.get("available", []):
        available_codes.add(item.get("code", ""))

    idiomas_selector_sem_json = sorted([
        code for code in langs_no_selector
        if code not in available_codes
        and code not in ("pt-BR",)
        and not (i18n_dir / f"{code.split('-')[0]}.json").exists()
    ])

    # Chaves tool.* esperadas vs existentes (91 ferramentas no index)
    tool_keys_index = sorted([k for k in index_i18n_keys if k.startswith("tool.")])
    tool_keys_en = sorted([k for k in en_keys if k.startswith("tool.")])
    tool_keys_es = sorted([k for k in es_keys if k.startswith("tool.")])

    # --- Páginas institucionais modularização ---
    inst_modular = {}
    for fname in INSTITUTIONAL - {"calculadora-template.html"}:
        p = ROOT / fname
        if p.exists():
            c = p.read_text(encoding="utf-8", errors="replace")
            inst_modular[fname] = "partials-loader.js" in c

    # --- Montar relatório ---
    report["resumo"] = {
        "total_html_calculadoras": len(html_calcs),
        "total_json_tools": len(json_files),
        "pares_completos_slug": len(set(html_calcs) & json_slugs),
        "html_sem_json": len(html_sem_json),
        "json_sem_html": len(json_sem_html),
        "links_quebrados_no_index": len(links_quebrados_index),
        "html_sem_tool_config": len(sem_tool_config),
        "html_nao_modularizados": len(sem_partials_loader),
        "chaves_i18n_index": len(index_i18n_keys),
        "chaves_en_json": len(en_keys),
        "chaves_es_json": len(es_keys),
        "idiomas_completos": ["pt (nativo)", "en", "es"],
        "idiomas_parciais_planejados": len(planned),
    }

    report["json_pendentes"] = {
        "criar_json_para_html": html_sem_json,
        "json_sem_html_gerado": json_sem_html,
        "json_com_erro_parse": json_errors,
        "json_incompletos_schema": json_incomplete,
        "nome_arquivo_diverge_do_slug": nome_divergente,
        "html_com_tool_config_desatualizado": json_embed_desatualizado,
    }

    report["html_pendentes"] = {
        "gerar_html_a_partir_de_json": json_sem_html,
        "links_quebrados_referenciados_no_index": links_quebrados_index,
        "sem_bloco_tool_config": sem_tool_config,
        "tool_config_malformado": tool_config_invalido,
        "sem_partials_loader_modular": sem_partials_loader,
        "sem_calc_engine_js": sem_calc_engine,
        "paginas_institucionais_modularizacao": inst_modular,
    }

    report["traducoes_pendentes"] = {
        "idiomas_planejados_sem_arquivo_json": [
            {"code": c, "arquivo_esperado": f"i18n/{c}.json"}
            for c in idiomas_sem_arquivo
        ],
        "idiomas_no_seletor_sem_traducao_completa": idiomas_selector_sem_json,
        "chaves_index_ausentes_em_en": chaves_index_sem_en,
        "chaves_index_ausentes_em_es": chaves_index_sem_es,
        "divergencia_en_vs_es": {
            "somente_em_en": chaves_en_sem_es,
            "somente_em_es": chaves_es_sem_en,
        },
        "tool_keys": {
            "no_index": len(tool_keys_index),
            "em_en": len(tool_keys_en),
            "em_es": len(tool_keys_es),
            "index_sem_en": sorted(set(k.split(".")[1] if len(k.split(".")) > 1 else k for k in tool_keys_index) - set(k.split(".")[1] if len(k.split(".")) > 1 else k for k in tool_keys_en)),
        },
    }

    report["outras_pendencias"] = {
        "sitemap_xml": (ROOT / "sitemap.xml").exists(),
        "pt_json": (i18n_dir / "pt.json").exists(),
        "fonts_woff2": list((ROOT / "fonts").rglob("*.woff2")) if (ROOT / "fonts").exists() else [],
        "manifest_json_link": "manifest.json" in index_content,
        "site_webmanifest": (ROOT / "site.webmanifest.webmanifest").exists(),
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print("===RELATORIO_JSON_START===")
    print(payload)
    print("===RELATORIO_JSON_END===")
    print(json.dumps(report["resumo"], ensure_ascii=False, indent=2), file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
