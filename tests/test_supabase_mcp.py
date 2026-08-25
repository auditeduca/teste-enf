"""Supabase MCP is documented read-only. Schema listing remains EVIDENCE_PENDING."""

import json

from engine.generate import build
from engine.paths import ROOT
from engine.store_inventory import inventory_supabase, plan_fronts

MCP_URL = (
    "https://mcp.supabase.com/mcp?project_ref=yskgekcjzndptzmnjfke"
    "&read_only=true&features=docs%2Caccount%2Cdatabase%2Cdebugging%2Cdevelopment%2Cfunctions%2Cbranching"
)
OWNER_REF = "yskgekcjzndptzmnjfke"
FORBIDDEN_KEY_PREFIX = "sb_publishable_8PBIVYR"


def test_mcp_json_is_read_only_and_scoped_to_owner_project():
    for rel in (".cursor/mcp.json", ".mcp.json"):
        payload = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        url = payload["mcpServers"]["supabase"]["url"]
        assert url == MCP_URL
        assert "read_only=true" in url
        assert f"project_ref={OWNER_REF}" in url
        blob = json.dumps(payload)
        assert FORBIDDEN_KEY_PREFIX not in blob
        assert "service_role" not in blob


def test_agent_skills_installed_without_committing_publishable_key():
    assert (ROOT / ".agents" / "skills" / "supabase" / "SKILL.md").is_file()
    assert (ROOT / ".agents" / "skills" / "supabase-postgres-best-practices" / "SKILL.md").is_file()
    lock = json.loads((ROOT / "skills-lock.json").read_text(encoding="utf-8"))
    assert set(lock["skills"]) >= {"supabase", "supabase-postgres-best-practices"}
    probe = json.loads((ROOT / "cko_inbox" / "extracted" / "supabase_mcp_probe.json").read_text(encoding="utf-8"))
    assert probe["business_key"] == "IPE-SUPABASE-MCP-001"
    assert probe["read_only"] is True
    assert probe["project_ref"] == OWNER_REF
    assert probe["schema"] == "EVIDENCE_PENDING"
    assert probe["publishable_key"]["committed"] is False
    assert probe["probes"]["auth_v1_settings_publishable"]["http_status"] == 200
    assert probe["probes"]["rest_v1_publishable"]["http_status"] == 401
    tracked = (ROOT / "cko_inbox" / "extracted" / "supabase_mcp_probe.json").read_text(encoding="utf-8")
    assert FORBIDDEN_KEY_PREFIX not in tracked


def test_inventory_keeps_schema_pending_and_records_owner_ref():
    result = inventory_supabase()
    plan = plan_fronts()
    assert result["schema"] == "EVIDENCE_PENDING"
    assert result["sql_blocked"] is True
    assert "F2" in plan["blocked"]
    inv = json.loads((ROOT / "cko_inbox" / "extracted" / "supabase_inventory.json").read_text(encoding="utf-8"))
    refs = {item["ref"] for item in inv["projects"]}
    assert OWNER_REF in refs
    assert inv["mcp"]["oauth_this_agent"] == "PERMISSION_DENIED"
    unblock = json.loads((ROOT / "cko_md" / "owner_unblock.json").read_text(encoding="utf-8"))
    ids = {item["id"] for item in unblock["actions"]}
    assert "UNBLOCK-SUPABASE-MCP-OAUTH" in ids
    assert "UNBLOCK-SUPABASE-SQL" in ids


def test_admin_database_surfaces_mcp_without_wiring_schema():
    build()
    html = (ROOT / "render" / "fetch" / "admin" / "database.html").read_text(encoding="utf-8")
    assert OWNER_REF in html
    assert "read_only" in html
    assert ".cursor/mcp.json" in html
    assert "28P01" in html
    assert FORBIDDEN_KEY_PREFIX not in html
