"""Register /api/v1 Nursing Knowledge API routes on Flask app."""
from __future__ import annotations

from flask import jsonify, request

from calculator_service import calc_drip_rate, run_calculator
from clinical_service import get_calculator, get_scale, glossary, list_calculators, list_protocols, list_scales
from extended_services import (
    agent_run,
    get_article,
    get_career_path,
    get_education_path,
    job_match,
    list_articles,
    list_career_paths,
    list_education_paths,
    list_profile_templates,
    regulation_by_topic,
    research_trends,
    resolve_profile,
    visual_generate_brief,
)
from security import v1_protected
from status import collect_status


def register_v1_routes(app) -> None:
    @app.get("/api/v1")
    def v1_gateway():
        return jsonify({
            "name": "Nursing Knowledge API",
            "version": "1.0.0",
            "docs": "/api/v1/status",
            "auth": "X-API-Key (optional in dev) + X-Nursing-Identity",
        })

    @app.get("/api/v1/status")
    def v1_status():
        return jsonify(collect_status())

    # --- Clinical ---
    @app.get("/api/v1/clinical/scales")
    @v1_protected
    def v1_clinical_scales(auth, identity):
        return jsonify(list_scales(category=request.args.get("category")))

    @app.get("/api/v1/clinical/scales/<scale_id>")
    @v1_protected
    def v1_clinical_scale(scale_id, auth, identity):
        result = get_scale(scale_id)
        return jsonify(result), (404 if not result.get("ok") else 200)

    @app.get("/api/v1/clinical/calculators")
    @v1_protected
    def v1_clinical_calculators(auth, identity):
        return jsonify(list_calculators())

    @app.get("/api/v1/clinical/calculators/<calc_id>")
    @v1_protected
    def v1_clinical_calculator(calc_id, auth, identity):
        result = get_calculator(calc_id)
        return jsonify(result), (404 if not result.get("ok") else 200)

    @app.get("/api/v1/clinical/protocols")
    @v1_protected
    def v1_clinical_protocols(auth, identity):
        return jsonify(list_protocols())

    @app.get("/api/v1/clinical/glossary")
    @v1_protected
    def v1_clinical_glossary(auth, identity):
        return jsonify(glossary())

    # --- Calculator ---
    @app.post("/api/v1/calculator/drip-rate")
    @v1_protected
    def v1_calc_drip(auth, identity):
        body = request.get_json(silent=True) or {}
        result = calc_drip_rate(
            volume=float(body.get("volume", 0)),
            time=float(body.get("time", 0)),
            factor=float(body.get("factor", 20)),
            time_unit=body.get("time_unit", "hours"),
        )
        return jsonify(result), (400 if not result.get("ok") else 200)

    @app.post("/api/v1/calculator/bmi")
    @v1_protected
    def v1_calc_bmi(auth, identity):
        body = request.get_json(silent=True) or {}
        result = run_calculator("bmi", body)
        return jsonify(result), (400 if not result.get("ok") else 200)

    @app.post("/api/v1/calculator/<calc_id>")
    @v1_protected
    def v1_calc_generic(calc_id, auth, identity):
        body = request.get_json(silent=True) or {}
        result = run_calculator(calc_id, body)
        return jsonify(result), (400 if not result.get("ok") else 200)

    # --- Content ---
    @app.get("/api/v1/content/articles")
    @v1_protected
    def v1_content_articles(auth, identity):
        return jsonify(list_articles(tool_code=request.args.get("tool_code"), limit=int(request.args.get("limit", 20))))

    @app.get("/api/v1/content/articles/<article_id>")
    @v1_protected
    def v1_content_article(article_id, auth, identity):
        result = get_article(article_id)
        return jsonify(result), (404 if not result.get("ok") else 200)

    # --- Identity ---
    @app.get("/api/v1/identity/profiles")
    @v1_protected
    def v1_identity_profiles(auth, identity):
        return jsonify(list_profile_templates())

    @app.get("/api/v1/identity/profile")
    @v1_protected
    def v1_identity_profile_get(auth, identity):
        return jsonify(resolve_profile(identity))

    @app.post("/api/v1/identity/profile")
    @v1_protected
    def v1_identity_profile_post(auth, identity):
        body = request.get_json(silent=True) or {}
        merged = {**identity, **body}
        return jsonify(resolve_profile(merged))

    # --- Visual ---
    @app.post("/api/v1/visual/generate")
    @v1_protected
    def v1_visual_generate(auth, identity):
        body = request.get_json(silent=True) or {}
        return jsonify(visual_generate_brief(
            country=body.get("country", identity.get("country", "BR")),
            persona=body.get("persona", identity.get("role", "student")),
            topic=body.get("topic", ""),
            style=body.get("style", "clinical"),
        ))

    # --- Education (Phase 2) ---
    @app.get("/api/v1/education/paths")
    @v1_protected
    def v1_education_paths(auth, identity):
        return jsonify(list_education_paths())

    @app.get("/api/v1/education/path/<slug>")
    @v1_protected
    def v1_education_path(slug, auth, identity):
        result = get_education_path(slug)
        return jsonify(result), (404 if not result.get("ok") else 200)

    # --- Regulation (Phase 2) ---
    @app.get("/api/v1/regulation/country/<country>/topic/<topic>")
    @v1_protected
    def v1_regulation_topic(country, topic, auth, identity):
        return jsonify(regulation_by_topic(country, topic))

    # --- Career (Phase 2) ---
    @app.get("/api/v1/career/paths")
    @v1_protected
    def v1_career_paths(auth, identity):
        return jsonify(list_career_paths())

    @app.get("/api/v1/career/path/<slug>")
    @v1_protected
    def v1_career_path(slug, auth, identity):
        result = get_career_path(slug)
        return jsonify(result), (404 if not result.get("ok") else 200)

    @app.get("/api/v1/career/certifications")
    @v1_protected
    def v1_career_certs(auth, identity):
        from paths import load_dataset
        certs = load_dataset("datasets/master-data/professional-intelligence/certifications_registry.json")
        return jsonify({"ok": True, "certifications": certs.get("certifications", [])})

    # --- Jobs (Phase 3) ---
    @app.post("/api/v1/jobs/match")
    @v1_protected
    def v1_jobs_match(auth, identity):
        body = request.get_json(silent=True) or {}
        profile = body.get("profile", "ICU nurse")
        country = body.get("country", identity.get("country", "Brazil"))
        return jsonify(job_match(profile, country, identity))

    # --- Research (Phase 3) ---
    @app.get("/api/v1/research/trends")
    @v1_protected
    def v1_research_trends(auth, identity):
        return jsonify(research_trends())

    # --- Agent (Phase 3) ---
    @app.post("/api/v1/agent/<agent_id>")
    @v1_protected
    def v1_agent(agent_id, auth, identity):
        body = request.get_json(silent=True) or {}
        body.setdefault("identity", identity)
        result = agent_run(agent_id, body)
        return jsonify(result), (404 if not result.get("ok") else 200)
