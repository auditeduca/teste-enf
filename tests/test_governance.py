"""Vault WORM, Lei 9.610 binding, ISO 8000 profile, masks, lineage, monitoring."""

import hashlib
import json

from engine.agents import run_extraction
from engine.generate import build
from engine.paths import ROOT, TOOLS_DIR
from engine.vault import compare_to_first, object_path, put_bytes, read_bytes
from validators.dual_render import check_parity
from validators.release_gate import evaluate_release
from validators.clinical_completeness import evaluate_catalog


def test_vault_same_hash_does_not_overwrite():
    payload = b"cko-worm-fixture-v1"
    first = put_bytes(payload, logical_id="TEST-WORM-001", source_path="tests/worm", media_type="text/plain")
    again = put_bytes(payload, logical_id="TEST-WORM-001", source_path="tests/worm", media_type="text/plain")
    assert first["sha256"] == hashlib.sha256(payload).hexdigest()
    assert again["existed"] is True
    assert again["changed_from_first"] is False
    assert read_bytes(first["sha256"]) == payload
    assert object_path(first["sha256"]).exists()


def test_vault_new_hash_keeps_first_copy_and_emits_drift():
    put_bytes(b"alpha-copy", logical_id="TEST-DRIFT-001", media_type="text/plain")
    second = put_bytes(b"beta-copy", logical_id="TEST-DRIFT-001", media_type="text/plain")
    assert second["changed_from_first"] is True
    cmp = compare_to_first("TEST-DRIFT-001", b"beta-copy")
    assert cmp["status"] == "SOURCE_DRIFT"
    assert cmp["first_sha256"] != cmp["observed_sha256"]
    assert read_bytes(cmp["first_sha256"]) == b"alpha-copy"


def test_extract_binds_rights_iso_lineage_without_fake_pass():
    run = run_extraction(network=False)
    assert run["publication"] == "HOLD"
    assert run["llm_used"] is False
    assert all(step.get("llm_used") is not True for step in run["steps"] if "llm_used" in step)

    rights = json.loads((ROOT / "cko_reg" / "rights_profile.json").read_text(encoding="utf-8"))
    works = json.loads((ROOT / "cko_md" / "work_registry.json").read_text(encoding="utf-8"))
    instruments = json.loads((ROOT / "cko_reg" / "instrument_registry.json").read_text(encoding="utf-8"))
    iso = json.loads((ROOT / "cko_md" / "iso8000_profile.json").read_text(encoding="utf-8"))
    lineage = json.loads((ROOT / "cko_md" / "lineage_registry.json").read_text(encoding="utf-8"))
    masks = json.loads((ROOT / "cko_reg" / "norm_masks.json").read_text(encoding="utf-8"))
    mask_run = json.loads((ROOT / "cko_inbox" / "extracted" / "mask_run.json").read_text(encoding="utf-8"))
    frameworks = json.loads((ROOT / "cko_core" / "framework_registry.json").read_text(encoding="utf-8"))
    fields = json.loads((ROOT / "cko_md" / "field_dictionary.json").read_text(encoding="utf-8"))
    shell = json.loads((ROOT / "cko_inbox" / "drive" / "site_shell" / "INVENTORY.json").read_text(encoding="utf-8"))

    assert instruments["instruments"][0]["business_key"] == "INS-LEI-9610-1998"
    assert instruments["instruments"][0]["clause_text"] == "NOT_COPIED_AS_PRODUCT_RULE"
    gotejamento = next(item for item in works["works"] if item["slug"] == "gotejamento")
    braden = next(item for item in works["works"] if item["slug"] == "braden")
    assert gotejamento["work_class"] == "ORIGINAL_CKO_CANDIDATE"
    assert gotejamento["assured"] is False
    assert braden["cko_copyright_claim"] == "FORBIDDEN"
    assert braden["in_data_tools"] is False
    assert not (TOOLS_DIR / "braden.json").exists()
    assert rights["gate"] == "HOLD"

    iso_fw = next(item for item in frameworks["frameworks"] if item["business_key"] == "FWK-ISO-8000-001")
    assert iso_fw["clause_text"] == "CLAUSE_TEXT_UNAVAILABLE"
    assert iso_fw["pgdados_hub_url"].endswith("/pgdados")
    assert iso["certified"] is False
    assert iso["iso_implemented"] is False
    assert iso["cko_profile_applied"] is True
    assert "ISO 8000 certified" not in json.dumps(iso)

    assert masks["authoring_policy"] == "ROBUST_AI_ALLOWED"
    assert masks["execution_policy"] == "SIMPLE_DETERMINISTIC_ONLY"
    assert masks["llm_as_checker"] == "FORBIDDEN"
    assert mask_run["llm_used"] is False

    assert fields["population"] == 11
    assert lineage["complete_count"] >= 4
    assert shell["hash_match"] is True
    assert shell["promoted_to_frontend"] is False
    assert "adsbygoogle" in (shell.get("forbidden_token_hits") or {})

    law = (ROOT / "cko_inbox" / "official" / "lei-9610.html").read_text(encoding="latin-1", errors="replace")
    assert "9.610" in law
    pointers = json.loads((ROOT / "cko_inbox" / "vault" / "pointers.json").read_text(encoding="utf-8"))
    assert "SRC-LEI-9610-1998" in pointers["pointers"]
    assert "SRC-SITE-SHELL" in pointers["pointers"]
    assert pointers["pointers"]["SRC-LEI-9610-1998"]["immutable"] is True


def test_frontend_lineage_and_monitoring_without_ads():
    run_extraction(network=False)
    build()
    tool = (ROOT / "render" / "fetch" / "tools" / "gotejamento.html").read_text(encoding="utf-8")
    inspector = (ROOT / "render" / "fetch" / "inspector.html").read_text(encoding="utf-8")
    monitoring = (ROOT / "render" / "fetch" / "admin" / "monitoring.html").read_text(encoding="utf-8")
    mdm = (ROOT / "render" / "fetch" / "admin" / "mdm.html").read_text(encoding="utf-8")
    frameworks = (ROOT / "render" / "fetch" / "admin" / "frameworks.html").read_text(encoding="utf-8")
    assert 'id="rastreio"' in tool
    assert "ORIGINAL_CKO_CANDIDATE" in tool
    assert "INS-LEI-9610-1998" in tool
    assert "adsbygoogle" not in tool
    assert "ORIGINAL_CKO_CANDIDATE" in inspector
    assert "SOURCE_DRIFT" in monitoring or "Nenhum evento" in monitoring or "eventos=" in monitoring
    assert "EXPECTED_REWRITE" in monitoring or "Fonte vs primeira cópia" in monitoring
    assert "FWK-ISO-8000-001" in frameworks or "ISO 8000" in frameworks
    assert "CLAUSE_TEXT_UNAVAILABLE" in frameworks
    assert "pgdados" in mdm.lower()
    assert "certified" in mdm.lower() or "ISO 8000" in mdm
    assert "ca-pub-6472730056006847" not in tool
    parity = check_parity()
    assert parity["status"] == "PASS"
    release = evaluate_release(evaluate_catalog(), parity)
    assert release["status"] == "HOLD"
