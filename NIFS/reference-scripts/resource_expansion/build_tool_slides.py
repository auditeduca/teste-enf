"""Gera JSON de slides técnicos por ferramenta (padrão website)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY = ROOT / "datasets" / "master-data" / "resource-expansion" / "slides_registry.json"
SLIDES_DIR = ROOT / "website" / "assets" / "data" / "slides"
CATALOG = ROOT / "datasets" / "clinical" / "clinical_tools_catalog.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tool_name(tool_code: str, catalog: dict) -> str:
    for r in catalog.get("records", []):
        if r.get("tool_code") == tool_code:
            return r.get("name", tool_code)
    return tool_code


def build_deck(deck: dict, catalog: dict) -> dict:
    name = _tool_name(deck["tool_code"], catalog)
    sections = deck.get("sections", [])
    slides = []
    for i, sec in enumerate(sections, 1):
        slides.append({
            "slide_number": i,
            "section_id": sec,
            "title_pt": sec.replace("_", " ").title(),
            "body_pt": f"Conteúdo técnico — {name}. Evidência Grau A pendente de revisão agente.",
            "layout": "title_body" if i > 1 else "title_hero",
            "evidence_grade_required": "A",
            "status": "scaffold",
        })
    return {
        "schema_version": "2026.2.8",
        "entity_code": deck["entity_code"],
        "tool_code": deck["tool_code"],
        "slug": deck["slug"],
        "deck_title_pt": f"Slides — {name}",
        "generated_at": _now(),
        "slide_count": len(slides),
        "template": deck.get("template", "TPL.SLIDES_TOOL"),
        "canonical_url": deck.get("canonical_url"),
        "slides": slides,
    }


def main(*, limit: int = 100) -> dict:
    if not REGISTRY.is_file():
        from build_registry import main as build_main  # noqa: WPS433

        build_main()
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    pt_dir = ROOT / "website" / "pt" / "assets" / "data" / "slides"
    pt_dir.mkdir(parents=True, exist_ok=True)
    built = 0
    for deck in reg.get("decks", [])[:limit]:
        doc = build_deck(deck, catalog)
        path = SLIDES_DIR / f"{deck['slug']}.json"
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (pt_dir / f"{deck['slug']}.json").write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        built += 1
    print(f"slides JSON: {built} decks em {SLIDES_DIR}")
    return {"built": built}


if __name__ == "__main__":
    main()
