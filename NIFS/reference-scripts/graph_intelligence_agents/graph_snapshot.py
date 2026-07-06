"""Build graph snapshots for validation — deterministic + LLM input."""
from __future__ import annotations

import json
from collections import Counter, defaultdict

from paths import (
    clinical_tools,
    decision_trees,
    entity_relations_path,
    knowledge_nodes,
    load_json,
    nnn_linkages,
    safety_rules,
)


def _load_relations(limit: int | None = None) -> list[dict]:
    doc = load_json(entity_relations_path())
    records = doc.get("records", [])
    if limit:
        return records[:limit]
    return records


def build_inventory_stats() -> dict:
    relations = _load_relations()
    tools = clinical_tools()
    nodes = knowledge_nodes()
    trees = decision_trees()
    rules = safety_rules()
    linkages = nnn_linkages()

    tool_codes = {t.get("tool_code") for t in tools if t.get("tool_code")}
    linked_tools: set[str] = set()
    relation_types = Counter()
    entity_types = Counter()

    for rel in relations:
        relation_types[rel.get("relation_type", "unknown")] += 1
        entity_types[rel.get("source_entity_type", "?")] += 1
        entity_types[rel.get("target_entity_type", "?")] += 1
        if rel.get("source_entity_type") == "ClinicalTool":
            linked_tools.add(rel.get("source_code", ""))
        if rel.get("target_entity_type") == "ClinicalTool":
            linked_tools.add(rel.get("target_code", ""))

    isolated_tools = sorted(tool_codes - linked_tools)
    node_sources = {n.get("source_code") for n in nodes if n.get("source_code")}

    return {
        "counts": {
            "relations": len(relations),
            "clinical_tools": len(tools),
            "knowledge_nodes": len(nodes),
            "decision_trees": len(trees),
            "safety_rules": len(rules),
            "nnn_linkages": len(linkages),
        },
        "relation_types": dict(relation_types.most_common(20)),
        "entity_types": dict(entity_types.most_common(20)),
        "tools_with_relations": len(linked_tools),
        "isolated_tools_count": len(isolated_tools),
        "isolated_tools_sample": isolated_tools[:30],
        "knowledge_nodes_without_relations_estimate": max(0, len(nodes) - len(node_sources & linked_tools)),
    }


def build_tool_subgraph(tool_code: str, *, relation_limit: int = 50) -> dict:
    relations = _load_relations()
    tool = next((t for t in clinical_tools() if t.get("tool_code") == tool_code), None)
    related = [
        r for r in relations
        if r.get("source_code") == tool_code or r.get("target_code") == tool_code
    ][:relation_limit]

    linked_trees = [
        t for t in decision_trees()
        if tool_code in (t.get("linked_tool_codes") or []) or tool_code.replace("TOOL.", "") in (t.get("tree_code") or "")
    ][:5]
    linked_rules = [r for r in safety_rules() if tool_code in (r.get("linked_tool_codes") or [])][:5]

    return {
        "tool_code": tool_code,
        "tool": tool,
        "relations": related,
        "relations_count": len(related),
        "decision_trees": linked_trees,
        "safety_rules": linked_rules,
    }


def build_validation_snapshot(
    *,
    tool_codes: list[str] | None = None,
    relations_sample: int = 200,
    include_stats: bool = True,
) -> dict:
    """Snapshot compacto para Claude validar critérios."""
    stats = build_inventory_stats() if include_stats else {}
    relations = _load_relations(limit=relations_sample)
    tools = clinical_tools()

    if tool_codes:
        tools = [t for t in tools if t.get("tool_code") in tool_codes]
        rel_set = set(tool_codes)
        relations = [
            r for r in _load_relations()
            if r.get("source_code") in rel_set or r.get("target_code") in rel_set
        ][:relations_sample]

    tools_summary = [
        {
            "tool_code": t.get("tool_code"),
            "name_pt": t.get("name_pt") or t.get("title_pt"),
            "tool_type": t.get("tool_type"),
            "category": t.get("category"),
            "taxonomy_code": t.get("taxonomy_code"),
        }
        for t in tools[:50]
    ]

    return {
        "stats": stats,
        "tools_sample": tools_summary,
        "relations_sample": relations,
        "nnn_linkages_count": stats.get("counts", {}).get("nnn_linkages", 0),
        "decision_trees_count": stats.get("counts", {}).get("decision_trees", 0),
    }


def detect_structural_issues(*, max_issues: int = 100) -> dict:
    relations = _load_relations()
    seen: set[str] = set()
    duplicates: list[str] = []
    invalid: list[dict] = []

    for rel in relations:
        key = f"{rel.get('source_code')}|{rel.get('target_code')}|{rel.get('relation_type')}"
        if key in seen:
            duplicates.append(rel.get("relation_code", key))
        seen.add(key)
        if not rel.get("source_code") or not rel.get("target_code"):
            invalid.append({"relation_code": rel.get("relation_code"), "issue": "missing_codes"})

    tool_codes = {t.get("tool_code") for t in clinical_tools()}
    orphan_tool_refs: list[str] = []
    for rel in relations:
        if rel.get("source_entity_type") == "ClinicalTool" and rel.get("source_code") not in tool_codes:
            orphan_tool_refs.append(rel.get("source_code"))
        if rel.get("target_entity_type") == "ClinicalTool" and rel.get("target_code") not in tool_codes:
            orphan_tool_refs.append(rel.get("target_code"))

    return {
        "duplicate_relations": duplicates[:max_issues],
        "invalid_relations": invalid[:max_issues],
        "orphan_tool_refs": sorted(set(orphan_tool_refs))[:max_issues],
        "total_relations": len(relations),
    }


def relations_by_tool(tool_code: str) -> list[dict]:
    return [
        r for r in _load_relations()
        if r.get("source_code") == tool_code or r.get("target_code") == tool_code
    ]
