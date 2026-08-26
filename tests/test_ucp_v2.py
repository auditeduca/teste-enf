"""UCP v2.0 attachments stay COMPARE-only. They do not replace schemas/."""

import json

from engine.generate import build
from engine.paths import ROOT, TOOLS_DIR
from engine.store_inventory import plan_fronts
from engine.ucp_v2 import compare_ucp_v2, EXPECTED_SCHEMAS


def test_ucp_v2_compare_does_not_promote_into_schemas():
    result = compare_ucp_v2()
    assert result["agent_id"] == "AG-UCP-V2-COMPARE"
    assert result["promotes_to_md"] is False
    assert result["copied_into_schemas"] is False
    assert result["publication"] == "HOLD"
    assert result["schema_count"] == 11
    catalog = json.loads((ROOT / "cko_md" / "ucp_v2_compare.json").read_text(encoding="utf-8"))
    assert catalog["business_key"] == "MD-UCP-V2-COMPARE-001"
    assert catalog["uuid"] is None
    assert catalog["copied_into_schemas"] is False
    assert catalog["assured"] is False
    assert catalog["implemented"] is False
    assert catalog["status"] == "SOURCE_DERIVED"
    assert catalog["engine_authority_mode"] == "DERIVED_NOT_AUTHORITY"
    assert catalog["engine_authority_aligned"] is True
    assert catalog["missing_register_count"] == 10
    files = {item["file"] for item in catalog["schemas"]}
    assert files == set(EXPECTED_SCHEMAS)
    for item in catalog["schemas"]:
        assert item["present"] is True
        assert item["sha256"]
        assert item["copied_into_schemas"] is False
        assert item["draft"] == "https://json-schema.org/draft/2020-12/schema"
        assert item["policy"] == "POL-CKO-UCP-001-v2.0"
        assert not (ROOT / "schemas" / item["file"]).exists()
    existing_titles = {item["title"] for item in catalog["existing_schemas"]}
    assert "CKO Object" in existing_titles
    assert all(item.get("draft", "").endswith("draft-07/schema#") for item in catalog["existing_schemas"])
    missing_ids = {item["artifact_id"] for item in catalog["missing_from_register"]}
    missing_files = {item["file"] for item in catalog["missing_from_register"]}
    assert "audience-model" in missing_ids
    assert "PILOT-UCP-v2.0" in missing_ids
    assert "audience-model.json" in missing_files
    assert "pilot-catalog.json" in missing_files
    assert catalog["capability_count"] == 16
    assert all(item["runtime_status"] == "NOT_IMPLEMENTED" for item in catalog["capabilities"])
    gap_ids = {item["id"] for item in catalog["gaps"]}
    assert {"GAP-UCP-DRAFT", "GAP-UCP-NOT-PROMOTED", "GAP-UCP-MODELS-MISSING"} <= gap_ids
    plan = plan_fronts()
    assert plan["front_count"] == 24
    fronts = json.loads((ROOT / "cko_md" / "fronts_plan.json").read_text(encoding="utf-8"))
    f23 = next(item for item in fronts["fronts"] if item["id"] == "F23")
    assert f23["status"] == "COMPARE_ONLY"
    assert not (TOOLS_DIR / "braden.json").exists()
    blob = json.dumps(catalog)
    assert "definingCharacteristics" not in blob
    build()
    html = (ROOT / "render" / "fetch" / "admin" / "library.html").read_text(encoding="utf-8")
    assert "MD-UCP-V2-COMPARE-001" in html
    assert "urn:cko:schema:engine-contract:2.0" in html
    assert "CONTROLLED_CANDIDATE" in html or "COMPARE only" in html
    admin_json = json.loads((ROOT / "render" / "fetch" / "admin" / "ucp_v2_compare.json").read_text(encoding="utf-8"))
    assert admin_json["copied_into_schemas"] is False
