"""Lei 9.610/98 rights binding for CKO works. Not a copyright PASS for third-party scales."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT, TOOLS_DIR
from .vault import first_copy

PILOT_ORIGINAL = ("gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico")
PILOT_HOLD = ("dimensionamento",)
THIRD_PARTY = ("braden", "norton", "glasgow")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def bind_rights(*, law_text: str | None = None, law_sha256: str | None = None) -> dict:
    law_copy = first_copy("SRC-LEI-9610-1998")
    instrument = {
        "business_key": "INS-LEI-9610-1998",
        "uuid": None,
        "name": "Lei n. 9.610, de 19 de fevereiro de 1998",
        "short_name": "Lei de Direitos Autorais",
        "jurisdiction": "JUR-BR",
        "authority_class": "AUTH-OFFICIAL-BR",
        "issuer": "Presidência da República / Planalto",
        "source_url": "https://www.planalto.gov.br/ccivil_03/leis/l9610.htm",
        "kind": "PUBLIC_LAW",
        "mask_id": "MASK-LAW-BR",
        "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
        "protects": "obras literárias, artísticas e científicas originais, inclusive texto e software quando original",
        "does_not": [
            "não transfere automaticamente ao CKO direitos sobre escalas de terceiros (Braden, Norton, Glasgow)",
            "não autoriza copiar cláusula de norma técnica licenciada",
            "não equivale a registro em órgão de direitos autorais nem a ASSURED",
        ],
        "related_instrument": {
            "business_key": "INS-LEI-9609-1998",
            "name": "Lei n. 9.609, de 19 de fevereiro de 1998 (programa de computador)",
            "status": "REGISTERED",
            "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
        },
        "vault_sha256": (law_copy or {}).get("first_sha256") or law_sha256,
        "inbox_present": bool(law_copy) or bool(law_text),
        "status": "DOCUMENTADO" if (law_copy or law_text or law_sha256) else "EVIDENCE_PENDING",
        "epistemic_status": "SOURCE_DERIVED" if (law_copy or law_text) else "PROPOSED",
        "implemented": False,
        "assured": False,
        "note": "Lei pública registrada como instrumento. Texto integral, se vaulted, permanece cópia inalterada; não vira regra de produto.",
    }
    works = []
    for slug in PILOT_ORIGINAL:
        path = TOOLS_DIR / f"{slug}.json"
        works.append({
            "business_key": f"WORK-{slug.upper()}",
            "slug": slug,
            "work_class": "ORIGINAL_CKO_CANDIDATE",
            "kind": "calculator_or_educational_object",
            "instrument_ref": "INS-LEI-9610-1998",
            "mask_id": "MASK-TOOL-WORK",
            "in_data_tools": path.exists(),
            "rights_status": "DOCUMENTADO",
            "assured": False,
            "cko_copyright_claim": "CANDIDATE_ORIGINAL — não ASSURED",
            "uuid": None,
        })
    for slug in PILOT_HOLD:
        path = TOOLS_DIR / f"{slug}.json"
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        works.append({
            "business_key": f"WORK-{slug.upper()}",
            "slug": slug,
            "work_class": "HOLD_OBJECT",
            "instrument_ref": "INS-LEI-9610-1998",
            "mask_id": "MASK-HOLD-WORK",
            "in_data_tools": path.exists(),
            "status": payload.get("status"),
            "has_formula": "calculator" in payload,
            "rights_status": "HOLD",
            "assured": False,
            "uuid": None,
        })
    for slug in THIRD_PARTY:
        works.append({
            "business_key": f"WORK-{slug.upper()}",
            "slug": slug,
            "work_class": "THIRD_PARTY_SCALE",
            "instrument_ref": "INS-LEI-9610-1998",
            "mask_id": "MASK-SCALE-THIRD-PARTY",
            "in_data_tools": (TOOLS_DIR / f"{slug}.json").exists(),
            "quarantined": True,
            "rights_status": "HOLD",
            "cko_copyright_claim": "FORBIDDEN",
            "assured": False,
            "note": "Lei 9.610 protege o autor original da escala, não autoriza o CKO a reivindicar a obra.",
            "uuid": None,
        })

    work_registry = {
        "business_key": "MD-WORK-REG-001",
        "uuid": None,
        "status": "REGISTERED",
        "maturity": "M1_SCHEMA_DEFINED",
        "population": len(works),
        "works": works,
        "bound_at": _now(),
        "rule": "Uma obra → uma identidade. Extração HTML não cria direito. SEM EVIDÊNCIA de titularidade → não ASSURED.",
    }
    rights_profile = {
        "business_key": "REG-RIGHTS-001",
        "uuid": None,
        "status": "HOLD",
        "instrument_ref": "INS-LEI-9610-1998",
        "mask_id": "MASK-LAW-BR",
        "gate": "HOLD",
        "publication_requires": ["work_class bound", "third-party scales not claimed", "vault first copy of instrument"],
        "note": "Direito autoral documentado ≠ implementação de licença de escala ≠ PASS de publicação.",
        "bound_works": [item["business_key"] for item in works],
    }
    instruments = {
        "business_key": "REG-INSTRUMENT-001",
        "uuid": None,
        "status": "REGISTERED",
        "population": 2,
        "instruments": [instrument, instrument["related_instrument"]],
    }
    _dump(ROOT / "cko_reg" / "instrument_registry.json", instruments)
    _dump(ROOT / "cko_md" / "work_registry.json", work_registry)
    _dump(ROOT / "cko_reg" / "rights_profile.json", rights_profile)
    return {
        "agent_id": "AG-RIGHTS-BIND",
        "class": "REGULATORY",
        "role": "CHECKER",
        "status": instrument["status"],
        "instrument": instrument["business_key"],
        "works": work_registry["population"],
        "third_party_claimed": False,
        "assured": False,
        "llm_used": False,
        "promotes_to_md": False,
    }
