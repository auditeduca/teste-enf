"""Studio workflow — graph → template → generate → evaluate → review."""
from __future__ import annotations

from uuid import uuid4

from graph_context import resolve_graph_context
from social_generator import generate_social_svg
from studio_agents import create_template, edit_template, evaluate_publication, review_image


def run_studio_pipeline(
    *,
    tool_code: str | None = None,
    topic: str | None = None,
    entity_code: str | None = None,
    format_id: str = "instagram_post",
    persona: str = "profissional",
    country: str = "BR",
    template_id: str | None = None,
    edits: dict | None = None,
    persist: bool = True,
) -> dict:
    run_id = f"STUDIO.{uuid4().hex[:10].upper()}"
    graph_ctx = resolve_graph_context(
        entity_code=entity_code, tool_code=tool_code, topic=topic, country=country, persona=persona,
    )

    steps = []

    # 1 Graph context
    steps.append({"step": "graph_context", "status": "completed", "relations": graph_ctx["graph"]["relations_count"]})

    # 2 Template creator or editor
    if template_id:
        tpl_result = edit_template(template_id, edits or {}, persona=persona, country=country)
        spec = tpl_result.get("updated_template", {})
    else:
        tpl_result = create_template(graph_ctx=graph_ctx, format_id=format_id, topic=topic)
        spec = tpl_result.get("template_spec", {})
    steps.append({"step": "template", "agent": tpl_result.get("agent_id"), "status": tpl_result.get("status"), "result": tpl_result})

    content = spec.get("content") or spec
    headline = content.get("headline") or graph_ctx.get("tool", {}).get("name") or topic or "NKOS"
    subheadline = content.get("subheadline") or spec.get("subheadline", "")
    cta = content.get("cta") or spec.get("cta") or "Saiba mais"

    # 3 Generate image
    gen = generate_social_svg(
        headline=headline,
        subheadline=subheadline,
        format_id=format_id,
        cta=cta,
        persona=persona,
        country=country,
        badges=["🩺 Clínico", "📚 Evidências", f"🌎 {country}"],
    )
    steps.append({"step": "social_generate", "status": "completed", "result": gen})

    # 4 Evaluate publication
    eval_result = evaluate_publication(template_spec=spec, persona=persona, country=country, format_id=format_id)
    steps.append({"step": "publication_evaluator", "status": "completed", "result": eval_result})

    # 5 Review image
    review_result = review_image(evaluation=eval_result, format_id=format_id)
    steps.append({"step": "image_reviewer", "status": "completed", "result": review_result})

    all_passed = eval_result.get("passed") and review_result.get("passed")

    return {
        "ok": all_passed,
        "run_id": run_id,
        "graph_context": graph_ctx,
        "steps": steps,
        "output": {
            "image": gen,
            "evaluation": eval_result.get("scores"),
            "review": review_result.get("scores"),
        },
        "passed": all_passed,
        "human_review_recommended": review_result.get("human_review_recommended", False),
    }
