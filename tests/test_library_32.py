"""F10 COMPARE 11+24+15 accepted; claimed 32 stays EVIDENCE_PENDING. F4 PGDADOS probe."""

import json

from engine.agents import run_extraction
from engine.generate import build
from engine.govlib import catalog_library, catalog_pgdados, compare_claimed_32
from engine.paths import ROOT, TOOLS_DIR
from engine.store_inventory import plan_fronts


def test_f10_compare_accepted_claimed_32_still_pending():
    catalog_library()
    compare = json.loads((ROOT / "cko_md" / "library_32_compare.json").read_text(encoding="utf-8"))
    assert compare["business_key"] == "MD-LIB-32-COMPARE-001"
    assert compare["owner_decision"] == "COMPARE_ACCEPTED"
    assert compare["claimed_32_libraries"] == "EVIDENCE_PENDING"
    assert compare["claimed_32_equals_any_observed_sum"] is False
    counts = compare["observed_counts"]
    assert counts["device_library_slugs"] == 11
    assert counts["clinical_object_types"] == 24
    assert counts["cal_vac_tools"] == 15
    assert counts["pages_full_biblioteca_hubs"] == 5
    for value in compare["observed_sums"].values():
        assert value != 32
    assert all(flag is False for flag in compare["observed_sum_equals_32"].values())
    quarantine = compare.get("quarantine") or {}
    assert quarantine.get("nanda-00046.json") == "QUARANTINE"
    assert "definingCharacteristics" not in json.dumps(quarantine)
    libmap = json.loads((ROOT / "cko_md" / "library_api_map.json").read_text(encoding="utf-8"))
    assert libmap["claimed_32_libraries"] == "EVIDENCE_PENDING"
    assert libmap["owner_decision"] == "COMPARE_ACCEPTED"
    assert libmap["library_32_compare_ref"] == "MD-LIB-32-COMPARE-001"
    unblock = json.loads((ROOT / "cko_md" / "owner_unblock.json").read_text(encoding="utf-8"))
    action = next(item for item in unblock["actions"] if item["id"] == "UNBLOCK-32-LIST")
    assert action["status"] == "COMPARE_ACCEPTED"
    assert action["owner_decision"] == "COMPARE_ACCEPTED"
    plan = plan_fronts()
    fronts = json.loads((ROOT / "cko_md" / "fronts_plan.json").read_text(encoding="utf-8"))
    f10 = next(item for item in fronts["fronts"] if item["id"] == "F10")
    assert f10["owner_decision"] == "COMPARE_ACCEPTED"
    assert f10["status"] == "COMPARE_ONLY"
    assert "F10" not in plan["hold"]
    assert not (TOOLS_DIR / "CAL-VAC-001.json").exists()
    assert not (TOOLS_DIR / "braden.json").exists()
    assert not (TOOLS_DIR / "nanda-00046.json").exists()


def test_pgdados_parte3_and_cartilhas_45_remain_pending_after_offline_catalog():
    gov = json.loads((ROOT / "cko_inbox" / "extracted" / "gov_pages.json").read_text(encoding="utf-8"))
    catalog_pgdados(gov.get("pages") or [])
    pgd = json.loads((ROOT / "cko_md" / "pgdados_program.json").read_text(encoding="utf-8"))
    parts = {item.get("part"): item for item in pgd.get("guia_parts") or []}
    vols = {item.get("volume"): item for item in pgd.get("cartilhas") or []}
    assert parts[3]["status"] == "EVIDENCE_PENDING"
    assert parts[3].get("url") is None
    assert vols[4]["status"] == "EVIDENCE_PENDING"
    assert vols[5]["status"] == "EVIDENCE_PENDING"
    last = pgd.get("last_html_probe") or {}
    assert last.get("parte3_pdf_href") is False
    assert last.get("cartilha_v4_pdf_href") is False
    assert last.get("cartilha_v5_pdf_href") is False
    probe = json.loads((ROOT / "cko_md" / "pgdados_pending_probe.json").read_text(encoding="utf-8"))
    assert probe["parte3_pdf_href"] is False
    assert probe["cartilha_v4_pdf_href"] is False
    assert probe["cartilha_v5_pdf_href"] is False
    if probe.get("network"):
        assert probe.get("hub_http_status") == 200
        assert probe.get("guia_http_status") == 200
        assert probe.get("guia_parte3_label_mentioned") is True
        assert probe.get("cartilha_v4_label_mentioned") is True
        assert probe.get("cartilha_v5_label_mentioned") is True
    blob = json.dumps(pgd)
    assert "mwpt.com.br" not in blob
    assert "abnt-nbr" not in blob.lower()


def test_admin_library_surfaces_32_compare_and_pgdados_pending():
    run_extraction(network=False)
    build()
    html = (ROOT / "render" / "fetch" / "admin" / "library.html").read_text(encoding="utf-8")
    assert "MD-LIB-32-COMPARE-001" in html
    assert "COMPARE_ACCEPTED" in html
    assert "EVIDENCE_PENDING" in html
    assert "equals 32" in html
    assert "Guia Parte 3" in html
    assert "Cartilha vol. 4" in html
    assert "Cartilha vol. 5" in html
    agents = (ROOT / "render" / "fetch" / "admin" / "agents.html").read_text(encoding="utf-8")
    assert "UNBLOCK-32-LIST" in agents
    assert "COMPARE_ACCEPTED" in agents
    copied = json.loads((ROOT / "render" / "fetch" / "admin" / "library_32_compare.json").read_text(encoding="utf-8"))
    assert copied["claimed_32_libraries"] == "EVIDENCE_PENDING"
    assert copied["owner_decision"] == "COMPARE_ACCEPTED"
    phase = json.loads((ROOT / "cko_md" / "layer_md_reg_phase.json").read_text(encoding="utf-8"))
    l60 = next(item for item in phase["layers"] if item["layer_code"] == "L60")
    assert "cko_md/library_32_compare.json" in l60["md"]["evidence_ok"]
    assert l60["owner_unblock"] == "UNBLOCK-32-LIST"
    assert "COMPARE_ACCEPTED" in l60["gap"]
    l20 = next(item for item in phase["layers"] if item["layer_code"] == "L20")
    assert "Parte 3" in l20["gap"]
