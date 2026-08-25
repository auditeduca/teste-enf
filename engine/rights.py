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
    bind_nnn_opt_b()
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


# Codes taken from Drive *filenames* only (nanda-00046.json / nic-2312.json / noc-0401.json).
# Never copy definingCharacteristics, NIC activities, or NOC indicators.
NNN_DRIVE_CODES = (
    {
        "system": "NANDA",
        "code": "00046",
        "drive_filename": "nanda-00046.json",
        "cko_key": "CKO-NNN-DIAG-00046",
        "holder": "NANDA-I",
        "deep_link": "https://nanda.org/",
    },
    {
        "system": "NIC",
        "code": "2312",
        "drive_filename": "nic-2312.json",
        "cko_key": "CKO-NNN-INT-2312",
        "holder": "Elsevier",
        "deep_link": "https://www.elsevier.com/",
    },
    {
        "system": "NOC",
        "code": "0401",
        "drive_filename": "noc-0401.json",
        "cko_key": "CKO-NNN-OUT-0401",
        "holder": "Elsevier",
        "deep_link": "https://www.elsevier.com/",
    },
)
DISPLAY_LICENSE_UNAVAILABLE = "texto indisponível (licença)"


def bind_nnn_opt_b() -> dict:
    """Owner F12 = B. Identity catalog only. Zero licensed NANDA/NIC/NOC text."""
    identities = []
    for item in NNN_DRIVE_CODES:
        identities.append({
            "business_key": item["cko_key"],
            "uuid": None,
            "system": item["system"],
            "code": item["code"],
            "canonical_label": None,
            "display_label": DISPLAY_LICENSE_UNAVAILABLE,
            "drive_filename": item["drive_filename"],
            "drive_file_status": "QUARANTINE",
            "holder": item["holder"],
            "deep_link": item["deep_link"],
            "licensed_text": False,
            "in_data_tools": (TOOLS_DIR / item["drive_filename"]).exists(),
            "mapping": {"cid": None, "cipec": None, "note": "Arestas públicas HOLD até evidência HTTP."},
        })
    catalog = {
        "business_key": "MD-NNN-IDENTITY-001",
        "uuid": None,
        "status": "REGISTERED",
        "implemented": True,
        "publication": "HOLD",
        "assured": False,
        "owner_decision": "B",
        "chosen": ["OPT-B-IDENTIFIERS", "OPT-D-DEEPLINK"],
        "mode": "IDENTIFIERS_ONLY",
        "layer": "L120",
        "architecture_ref": "MD-NNN-RIGHTS-001",
        "owner_unblock": "UNBLOCK-NNN-LICENSE",
        "codes_source": "Drive filenames only. No JSON body copied.",
        "display_policy": DISPLAY_LICENSE_UNAVAILABLE,
        "do_not": [
            "Copiar nanda-00046.json / nic-2312.json / noc-0401.json para data/tools.",
            "Republicar definingCharacteristics, NIC activities ou NOC indicators.",
            "Inventar label canônico equivalente via LLM.",
        ],
        "identities": identities,
        "population": len(identities),
        "bound_at": _now(),
    }
    _dump(ROOT / "cko_md" / "nnn_identity_catalog.json", catalog)

    arch_path = ROOT / "cko_md" / "nnn_rights_architecture.json"
    architecture = {}
    if arch_path.exists():
        architecture = json.loads(arch_path.read_text(encoding="utf-8"))
    architecture.update({
        "business_key": architecture.get("business_key") or "MD-NNN-RIGHTS-001",
        "uuid": None,
        "status": "DOCUMENTADO",
        "implemented": True,
        "publication": "HOLD",
        "assured": False,
        "layer": "L120",
        "owner_decision": "B",
        "chosen": ["OPT-B-IDENTIFIERS", "OPT-D-DEEPLINK"],
        "identity_catalog_ref": "MD-NNN-IDENTITY-001",
        "gap": (
            "UNBLOCK-NNN-LICENSE OPT-B CHOSEN: identity catalog (codes+URI+deep-link); "
            "canonical labels withheld; no NANDA/NIC/NOC dump"
        ),
    })
    options = list(architecture.get("options_for_owner") or [])
    by_id = {item.get("id"): dict(item) for item in options}
    if "OPT-B-IDENTIFIERS" in by_id:
        by_id["OPT-B-IDENTIFIERS"]["status"] = "CHOSEN"
    if "OPT-D-DEEPLINK" in by_id:
        by_id["OPT-D-DEEPLINK"]["status"] = "CHOSEN"
    if "OPT-A-LICENSE" in by_id:
        by_id["OPT-A-LICENSE"]["status"] = "HOLD_UNTIL_CONTRACT"
    architecture["options_for_owner"] = list(by_id.values()) or architecture.get("options_for_owner")
    architecture["recommended_now"] = "OPT-B-IDENTIFIERS + OPT-D-DEEPLINK chosen by owner. OPT-A só após contrato."
    _dump(arch_path, architecture)
    return {
        "agent_id": "AG-RIGHTS-BIND",
        "step": "NNN_OPT_B",
        "status": "REGISTERED",
        "owner_decision": "B",
        "population": catalog["population"],
        "licensed_text": False,
        "publication": "HOLD",
    }
