#!/usr/bin/env python3
"""Sync generated website pages into NKOS datasets (SEO, templates, page registry)."""
from __future__ import annotations

import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "pt"
DATASETS = ROOT / "datasets"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def page_to_canonical(rel: str) -> str:
    rel = rel.replace("\\", "/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        rel = rel[: -len("/index.html")]
    return f"/{rel}" if rel else "/"


def infer_template(canon: str) -> str:
    if canon == "/":
        return "TPL.LANDING_HOME"
    if canon == "/privacidade":
        return "TPL.PRIVACY_CENTER"
    if canon == "/sustentabilidade":
        return "TPL.SUSTAINABILITY_CENTER"
    if canon in (
        "/ferramentas", "/protocolos", "/calculadoras", "/escalas", "/biblioteca",
        "/simulados", "/artigos", "/flashcards", "/quiz", "/glossario", "/competencias",
        "/educacao", "/tabelas",
    ):
        return "TPL.HUB"
    if canon.startswith("/ferramentas/"):
        return "TPL.CLINICAL_TOOL"
    if canon.startswith("/protocolos/"):
        return "TPL.PROTOCOL"
    if canon.startswith("/artigos/"):
        return "TPL.ARTICLE"
    if canon.startswith("/simulados/"):
        return "TPL.SIMULATION"
    if canon.startswith("/flashcards/"):
        return "TPL.FLASHCARD"
    if canon in ("/calculadoras-trabalhistas",):
        return "TPL.HUB"
    if canon.startswith("/calculadoras-trabalhistas/"):
        return "TPL.CLINICAL_TOOL"
    if canon.startswith("/curriculo/") or canon.startswith("/sbar/"):
        return "TPL.WIZARD"
    if canon in ("/nanda", "/sae", "/sbar", "/curriculo", "/calendario-vacinal", "/mapas-mentais", "/empregos", "/concursos", "/cursos", "/autoconhecimento"):
        return "TPL.MODULE_LANDING"
    if canon.startswith("/gestao/"):
        return "TPL.DASHBOARD"
    if canon == "/trilhas":
        return "TPL.MODULE_LANDING"
    if canon == "/404":
        return "TPL.ERROR"
    if canon == "/mapa-site":
        return "TPL.SITEMAP"
    if canon == "/acessibilidade":
        return "TPL.ACCESSIBILITY"
    if canon in ("/quiz", "/flashcards", "/trilhas", "/educacao", "/nanda"):
        return "TPL.HUB" if canon in ("/quiz", "/educacao") else "TPL.LISTING"
    return "TPL.INSTITUTIONAL"


def extract_seo(html_path: Path) -> tuple[str, str]:
    html = html_path.read_text(encoding="utf-8")
    title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html, re.I)
    title = title_m.group(1).strip() if title_m else "Calculadoras de Enfermagem"
    desc = desc_m.group(1).strip() if desc_m else f"Página {html_path.parent.name} — NKOS 2026."
    return title, desc


def upsert_seo(seo: dict, canon: str, title: str, description: str, template_code: str) -> bool:
    for rec in seo["records"]:
        if rec.get("canonical_path") == canon:
            rec["title"] = title
            rec["description"] = description
            rec["updated_at"] = NOW
            rec["status"] = "active"
            if not rec.get("target_code"):
                rec["target_code"] = template_code
            return False
    seo_code = f"SEO.PAGE.{canon.strip('/').replace('/', '_').upper() or 'HOME'}"
    seo["records"].append({
        "uuid": str(uuid.uuid4()),
        "seo_code": seo_code[:80],
        "target_type": "page",
        "target_code": template_code,
        "title": title,
        "description": description,
        "canonical_path": canon,
        "og_type": "website",
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    })
    return True


def upsert_template(tpl: dict, canon: str, template_code: str, name: str) -> bool:
    for rec in tpl["records"]:
        if rec.get("reference_page") == canon or rec.get("template_code") == template_code:
            rec["status"] = "active"
            rec["updated_at"] = NOW
            rec["reference_page"] = canon
            return False
    layout_map = {
        "TPL.LANDING_HOME": "LAYOUT.MAIN",
        "TPL.HUB": "LAYOUT.HUB",
        "TPL.CLINICAL_TOOL": "LAYOUT.TOOL",
        "TPL.PRIVACY_CENTER": "LAYOUT.PRIVACY_CENTER",
        "TPL.SUSTAINABILITY_CENTER": "LAYOUT.SUSTAINABILITY_CENTER",
        "TPL.ACCESSIBILITY": "LAYOUT.INSTITUTIONAL",
        "TPL.SITEMAP": "LAYOUT.INSTITUTIONAL",
        "TPL.ERROR": "LAYOUT.INSTITUTIONAL",
        "TPL.LISTING": "LAYOUT.LISTING",
        "TPL.INSTITUTIONAL": "LAYOUT.INSTITUTIONAL",
    }
    tpl["records"].append({
        "uuid": str(uuid.uuid4()),
        "template_code": template_code,
        "name": name[:120],
        "layout_code": layout_map.get(template_code, "LAYOUT.INSTITUTIONAL"),
        "reference_page": canon,
        "status": "active",
        "edition": "2026",
        "updated_at": NOW,
    })
    return True


def main() -> int:
    manifest_path = OUT / "generation_manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: {manifest_path} not found. Run generate_website_pt.py first.")
        return 1

    manifest = load(manifest_path)
    pages = manifest.get("pages", [])
    if not pages:
        print("ERROR: generation manifest has no pages.")
        return 1

    seo = load(DATASETS / "metadata" / "seo_metadata.json")
    tpl = load(DATASETS / "metadata" / "templates.json")

    registry_records = []
    seo_added = seo_updated = tpl_added = 0

    for rel in sorted(pages):
        html_path = OUT / rel
        if not html_path.exists():
            continue
        canon = page_to_canonical(rel)
        title, description = extract_seo(html_path)
        template_code = infer_template(canon)
        page_name = title.split("|")[0].strip() or canon

        if upsert_seo(seo, canon, title, description, template_code):
            seo_added += 1
        else:
            seo_updated += 1

        if upsert_template(tpl, canon, template_code, page_name):
            tpl_added += 1

        depth = rel.count("/")
        registry_records.append({
            "page_code": f"PAGE.{canon.strip('/').replace('/', '.').upper() or 'HOME'}",
            "canonical_path": canon,
            "html_path": rel,
            "template_code": template_code,
            "title": title,
            "description": description,
            "depth": depth,
            "locale": "pt-BR",
            "status": "published",
            "updated_at": NOW,
        })

    seo["count"] = len(seo["records"])
    seo["updated_at"] = NOW
    tpl["count"] = len(tpl["records"])
    tpl["updated_at"] = NOW

    save(DATASETS / "metadata" / "seo_metadata.json", seo)
    save(DATASETS / "metadata" / "templates.json", tpl)

    registry = {
        "generated_at": NOW,
        "schema_version": "2026.1.0",
        "entity": "WebsitePageRegistry",
        "locale": "pt-BR",
        "source_manifest": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
        "page_count": len(registry_records),
        "tool_pages": manifest.get("tool_pages", 0),
        "records": registry_records,
    }
    save(DATASETS / "metadata" / "website_pages_registry.json", registry)

    status_path = DATASETS / "metadata" / "nkos_implementation_status.json"
    if status_path.exists():
        st = load(status_path)
        st.setdefault("website_pt", {})
        a11y_path = ROOT / "website" / "audit_a11y_pt_report.json"
        a11y_summary = {}
        if a11y_path.exists():
            a11y = load(a11y_path)
            a11y_summary = {
                "report": str(a11y_path.relative_to(ROOT)).replace("\\", "/"),
                "wcag_A": a11y.get("wcag_levels", {}).get("A", {}).get("status"),
                "wcag_AA": a11y.get("wcag_levels", {}).get("AA", {}).get("status"),
                "wcag_AAA": a11y.get("wcag_levels", {}).get("AAA", {}).get("status"),
                "audited_at": a11y.get("audited_at"),
            }
        st["website_pt"].update({
            "page_registry": "datasets/metadata/website_pages_registry.json",
            "page_count": len(registry_records),
            "tool_pages": manifest.get("tool_pages", 0),
            "seo_records": seo["count"],
            "template_records": tpl["count"],
            "last_sync_at": NOW,
            "generation_manifest": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
            "accessibility_audit": a11y_summary or None,
        })
        save(status_path, st)

    print("Website pages database sync complete")
    print(f"  Manifest pages: {len(pages)}")
    print(f"  Registry records: {len(registry_records)}")
    print(f"  SEO: +{seo_added} new, {seo_updated} updated (total {seo['count']})")
    print(f"  Templates: +{tpl_added} new (total {tpl['count']})")
    print(f"  Registry: datasets/metadata/website_pages_registry.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
