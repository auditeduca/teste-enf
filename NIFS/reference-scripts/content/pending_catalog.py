"""Gera fila de conteúdos pendentes a partir da proposta master-data + gaps editoriais."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROPOSAL = ROOT / "datasets" / "metadata" / "master_code_sequence_proposal.json"
OUT = ROOT / "datasets" / "master-data" / "content-pending" / "pending_items.json"

# Escalas piloto para MMP/PKT/SIM derivados (prioridade clínica)
PILOT_SCL = [
    "APGAR", "BRADEN", "GLASGOW", "MORSE", "NEWS2", "RASS", "CAM-ICU",
    "MEWS", "SOFA", "QSOFA",
]

FAQ_PAGES = [
    {"page_code": "PAGE.FAQ", "title_pt": "FAQ institucional", "canonical_url": "/faq/"},
    {"page_code": "PAGE.APGAR", "title_pt": "FAQ Apgar", "canonical_url": "/ferramentas/apgar/"},
    {"page_code": "PAGE.BRADEN", "title_pt": "FAQ Braden", "canonical_url": "/ferramentas/braden/"},
    {"page_code": "PAGE.FLASHCARDS", "title_pt": "FAQ Flashcards", "canonical_url": "/flashcards/"},
    {"page_code": "PAGE.SIMULADOS", "title_pt": "FAQ Simulados", "canonical_url": "/simulados/"},
    {"page_code": "PAGE.PROTOCOLOS", "title_pt": "FAQ Protocolos", "canonical_url": "/protocolos/"},
    {"page_code": "PAGE.MAPAS", "title_pt": "FAQ Mapas mentais", "canonical_url": "/mapas-mentais/"},
    {"page_code": "PAGE.BIBLIOTECA", "title_pt": "FAQ Biblioteca", "canonical_url": "/biblioteca/"},
    {"page_code": "PAGE.GUIAS", "title_pt": "FAQ Guias de bolso", "canonical_url": "/guias/"},
    {"page_code": "PAGE.HOME", "title_pt": "FAQ Home", "canonical_url": "/"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _entity_code(concept: str, artifact: str, seq: int = 1) -> str:
    return f"{concept}_{artifact}_{seq:03d}"


def _pending_id(entity_code: str) -> str:
    return f"PEND.{entity_code}"


def _item(
    *,
    artifact_type: str,
    entity_code: str,
    concept_code: str,
    title_pt: str,
    canonical_url: str | None = None,
    parent_entity_code: str | None = None,
    target_dataset: str,
    status: str = "pending",
    completion_pct: int = 0,
    blocker: str | None = None,
) -> dict:
    return {
        "pending_id": _pending_id(entity_code),
        "artifact_type": artifact_type,
        "entity_code": entity_code,
        "concept_code": concept_code,
        "parent_entity_code": parent_entity_code,
        "title_pt": title_pt,
        "canonical_url": canonical_url,
        "target_dataset": target_dataset,
        "status": status,
        "completion_pct": completion_pct,
        "lifecycle": "draft",
        "agent_pipeline": ["search", "generate", "review", "validate"],
        "blocker": blocker,
    }


def _artifacts_from_proposal(proposal: dict, artifact_type: str) -> list[dict]:
    out: list[dict] = []
    for concept in proposal.get("concepts", []):
        for art in concept.get("artifacts", []):
            if art.get("artifact_type") != artifact_type:
                continue
            out.append(
                {
                    "concept_code": concept["concept_code"],
                    "entity_code": art["entity_code"],
                    "name": art.get("name") or concept["concept_code"],
                    "canonical_url": art.get("canonical_url") or concept.get("canonical_url"),
                    "parent": f"{concept['concept_code']}_SCL_001"
                    if artifact_type in ("FLA", "MMP", "PKT")
                    else None,
                }
            )
    return out


def build_pending_queue() -> dict:
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    items: list[dict] = []

    targets = {
        "FLA": "datasets/education/flashcards.json",
        "PRT": "datasets/clinical/clinical_tools_catalog.json",
        "SIM": "datasets/education/simulated_exams.json",
        "MMP": "datasets/content/editorial/mindmaps.json",
        "PKT": "datasets/content/editorial/pocket_guides.json",
        "FAQ": "datasets/content/editorial/template_pages.json",
    }

    for art in _artifacts_from_proposal(proposal, "FLA"):
        items.append(
            _item(
                artifact_type="FLA",
                entity_code=art["entity_code"],
                concept_code=art["concept_code"],
                title_pt=f"Flashcards {art['name']}",
                canonical_url=art["canonical_url"],
                parent_entity_code=art["parent"],
                target_dataset=targets["FLA"],
                blocker="Deck sem validação master-data",
            )
        )

    for art in _artifacts_from_proposal(proposal, "PRT"):
        items.append(
            _item(
                artifact_type="PRT",
                entity_code=art["entity_code"],
                concept_code=art["concept_code"],
                title_pt=f"Protocolo {art['name']}",
                canonical_url=art["canonical_url"],
                target_dataset=targets["PRT"],
                blocker="Evidência Grau A pendente",
            )
        )

    for concept in PILOT_SCL:
        ec = _entity_code(concept, "SIM")
        items.append(
            _item(
                artifact_type="SIM",
                entity_code=ec,
                concept_code=concept,
                title_pt=f"Simulado {concept}",
                parent_entity_code=_entity_code(concept, "SCL"),
                target_dataset=targets["SIM"],
                blocker="Simulado sem entity_code NKOS",
            )
        )

    for concept in PILOT_SCL:
        ec = _entity_code(concept, "MMP")
        items.append(
            _item(
                artifact_type="MMP",
                entity_code=ec,
                concept_code=concept,
                title_pt=f"Mapa mental {concept}",
                parent_entity_code=_entity_code(concept, "SCL"),
                target_dataset=targets["MMP"],
                blocker="Dataset mindmaps.json ausente",
            )
        )

    for concept in PILOT_SCL:
        ec = _entity_code(concept, "PKT")
        items.append(
            _item(
                artifact_type="PKT",
                entity_code=ec,
                concept_code=concept,
                title_pt=f"Guia de bolso {concept}",
                parent_entity_code=_entity_code(concept, "SCL"),
                target_dataset=targets["PKT"],
                blocker="Dataset pocket_guides.json ausente",
            )
        )

    for page in FAQ_PAGES:
        page_key = page["page_code"].replace("PAGE.", "")
        ec = f"{page_key}_FAQ_001"
        items.append(
            _item(
                artifact_type="FAQ",
                entity_code=ec,
                concept_code=page_key,
                title_pt=page["title_pt"],
                canonical_url=page["canonical_url"],
                target_dataset=targets["FAQ"],
                blocker="FAQ sem entity_code",
            )
        )

    by_type: dict[str, int] = {}
    for it in items:
        by_type[it["artifact_type"]] = by_type.get(it["artifact_type"], 0) + 1

    return {
        "schema_version": "2026.2.3-content-pending",
        "generated_at": _now(),
        "generated_by": "scripts/content/pending_catalog.py",
        "status": "PENDING_REVIEW",
        "total": len(items),
        "counts_by_type": by_type,
        "items": items,
    }


def main() -> None:
    doc = build_pending_queue()
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} — {doc['total']} items")
    for k, v in sorted(doc["counts_by_type"].items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
