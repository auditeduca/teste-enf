"""Master-data → regulatory-norm → evidence → frontend chain.

Classified counts (md_fields=2496, normative_bindings=10913) stay classified.
This module materializes the chain as graph edges, one known-universe object,
and HTML data-* stamps. It does not explode coverage to one receipt per field.
"""
from __future__ import annotations

import re
from pathlib import Path

CHAIN_ID = "CKO-MD-TO-FRONTEND-1.0.0"
CHAIN_FLOW = [
    "MD",
    "REG",
    "Schema",
    "Engine",
    "Validator",
    "Renderer",
    "Runtime",
    "Frontend",
]
CHAIN_NODE_IDS = [
    "CHAIN-MD",
    "CHAIN-REG",
    "CHAIN-SCHEMA",
    "CHAIN-ENGINE",
    "CHAIN-VALIDATOR",
    "CHAIN-RENDERER",
    "CHAIN-RUNTIME",
    "CHAIN-FRONTEND",
]
HTML_ATTRS = {
    "data-cko-md": "CKO-MD",
    "data-cko-reg": "CKO-REG",
    "data-cko-norm": "NIFS-900-03",
    "data-cko-evidence": "HOLD",
    "data-cko-chain": "MD / REG / Schema / Engine / Validator / Renderer / Runtime / Frontend",
}
HTML_ATTR_SNIPPET = " ".join(f'{k}="{v}"' for k, v in HTML_ATTRS.items())

MD_NORM_CHAIN = {
    "id": CHAIN_ID,
    "kind": "md-norm-evidence-chain",
    "root": "policy-as-code",
    "flow": CHAIN_FLOW,
    "master_data": {
        "layer": "CKO-MD",
        "artifact": "ART-CKO-MASTER-DATA-FINAL-CONTROLLED",
        "version": "OV-CKO-MASTER-DATA-FINAL-CONTROLLED-1.0.0",
        "freeze": "FROZEN",
        "fields_classified": 2496,
    },
    "regulatory": {
        "layer": "CKO-REG",
        "artifact": "ART-CKO-REGULATORY-FINAL-CONTROLLED",
        "version": "OV-CKO-REGULATORY-FINAL-CONTROLLED-1.0.0",
        "freeze": "FROZEN",
        "bindings_classified": 10913,
        "nifs": ["NIFS-900-03", "NIFS-600-15"],
    },
    "schema": "data/schemas/tool.schema.json",
    "engine": "js/calc-engine.js",
    "renderer": "scripts/generate_tool_page.py",
    "no_fact_without_evidence": True,
    "discovery_is_not_evidence": True,
    "pending_is_not_ack": True,
    "operational": "NOT_ASSERTED",
    "release": "HOLD / NOT_RELEASED",
    "materialized_field_bindings": False,
}


def _html_open_tag_span(text: str) -> tuple[int, int] | None:
    match = re.search(r"<html\b", text, flags=re.I)
    if not match:
        return None
    quote = None
    for index in range(match.end(), len(text)):
        char = text[index]
        if quote:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
            continue
        if char == ">":
            return match.start(), index + 1
    return None


def stamp_html_text(text: str) -> str:
    span = _html_open_tag_span(text)
    if not span:
        return text
    start, end = span
    tag = text[start:end]
    for key, value in HTML_ATTRS.items():
        if re.search(rf"\b{re.escape(key)}\s*=", tag, flags=re.I):
            tag = re.sub(rf'\b{re.escape(key)}\s*=\s*"[^"]*"', f'{key}="{value}"', tag, flags=re.I)
        else:
            tag = tag[:-1].rstrip() + f' {key}="{value}">'
    return text[:start] + tag + text[end:]


def stamp_html_file(path: Path) -> bool:
    if not path.is_file():
        return False
    original = path.read_text(encoding="utf-8")
    stamped = stamp_html_text(original)
    if stamped == original:
        return False
    if original and len(stamped) < max(256, int(len(original) * 0.9)):
        raise SystemExit(f"refusing HTML stamp that would shrink {path}: {len(original)} -> {len(stamped)}")
    path.write_text(stamped, encoding="utf-8")
    return True


def bind_md_norm_evidence(nodes: list, edges: list) -> None:
    """Attach MD→REG→evidence to every runtime object. Nodes for CKO-MD/REG must exist."""
    existing = {n["id"] for n in nodes}
    for nid, step, name in zip(CHAIN_NODE_IDS, range(1, 9), CHAIN_FLOW):
        if nid not in existing:
            nodes.append(
                {
                    "id": nid,
                    "type": "NormativeChainStep",
                    "step": step,
                    "name": name,
                    "no_fact_without_evidence": True,
                    "release": "HOLD / NOT_RELEASED",
                }
            )
            existing.add(nid)
        if step > 1:
            prev = CHAIN_NODE_IDS[step - 2]
            edges.append([prev, nid, "nextStep"])
    chain_edges = [
        ["LAYER-CKO-MD", "CHAIN-MD", "instanceOf"],
        ["LAYER-CKO-REG", "CHAIN-REG", "instanceOf"],
        ["LAYER-CKO-REG", "LAYER-CKO-MD", "derivedFrom"],
        ["SCHEMA-TOOL", "CHAIN-SCHEMA", "instanceOf"],
        ["SCHEMA-TOOL", "LAYER-CKO-MD", "derivedFrom"],
        ["SCHEMA-TOOL", "LAYER-CKO-REG", "boundToNorm"],
        ["LAYER-LYR-RND-001", "CHAIN-RENDERER", "instanceOf"],
        ["LAYER-LYR-RUN-001", "CHAIN-RUNTIME", "instanceOf"],
        ["LAYER-LYR-CLIN-RULE-001", "CHAIN-VALIDATOR", "instanceOf"],
        ["LAYER-LYR-CLIN-CALC-001", "CHAIN-ENGINE", "instanceOf"],
    ]
    edges.extend(chain_edges)
    governed_types = {"ToolRuntime", "LibraryRuntime", "InstitutionalPage", "LayerRuntime"}
    snapshot = [n for n in nodes if n.get("type") in governed_types]
    for node in snapshot:
        nid = node["id"]
        node["master_data"] = "CKO-MD"
        node["regulatory"] = "CKO-REG"
        node["norm"] = "NIFS-900-03"
        node["no_fact_without_evidence"] = True
        if nid != "LAYER-CKO-MD":
            edges.append([nid, "LAYER-CKO-MD", "derivedFrom"])
        if nid != "LAYER-CKO-REG":
            edges.append([nid, "LAYER-CKO-REG", "boundToNorm"])
        if node.get("type") == "InstitutionalPage":
            edges.append([nid, "CHAIN-FRONTEND", "instanceOf"])
        evd_id = f"EVD-{nid}"
        if evd_id not in existing:
            nodes.append(
                {
                    "id": evd_id,
                    "type": "EvidenceReceipt",
                    "of": nid,
                    "kind": "runtime",
                    "status": "HOLD",
                    "no_fact_without_evidence": True,
                    "discovery_is_not_evidence": True,
                    "pending_is_not_ack": True,
                    "operational": "NOT_ASSERTED",
                }
            )
            existing.add(evd_id)
        edges.append([nid, evd_id, "hasEvidence"])
    for extra_id in ("SCHEMA-TOOL", "GRAPH-KG"):
        evd_id = f"EVD-{extra_id}"
        if extra_id in existing and evd_id not in existing:
            nodes.append(
                {
                    "id": evd_id,
                    "type": "EvidenceReceipt",
                    "of": extra_id,
                    "kind": "schema" if extra_id == "SCHEMA-TOOL" else "graph",
                    "status": "HOLD",
                    "no_fact_without_evidence": True,
                    "discovery_is_not_evidence": True,
                    "pending_is_not_ack": True,
                    "operational": "NOT_ASSERTED",
                }
            )
            existing.add(evd_id)
            edges.append([extra_id, evd_id, "hasEvidence"])
