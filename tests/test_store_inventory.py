"""Store inventory agents classify Drive/Supabase without promoting HTML."""

from engine.store_inventory import classify_drive_file, inventory_drive, inventory_supabase, plan_fronts


def test_classify_does_not_promote_html_or_mega_zip():
    parecer = classify_drive_file({
        "id": "1OUlaOO-hvxKk7IHoiBoKWuJRg26hP3uC",
        "title": "CKO-MasterData-Parecer-360-v1.0.md",
        "mimeType": "text/markdown",
        "fileSize": "14581",
    })
    assert parecer["classification"] == "DISCOVERY_QUARANTINE"
    assert parecer["promotes_to_md"] is False
    grok = classify_drive_file({
        "id": "1VwN7LjxR30GbPctX6-Uq6IH7A-eh7idA",
        "title": "fH1ew2tMuINgm9Yt-grok-workspace.zip",
        "mimeType": "application/x-zip-compressed",
        "fileSize": "140316423",
    })
    assert grok["classification"] == "SKIP_BINARY_DUMP"
    shell = classify_drive_file({
        "id": "1HEOd0k5i_iBtereT_ob_T1q8qI9MzKKU",
        "title": "site-shell-calculadoras-enfermagem.zip",
        "mimeType": "application/zip",
        "fileSize": "82453",
    })
    assert shell["classification"] == "ALREADY_IN_CKO"
    completo = classify_drive_file({
        "id": "1QGdvsnUhKSr2XTQ03sJzWowKp8lQUxZf",
        "title": "site-shell-calculadoras-enfermagem-completo.zip",
        "mimeType": "application/zip",
        "fileSize": "296119",
    })
    assert completo["classification"] == "CANDIDATE_GAP"
    assert completo["action"] == "COMPARE_ONLY"


def test_inventory_agents_keep_schema_pending_and_plan_hold():
    from engine.paths import ROOT, TOOLS_DIR
    import json

    drive = inventory_drive()
    supabase = inventory_supabase()
    plan = plan_fronts()
    assert drive["promotes_to_md"] is False
    assert drive["do_not_unzip"] is True
    assert supabase["schema"] == "EVIDENCE_PENDING"
    assert supabase["sql_blocked"] is True
    assert plan["publication"] == "HOLD"
    assert plan["front_count"] == 19
    assert "F2" in plan["blocked"]
    assert "F12" in plan["hold"]
    fronts = json.loads((ROOT / "cko_md" / "fronts_plan.json").read_text(encoding="utf-8"))
    assert fronts["owner_unblock_ref"] == "MD-OWNER-UNBLOCK-001"
    assert fronts["library_api_map_ref"] == "MD-LIB-API-MAP-001"
    assert fronts["concept_renderer_ref"] == "MD-CONCEPT-RENDER-001"
    vaccines = json.loads((ROOT / "cko_inbox" / "extracted" / "vaccines_zip_inventory.json").read_text(encoding="utf-8"))
    assert vaccines["tool_id_count"] == 15
    assert vaccines["claimed_library_count_32"] == "EVIDENCE_PENDING"
    assert vaccines.get("pattern_candidate") is True
    drive_inv = json.loads((ROOT / "cko_inbox" / "extracted" / "drive_inventory.json").read_text(encoding="utf-8"))
    menu = next(item for item in drive_inv["files"] if item["id"] == "1b0ORWmyAaYk6b_bW112RVcuARtWwRd0T")
    assert menu["classification"] == "FOLDER_OBSERVED"
    assert "mega-menu" in menu["reason"]
    vac_file = next(item for item in drive_inv["files"] if item["id"] == "1E9OB0AKR0m2Hbeknf43Htwo-fXob6cP9")
    assert vac_file["classification"] == "CANDIDATE_GAP"
    assert vac_file["action"] == "COMPARE_ONLY"
    libs = json.loads((ROOT / "cko_inbox" / "extracted" / "templates_bibliotecas_compare.json").read_text(encoding="utf-8"))
    assert libs["observed_counts"]["clinical_object_types_05"] == 24
    assert libs["nnn_files_in_zip"]["nanda-00046.json"] == "QUARANTINE"
    assert not (TOOLS_DIR / "nanda-00046.json").exists()
