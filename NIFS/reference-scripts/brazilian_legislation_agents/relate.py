"""Etapa relate — vínculos ferramenta ↔ legislação."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from config import PROVISIONS, TOOL_LINKS


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path) -> dict:
    if not path.is_file():
        return {"records": []}
    return json.loads(path.read_text(encoding="utf-8"))


def relate_tool_to_provision(
    *,
    tool_code: str,
    tool_route: str,
    provision_entity_code: str,
    link_type: str = "legal_basis",
    summary_pt: str = "",
) -> dict:
    seq = len(_load(TOOL_LINKS).get("records", [])) + 1
    concept = tool_code.replace("TOOL.", "").replace(".", "_")
    return {
        "entity_code": f"TLK.{concept}.{seq:03d}",
        "concept_code": f"{concept}_LINK",
        "parent_entity_code": provision_entity_code,
        "parent_entity_type": "LegalProvision",
        "tool_code": tool_code,
        "tool_route": tool_route,
        "link_type": link_type,
        "summary_pt": summary_pt or f"Vínculo {tool_code} → {provision_entity_code}",
        "created_at": _now(),
        "content_source": "BRAZILIAN_LEGISLATION_AGENT",
    }


def auto_relate_notif_comp() -> list[dict]:
    """Garante links TOOL.NOTIF_COMP → dispositivos vigilância."""
    prov_doc = _load(PROVISIONS)
    links = []
    targets = [
        r for r in prov_doc.get("records", [])
        if r.get("domain_code") == "LEX_DOM.BR.VIGILANCE"
        or "NC" in r.get("concept_code", "")
        or r.get("parent_entity_code") == "LEG.BR.MS.PC4.2017"
    ]
    for t in targets[:3]:
        links.append(relate_tool_to_provision(
            tool_code="TOOL.NOTIF_COMP",
            tool_route="/compulsory-notifications",
            provision_entity_code=t["entity_code"],
            link_type="legal_basis",
            summary_pt=f"Notificação compulsória — base {t.get('article_label', t['entity_code'])}",
        ))
    return links


def run_relate() -> dict:
    new_links = auto_relate_notif_comp()
    existing = {r["entity_code"] for r in _load(TOOL_LINKS).get("records", [])}
    to_add = [l for l in new_links if l["entity_code"] not in existing]
    return {"generated_at": _now(), "new_links": to_add, "count": len(to_add)}
