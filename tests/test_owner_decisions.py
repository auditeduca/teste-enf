"""Owner decisions 2026-08-25: F2 HOLD, F12 B, F20 APPROVED, F21 enviado."""

import json

from engine.clinical_dict import evaluate_clinical_dict
from engine.generate import build
from engine.paths import ROOT, TOOLS_DIR
from engine.rights import bind_nnn_opt_b
from engine.store_inventory import plan_fronts
from engine.who_i18n import evaluate_who_i18n


def _unblock(action_id: str) -> dict:
    payload = json.loads((ROOT / "cko_md" / "owner_unblock.json").read_text(encoding="utf-8"))
    return next(item for item in payload["actions"] if item["id"] == action_id)


def test_f2_hold_does_not_collect_password_or_invent_schema():
    sql = _unblock("UNBLOCK-SUPABASE-SQL")
    assert sql["status"] == "HOLD"
    assert sql["owner_decision"] == "HOLD"
    oauth = _unblock("UNBLOCK-SUPABASE-MCP-OAUTH")
    assert oauth["status"] == "SKIPPED_BY_OWNER"
    plan = plan_fronts()
    assert "F2" in plan["hold"]
    assert "F2" not in plan["blocked"]
    fronts = json.loads((ROOT / "cko_md" / "fronts_plan.json").read_text(encoding="utf-8"))
    f2 = next(item for item in fronts["fronts"] if item["id"] == "F2")
    assert f2["status"] == "HOLD"
    assert f2["schema"] == "EVIDENCE_PENDING"
    inv = json.loads((ROOT / "cko_inbox" / "extracted" / "supabase_inventory.json").read_text(encoding="utf-8"))
    assert inv["schema"] == "EVIDENCE_PENDING"


def test_f12_opt_b_identity_codes_without_licensed_text():
    nnn = _unblock("UNBLOCK-NNN-LICENSE")
    assert nnn["status"] == "DECIDED_B"
    assert nnn["owner_decision"] == "B"
    assert nnn["chosen"] == ["OPT-B-IDENTIFIERS", "OPT-D-DEEPLINK"]
    result = bind_nnn_opt_b()
    assert result["owner_decision"] == "B"
    assert result["licensed_text"] is False
    catalog = json.loads((ROOT / "cko_md" / "nnn_identity_catalog.json").read_text(encoding="utf-8"))
    codes = {item["code"] for item in catalog["identities"]}
    assert codes == {"00046", "2312", "0401"}
    systems = {item["system"] for item in catalog["identities"]}
    assert systems == {"NANDA", "NIC", "NOC"}
    for item in catalog["identities"]:
        assert item["canonical_label"] is None
        assert item["display_label"] == "texto indisponível (licença)"
        assert item["licensed_text"] is False
        assert item["in_data_tools"] is False
        assert item["deep_link"] in {"https://nanda.org/", "https://www.elsevier.com/"}
        identities_blob = json.dumps(catalog["identities"])
        assert "definingCharacteristics" not in identities_blob
        assert "Impaired" not in identities_blob
        assert "definingCharacteristics" not in json.dumps(catalog)
    assert not (TOOLS_DIR / "nanda-00046.json").exists()
    assert not (TOOLS_DIR / "nic-2312.json").exists()
    assert not (TOOLS_DIR / "noc-0401.json").exists()
    arch = json.loads((ROOT / "cko_md" / "nnn_rights_architecture.json").read_text(encoding="utf-8"))
    assert arch["owner_decision"] == "B"
    assert arch["implemented"] is True
    assert arch["publication"] == "HOLD"
    assert "UNBLOCK-NNN-LICENSE" in arch["gap"]
    plan = plan_fronts()
    assert "F12" not in plan["hold"]
    fronts = json.loads((ROOT / "cko_md" / "fronts_plan.json").read_text(encoding="utf-8"))
    f12 = next(item for item in fronts["fronts"] if item["id"] == "F12")
    assert f12["status"] == "REGISTERED"


def test_f20_key_approved_selector_unwired():
    i18n_action = _unblock("UNBLOCK-I18N-TRANSLATION")
    assert i18n_action["status"] == "APPROVED"
    assert i18n_action["approved_key"] == "who.en+local.pt-BR"
    result = evaluate_who_i18n()
    assert result["owner_decision"] == "APPROVED"
    assert result["translation_gate"] == "HOLD"
    assert result["wired_to_frontend"] is False
    envelopes = json.loads((ROOT / "cko_md" / "translation_envelopes.json").read_text(encoding="utf-8"))
    assert envelopes["owner_decision"] == "APPROVED"
    assert envelopes["translation_gate"] == "HOLD"
    assert envelopes["wired_to_frontend"] is False
    slugs = {item["tool_slug"] for item in envelopes["envelopes"]}
    assert slugs == {"gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"}
    for item in envelopes["envelopes"]:
        assert item["who_local_key"] == "who.en+local.pt-BR"
        assert item["src_strings"] is None
        assert item["trg_strings"] is None
        assert item["wired_to_frontend"] is False
    who = json.loads((ROOT / "cko_md" / "who_i18n_modulation.json").read_text(encoding="utf-8"))
    assert who["owner_decision"] == "APPROVED"
    assert who["translation_gate"] == "HOLD"
    plan = plan_fronts()
    assert "F20" not in plan["hold"]
    fronts = json.loads((ROOT / "cko_md" / "fronts_plan.json").read_text(encoding="utf-8"))
    f20 = next(item for item in fronts["fronts"] if item["id"] == "F20")
    assert f20["status"] == "REGISTERED"


def test_f21_zip_received_sheets_still_missing():
    sheets = _unblock("UNBLOCK-DICT-SHEETS")
    assert sheets["status"] == "RECEIVED"
    assert sheets["drive_file_id"] == "152MrVMQHG76G8nVN0wMMqedvTpHzfEB-"
    result = evaluate_clinical_dict()
    assert result["promoted_to_data_tools"] is False
    catalog = json.loads((ROOT / "cko_md" / "clinical_dictionary_catalog.json").read_text(encoding="utf-8"))
    assert catalog["owner_sent"] is True
    assert catalog["drive_file_id"] == "152MrVMQHG76G8nVN0wMMqedvTpHzfEB-"
    assert catalog["sheets_content_meta"] == "MISSING"
    assert catalog["runtime_fld_policy"] == "ONLY_EXISTING_FLD"
    assert catalog["index_claimed_missing_sheets"] == ["Content_Schemas", "Meta_Schemas"]
    assert not (TOOLS_DIR / "braden.json").exists()
    plan = plan_fronts()
    assert "F21" not in plan["hold"]
    fronts = json.loads((ROOT / "cko_md" / "fronts_plan.json").read_text(encoding="utf-8"))
    f21 = next(item for item in fronts["fronts"] if item["id"] == "F21")
    assert f21["status"] == "COMPARE_ONLY"


def test_admin_surfaces_owner_decisions_without_wiring_i18n():
    bind_nnn_opt_b()
    evaluate_who_i18n()
    evaluate_clinical_dict()
    plan_fronts()
    build()
    agents = (ROOT / "render" / "fetch" / "admin" / "agents.html").read_text(encoding="utf-8")
    assert ">F2<" in agents or "F2" in agents
    assert "HOLD" in agents
    assert "DECIDED_B" in agents or "B" in agents
    library = (ROOT / "render" / "fetch" / "admin" / "library.html").read_text(encoding="utf-8")
    assert "00046" in library
    assert "2312" in library
    assert "0401" in library
    assert "texto indisponível (licença)" in library
    assert "https://nanda.org/" in library
    assert "definingCharacteristics" not in library
    assert "Content_Schemas" in library
    home = (ROOT / "render" / "fetch" / "index.html").read_text(encoding="utf-8")
    assert 'data-owner-i18n="APPROVED"' in home
    assert 'data-i18n-gate="HOLD"' in home
    assert "who.en+local.pt-BR · i18n HOLD" in home
    locales = (ROOT / "render" / "fetch" / "admin" / "locales.html").read_text(encoding="utf-8")
    assert "APPROVED" in locales
    assert "HOLD" in locales
