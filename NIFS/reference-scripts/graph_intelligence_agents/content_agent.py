"""Clinical decision content agent — Claude for dense enrichment."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from graph_snapshot import build_tool_subgraph, relations_by_tool
from paths import LOGS, clinical_tools, prompt_template


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _deterministic_content(entity_code: str, subgraph: dict) -> dict:
    tool = subgraph.get("tool") or {}
    name = tool.get("name_pt") or tool.get("title_pt") or entity_code
    rel_count = subgraph.get("relations_count", 0)
    return {
        "mode": "deterministic",
        "entity_code": entity_code,
        "title_pt": f"Decisão clínica: {name}",
        "summary_pt": (
            f"Ferramenta {name} com {rel_count} relações no grafo. "
            "Conteúdo denso requer ANTHROPIC_API_KEY para geração via Claude."
        ),
        "decision_path": [
            {"step": 1, "observation": "Coletar dados clínicos", "interpretation": "Contextualizar escore/cálculo", "decision": "Interpretar resultado", "intervention_hint": "Documentar e comunicar equipe"},
        ],
        "linked_tools": [],
        "proposed_relations": [],
        "disclaimer": "Não substitui julgamento clínico.",
        "generated_at": _now(),
    }


def generate_clinical_content(
    entity_code: str,
    *,
    entity_type: str = "ClinicalTool",
    country: str = "BR",
    persona: str = "profissional",
    use_llm: bool = True,
    payload: dict | None = None,
) -> dict:
    """Gera conteúdo denso sobre decisão clínica para entidade do grafo."""
    payload = payload or {}
    subgraph = build_tool_subgraph(entity_code)
    if not subgraph.get("tool") and entity_type == "ClinicalTool":
        tool = next((t for t in clinical_tools() if t.get("tool_code") == entity_code), None)
        if not tool:
            return {"ok": False, "error": "entity_not_found", "entity_code": entity_code}

    if not use_llm:
        return {"ok": True, **_deterministic_content(entity_code, subgraph)}

    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from llm_router import llm_enabled, route_chat_json

    if not llm_enabled(payload):
        content = _deterministic_content(entity_code, subgraph)
        content["llm_skipped"] = True
        return {"ok": True, **content}

    graph_ctx = {
        "subgraph": subgraph,
        "relations": relations_by_tool(entity_code)[:30],
    }
    tools_summary = [
        {"tool_code": t.get("tool_code"), "name_pt": t.get("name_pt"), "tool_type": t.get("tool_type")}
        for t in clinical_tools()[:40]
    ]

    tpl = prompt_template("CLINICAL_DECISION_CONTENT")
    system = tpl.format(
        entity_code=entity_code,
        entity_type=entity_type,
        graph_context_json=json.dumps(graph_ctx, ensure_ascii=False)[:80000],
        country=country,
        persona=persona,
    )

    messages = [
        {"role": "user", "content": system},
    ]

    try:
        result = route_chat_json(
            messages,
            task="clinical_decision_content",
            provider="claude",
            payload=payload,
            temperature=0.25,
            max_tokens=8192,
        )
        parsed = result.get("parsed") or {}
        out = {
            "ok": True,
            "mode": "llm",
            "provider": result.get("provider"),
            "model": result.get("model"),
            "entity_code": entity_code,
            **parsed,
            "generated_at": _now(),
        }
        _append_proposal(out)
        return out
    except Exception as exc:
        content = _deterministic_content(entity_code, subgraph)
        content["llm_error"] = str(exc)[:500]
        return {"ok": True, **content}


def generate_cross_tool_intelligence(
    tool_code: str,
    *,
    payload: dict | None = None,
) -> dict:
    """Inteligência cruzada entre ferramentas — Claude."""
    payload = payload or {}
    subgraph = build_tool_subgraph(tool_code)
    relations = relations_by_tool(tool_code)
    tools_summary = [
        {"tool_code": t.get("tool_code"), "name_pt": t.get("name_pt"), "tool_type": t.get("tool_type")}
        for t in clinical_tools()[:60]
    ]

    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from llm_router import llm_enabled, route_chat_json

    if not llm_enabled(payload):
        return {
            "ok": True,
            "mode": "deterministic",
            "tool_code": tool_code,
            "feeds_into": [],
            "global_risk_chain": [],
            "memory_hooks": [],
            "note": "Configure ANTHROPIC_API_KEY for cross-tool analysis",
        }

    tpl = prompt_template("CROSS_TOOL_INTELLIGENCE")
    prompt = tpl.format(
        tool_code=tool_code,
        relations_json=json.dumps(relations[:40], ensure_ascii=False),
        tools_summary_json=json.dumps(tools_summary, ensure_ascii=False),
    )

    try:
        result = route_chat_json(
            [{"role": "user", "content": prompt}],
            task="reasoning_chain",
            provider="claude",
            payload=payload,
            max_tokens=6144,
        )
        parsed = result.get("parsed") or {}
        return {"ok": True, "mode": "llm", "tool_code": tool_code, **parsed}
    except Exception as exc:
        return {"ok": False, "tool_code": tool_code, "error": str(exc)[:500]}


def _append_proposal(doc: dict) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    path = LOGS / "content_proposals.jsonl"
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False) + "\n")
