"""Exam prep plan generator — 30/60/90 day plans."""
from __future__ import annotations

from paths import exam_prep_templates, public_exams, tool_professional_context


def build_exam_plan(
    goal: str,
    *,
    days: int = 30,
    country: str = "BR",
    position: str | None = None,
) -> dict:
    templates = exam_prep_templates()
    plans = templates.get("plans", {})

    if days <= 30:
        plan_key = "30_days"
    elif days <= 60:
        plan_key = "60_days"
    else:
        plan_key = "90_days"

    plan_template = plans.get(plan_key, plans["30_days"])
    exams = public_exams().get("exams", [])
    matched_exams = [
        e for e in exams
        if (not position or position.lower() in e.get("position", "").lower())
        or goal.lower() in e.get("position", "").lower()
    ]

    subjects = templates.get("default_subjects_br", [])
    if matched_exams:
        for e in matched_exams:
            subjects = list(dict.fromkeys(subjects + e.get("subjects", [])))

    linked_tools = []
    for e in matched_exams:
        linked_tools.extend(e.get("linked_tools", []))
    linked_tools = list(dict.fromkeys(linked_tools))

    tool_topics = []
    ctx = tool_professional_context().get("tools", {})
    for tc in linked_tools:
        t = ctx.get(tc, {})
        tool_topics.append({"tool_code": tc, "name": t.get("display_name"), "exam_topics": t.get("exam_topics", [])})

    return {
        "ok": True,
        "agent": "Career & Exam Prep Agent",
        "goal": goal,
        "country": country,
        "position": position,
        "duration_days": days,
        "plan_key": plan_key,
        "plan_label": plan_template.get("label"),
        "schedule": plan_template.get("weeks") or plan_template.get("phases", []),
        "subjects": subjects,
        "matched_exams": matched_exams,
        "linked_tools": tool_topics,
        "next_steps": [
            "Revisar legislação COFEN + Lei 7.498/1986",
            "Praticar cálculos e escalas vinculadas ao edital",
            "Simulados cronometrados na última fase",
        ],
    }
