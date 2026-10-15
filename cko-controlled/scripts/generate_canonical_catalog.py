#!/usr/bin/env python3
"""Catalog canonical families: norms, tools, libraries (and related kinds).

Does not promote published tool payloads. Does not assign Vigente.
Does not write Drive. Does not emit one HTML file per library article.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PUBLIC = ROOT / "public"
SITE = REPO / "reference-website"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from canonical_kernel import render_catalog, validate_catalog  # noqa: E402

CANONICAL_KINDS = [
    "normative_instrument",
    "tool",
    "library_article",
    "simulado",
    "protocol",
    "checklist",
    "guideline",
    "template",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def scan_norms() -> list[dict]:
    folder = PUBLIC / "data" / "norms"
    rows = []
    if folder.is_dir():
        for path in sorted(folder.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "id": data.get("id") or path.stem,
                    "kind": "normative_instrument",
                    "template_id": data.get("template_id") or "norm-instrument",
                    "atoms_n": len(data.get("atoms") or []),
                    "governed_status": data.get("status") or "HOLD",
                    "source": str(path.relative_to(REPO)),
                }
            )
    return rows


def scan_tools() -> tuple[list[dict], int]:
    folder = SITE / "data" / "tools"
    rows = []
    published_n = 0
    for path in sorted(folder.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        observed = data.get("status") or "unknown"
        if observed == "published":
            published_n += 1
        rows.append(
            {
                "slug": data.get("slug") or path.stem,
                "name": (data.get("overview") or {}).get("name") or path.stem,
                "source": f"data/tools/{path.name}",
                "observed_payload_status": observed,
                "governed_status": "HOLD",
                "sha256": sha256_file(path),
                "template_id": "tool",
            }
        )
    return rows, published_n


def scan_library() -> tuple[int, int]:
    html_n = sum(1 for _ in (SITE / "biblioteca").rglob("*.html")) if (SITE / "biblioteca").is_dir() else 0
    catalog = SITE / "js" / "modules" / "data" / "biblioteca.json"
    stubs = 0
    if catalog.is_file():
        stubs = len((json.loads(catalog.read_text(encoding="utf-8")) or {}).get("libraryItems") or [])
    return html_n, stubs


def scan_simulados() -> list[str]:
    return sorted(path.name for path in SITE.glob("simulado*.html"))


def payload() -> dict:
    norms = scan_norms()
    tools, published_n = scan_tools()
    library_html_n, library_stubs_n = scan_library()
    simulados = scan_simulados()
    families = [
        {
            "id": "normative_instrument",
            "canonical": True,
            "template_id": "norm-instrument",
            "objects_n": len(norms),
            "atomized_n": len(norms),
            "governed_status": "VERIFY_PENDING",
            "materialization": "atoms_json",
        },
        {
            "id": "tool",
            "canonical": True,
            "template_id": "tool",
            "objects_n": len(tools),
            "atomized_n": len(tools),
            "governed_status": "HOLD",
            "materialization": "tool_json_projection",
            "observed_payload_status_published_n": published_n,
        },
        {
            "id": "library_article",
            "canonical": True,
            "template_id": "library-article",
            "objects_n": library_html_n,
            "atomized_n": 0,
            "governed_status": "HOLD",
            "materialization": "legacy_html_until_atoms",
            "catalog_stubs_n": library_stubs_n,
        },
        {
            "id": "simulado",
            "canonical": True,
            "template_id": "simulado",
            "objects_n": len(simulados),
            "atomized_n": 0,
            "governed_status": "HOLD",
            "materialization": "legacy_html_until_atoms",
        },
        {
            "id": "protocol",
            "canonical": True,
            "template_id": "protocol",
            "objects_n": 0,
            "atomized_n": 0,
            "governed_status": "HOLD",
            "materialization": "kind_declared_not_atomized",
        },
        {
            "id": "checklist",
            "canonical": True,
            "template_id": "checklist",
            "objects_n": 0,
            "atomized_n": 0,
            "governed_status": "HOLD",
            "materialization": "kind_declared_not_atomized",
        },
        {
            "id": "guideline",
            "canonical": True,
            "template_id": "guideline",
            "objects_n": 0,
            "atomized_n": 0,
            "governed_status": "HOLD",
            "materialization": "kind_declared_not_atomized",
        },
        {
            "id": "template",
            "canonical": True,
            "template_id": "template",
            "objects_n": 0,
            "atomized_n": 0,
            "governed_status": "HOLD",
            "materialization": "kind_declared_not_atomized",
        },
    ]
    return {
        "id": "CKO-CANONICAL-OBJECTS-HOLD",
        "kind": "canonical_object_catalog",
        "title": "Normas, ferramentas e bibliotecas são canónicas",
        "status": "HOLD",
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "assigns_vigencia": False,
        "canonical_promotion": False,
        "clinical_promotion": "DENIED",
        "b9": "HOLD / NOT_RELEASED",
        "drive_writes": 0,
        "supabase_ddl": 0,
        "invariant": "canonical ≠ published ≠ Vigente ≠ released. HTML is a projection of one template per kind.",
        "canonical_kinds": CANONICAL_KINDS,
        "families": families,
        "findings": [
            {
                "id": "FND-CANON-TOOL-PUBLISHED-DRIFT",
                "statement": f"{published_n} tool JSON files carry status=published. Universal Tool Policy keeps calculators PAUSED and implemented_n=0. Governed status remains HOLD.",
            },
            {
                "id": "FND-CANON-LIBRARY-HTML-ONLY",
                "statement": f"{library_html_n} biblioteca HTML files exist without article atoms. The kind is canonical; the next materialization is JSON atoms + library-article template, not more hand HTML.",
            },
            {
                "id": "FND-CANON-NORMS-VERIFY-PENDING",
                "statement": "The first normative instrument is atomized and VERIFY_PENDING. C001 and C002 remain open.",
            },
        ],
        "materialization": {
            "tool_index": tools,
            "norm_index": norms,
            "simulado_files": simulados,
            "pages_from_catalog": 1,
            "html_files_per_object": 0,
            "this_page_is_not_a_13th_runtime_page": True,
        },
    }


def generate() -> dict:
    doc = payload()
    errors = validate_catalog(doc)
    if errors:
        raise SystemExit("FAIL: " + "; ".join(errors))
    write_json(PUBLIC / "data" / "CKO-CANONICAL-OBJECTS-HOLD.json", doc)
    (PUBLIC / "cko-canonico.html").write_text(render_catalog(doc), encoding="utf-8")
    return doc


def main() -> None:
    doc = generate()
    families = {row["id"]: row["objects_n"] for row in doc["families"]}
    print("canonical HOLD", families)


if __name__ == "__main__":
    main()
