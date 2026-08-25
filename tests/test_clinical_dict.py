"""Drive clinical dictionary zip is COMPARE only. Pilot codes stay in data/tools."""

import json

from engine.clinical_dict import PILOT_CODES, compose_clinical_dict, evaluate_clinical_dict
from engine.generate import build
from engine.iso8000 import compose_field_dictionary, evaluate_profile
from engine.paths import ROOT, TOOLS_DIR
from engine.store_inventory import classify_drive_file


def test_drive_zip_classifies_as_candidate_gap_not_md():
    row = classify_drive_file({
        "id": "152MrVMQHG76G8nVN0wMMqedvTpHzfEB-",
        "title": "Dicionario clinico.zip",
        "mimeType": "application/x-zip-compressed",
        "fileSize": "3062527",
    })
    assert row["classification"] == "CANDIDATE_GAP"
    assert row["promotes_to_md"] is False
    assert row["action"] == "COMPARE_ONLY"


def test_clinical_dict_catalog_keeps_pilot_codes_and_rejects_braden():
    result = evaluate_clinical_dict()
    assert result["agent_id"] == "AG-CLIN-DICT"
    assert result["promoted_to_data_tools"] is False
    assert result["braden_in_data_tools"] is False
    assert not (TOOLS_DIR / "braden.json").exists()
    catalog = json.loads((ROOT / "cko_md" / "clinical_dictionary_catalog.json").read_text(encoding="utf-8"))
    assert catalog["business_key"] == "MD-CLIN-DICT-001"
    assert catalog["publication"] == "HOLD"
    assert catalog["identity_conflict"]["adopt_uuid_v4"] is False
    assert catalog["do_not_merge_21_with_44"] is True
    assert catalog["dictionary_field_count"] >= 160
    assert catalog["new_tool_name_count"] == 77
    codes = {item["slug"]: item for item in catalog["pilot_codes"]}
    assert codes["gotejamento"]["code"] == PILOT_CODES["gotejamento"]
    assert codes["meows"]["code"] == PILOT_CODES["meows"]
    assert codes["gotejamento"]["relation"] == "MATCH_NAME"
    assert codes["dimensionamento"]["in_data_tools"] is True
    assert "Braden" in catalog["third_party_scale_tokens"] or "braden" in {
        item.lower() for item in catalog["third_party_scale_tokens"]
    }
    blob = json.dumps(catalog)
    assert "ISO 8000 certified" not in blob
    assert catalog["identity_conflict"]["clause_text"] == "CLAUSE_TEXT_UNAVAILABLE"


def test_field_dictionary_includes_drive_named_hold_fields():
    keys = {item["business_key"] for item in compose_field_dictionary()["fields"]}
    assert "FLD-TOOL-CODE" in keys
    assert "FLD-TOOL-SLUG" in keys
    assert "FLD-CLIN-DICT-CAMPO" in keys
    assert "FLD-ID-SCHEME" in keys
    assert "FLD-REF-ACCESSED" in keys
    assert "FLD-RND-MODE" in keys
    for field in compose_field_dictionary()["fields"]:
        if field["business_key"].startswith("FLD-REF-") or field["business_key"].startswith("FLD-RND-"):
            assert field["status"] == "HOLD"
            assert field["iso_clause_text"] == "CLAUSE_TEXT_UNAVAILABLE"


def test_iso_profile_clinical_dict_test_and_admin_library():
    evaluate_clinical_dict()
    result = evaluate_profile()
    ids = {item["id"]: item["status"] for item in result["tests"]}
    assert ids["ISO8000-CKO-CLIN-DICT"] == "PASS"
    assert result["certified"] is False
    build()
    library = (ROOT / "render" / "fetch" / "admin" / "library.html").read_text(encoding="utf-8")
    assert "Dicionário clínico Drive" in library
    assert "CALC-GOTEJAMENTO-001" in library
    assert "SCALE-MEOWS-001" in library
    mdm = (ROOT / "render" / "fetch" / "admin" / "mdm.html").read_text(encoding="utf-8")
    assert "FLD-TOOL-CODE" in mdm
    assert "FLD-REF-ACCESSED" in mdm
    assert not (TOOLS_DIR / "braden.json").exists()
    assert compose_clinical_dict()["promoted_to_data_tools"] is False
