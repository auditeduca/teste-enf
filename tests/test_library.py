"""Government library, curriculum, API probe, and inbox SQLite."""

import json
import sqlite3

from engine.agents import run_extraction
from engine.generate import build
from engine.paths import ROOT, TOOLS_DIR


def test_library_curriculum_requires_md_and_reg_and_keeps_braden_out():
    run = run_extraction(network=False)
    lib = json.loads((ROOT / "cko_md" / "resource_library.json").read_text(encoding="utf-8"))
    curr = json.loads((ROOT / "cko_md" / "content_curriculum.json").read_text(encoding="utf-8"))
    agencies = json.loads((ROOT / "cko_md" / "agency_registry.json").read_text(encoding="utf-8"))
    adapters = json.loads((ROOT / "cko_md" / "api_adapter_registry.json").read_text(encoding="utf-8"))
    alerts = json.loads((ROOT / "cko_assurance" / "freshness_alerts.json").read_text(encoding="utf-8"))
    qual = json.loads((ROOT / "cko_reg" / "source_qualification.json").read_text(encoding="utf-8"))

    assert agencies["population"] >= 4
    assert all(item.get("uuid") is None for item in agencies["agencies"])
    assert all(item.get("md_ref") and item.get("reg_ref") for item in lib["resources"])
    assert all(item.get("md_ref") and item.get("reg_ref") for item in qual["qualifications"])
    assert lib["publication"] == "HOLD"
    assert curr["llm_authored"] is False
    assert curr["publication"] == "HOLD"
    slugs = {unit["tool_slug"] for unit in curr["units"]}
    assert slugs == {"gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"}
    assert "braden" not in slugs
    assert not (TOOLS_DIR / "braden.json").exists()
    assert curr["pending_high_count"] >= 4
    assert all(item.get("severity") == "ALTA" for item in curr["pending_high"])
    dim = [unit for unit in curr["units"] if unit["tool_slug"] == "dimensionamento"]
    assert any((unit.get("body") or {}).get("status") == "HOLD" for unit in dim)
    assert adapters["production_api"] is False
    assert all(item.get("base_url") in {None, item.get("base_url")} for item in adapters.get("adapters") or [])
    assert all(item.get("base_url") is None or item.get("online") for item in adapters.get("adapters") or [])
    assert alerts["email_dispatch"] is False
    assert alerts["alta_count"] >= 1
    lib_step = next(step for step in run["steps"] if step["agent_id"] == "AG-LIBRARY-CATALOG")
    assert lib_step.get("promotes_to_md") is False
    assert run["publication"] == "HOLD"


def test_ops_sqlite_mirrors_md_reg_and_biblioteca_renders():
    run_extraction(network=False)
    build()
    db = ROOT / "cko_inbox" / "cko_ops.sqlite"
    assert db.exists()
    conn = sqlite3.connect(db)
    missing = conn.execute(
        "SELECT COUNT(*) FROM resources WHERE md_ref IS NULL OR md_ref='' OR reg_ref IS NULL OR reg_ref=''"
    ).fetchone()[0]
    units = conn.execute("SELECT COUNT(*) FROM content_units").fetchone()[0]
    conn.close()
    assert missing == 0
    assert units == 25
    html = (ROOT / "render" / "fetch" / "biblioteca.html").read_text(encoding="utf-8")
    assert "Biblioteca de recursos" in html
    assert "PENDENCIA_ALTA" in html or "ALTA" in html
    assert "Congresso" in html or "legislação federal" in html.lower()
    assert "PLP" in html
    assert "adsbygoogle" not in html
    assert 'type="email"' not in html
    assert "braden.html" not in html
    index = (ROOT / "render" / "fetch" / "index.html").read_text(encoding="utf-8")
    assert "Biblioteca" in index
    admin_lib = (ROOT / "render" / "fetch" / "admin" / "library.html").read_text(encoding="utf-8")
    admin_api = (ROOT / "render" / "fetch" / "admin" / "apis.html").read_text(encoding="utf-8")
    assert "Nenhuma alteração de RLS" in (ROOT / "render" / "fetch" / "admin" / "database.html").read_text(encoding="utf-8")
    assert "Currículo" in admin_lib or "currículo" in admin_lib.lower()
    assert "base_url" in admin_api
