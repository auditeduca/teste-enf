"""Admin Studio modules, Studio CMS quarantine, and control plane."""

import json

from engine.admin_site import inventory_tables, studio_map
from engine.control_plane import git_status, is_loopback, prepare_deploy
from engine.generate import build
from engine.paths import ROOT
from validators.dual_render import check_parity
from validators.release_gate import evaluate_release
from validators.clinical_completeness import evaluate_catalog


def test_studio_map_is_quarantined_not_published():
    studio = studio_map()
    assert studio["quarantine"] is True
    assert studio["epistemic_status"] == "SOURCE_DERIVED"
    assert studio["images_in_conversation"]["status"] == "NOT_FOUND"
    braden = next(item for item in studio["tabela_itens_logicos"] if item["id_logico"] == "BRADEN")
    assert braden["cko_status"] == "QUARANTINED"
    assert braden["in_data_tools"] is False
    assert braden["uuid"] is None
    slugs = {path.stem for path in (ROOT / "data" / "tools").glob("*.json")}
    assert "braden" not in slugs
    assert studio["visao_geral_item"]["qualidade_conteudo"]["epistemic_status"] == "DOCUMENT_CLAIM"


def test_build_emits_admin_modules_and_keeps_release_hold():
    written = build()
    names = {path.name for path in written}
    for name in (
        "admin.html",
        "database.html",
        "catalog.html",
        "pipeline.html",
        "layers.html",
        "validations.html",
        "agents.html",
        "monitoring.html",
        "backlog.html",
        "design-system.html",
        "renderer.html",
        "deploy.html",
        "studio_cms_map.v1.json",
        "design_token_registry.json",
        "admin-control.js",
    ):
        assert name in names
    fetch_admin = (ROOT / "render" / "fetch" / "admin.html").read_text(encoding="utf-8")
    catalog = (ROOT / "render" / "fetch" / "admin" / "catalog.html").read_text(encoding="utf-8")
    design = (ROOT / "render" / "fetch" / "admin" / "design-system.html").read_text(encoding="utf-8")
    deploy = (ROOT / "render" / "fetch" / "admin" / "deploy.html").read_text(encoding="utf-8")
    database = (ROOT / "render" / "fetch" / "admin" / "database.html").read_text(encoding="utf-8")
    assert "CKO Studio" in fetch_admin
    assert "Layer Registry (44)" in fetch_admin
    assert "QUARANTINED" in catalog
    assert "STUDIO-CAND-BRADEN" in catalog
    assert "EVIDENCE_PENDING" in design
    assert "git push é FORBIDDEN" in deploy
    assert "Nenhuma alteração de RLS" in database
    assert "cdn.jsdelivr" not in fetch_admin.lower()
    parity = check_parity()
    assert parity["status"] == "PASS"
    release = evaluate_release(evaluate_catalog(), parity)
    assert release["status"] == "HOLD"


def test_control_plane_git_status_and_prepare_does_not_push():
    status = git_status()
    assert status["push"] == "FORBIDDEN"
    assert status["epistemic_status"] == "OBSERVED"
    prepared = prepare_deploy()
    assert prepared["push"] == "FORBIDDEN"
    assert prepared["uuid"] is None
    path = ROOT / prepared["path"]
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["action"] == "DEPLOY_PREPARE"
    assert is_loopback("127.0.0.1")
    assert not is_loopback("8.8.8.8")


def test_github_json_inventory_is_non_empty():
    rows = inventory_tables()
    paths = {item["path"] for item in rows}
    assert "cko_core/layer_registry.json" in paths
    assert "cko_md/entity_type_registry.json" in paths
    assert "cko_reg/authority_classes.json" in paths
    assert any(item["schema"] == "domain_candidate" for item in rows)
