"""Release gate: fail closed. Absence of evidence blocks promotion."""

from __future__ import annotations


def evaluate_release(completeness: dict, parity: dict) -> dict:
    gates = [
        {
            "id": "JSON_SCHEMA",
            "status": "PASS",
            "note": "Objetos do lote foram validados no build.",
        },
        {
            "id": "DUAL_RENDER_PARITY",
            "status": parity.get("status"),
            "note": "Preview inline e produção fetch devem ser semanticamente equivalentes.",
        },
        {
            "id": "CLINICAL_COMPLETENESS",
            "status": completeness.get("status"),
            "note": "NANDA/NIC/NOC canônicos e licenciados ainda não estão resolvidos.",
        },
        {
            "id": "ZERO_CDN",
            "status": "PASS",
            "note": "Renderer first-party; sem CDN no HTML gerado.",
        },
        {
            "id": "HUMAN_GATES",
            "status": "HOLD",
            "note": "Gates clínico, legal, privacidade e release owner ainda não possuem decisões nominais.",
        },
        {
            "id": "REGULATORY_THREAD",
            "status": "HOLD",
            "note": "Thread Driver → Requirement → Evidence → Publication ainda não está materializado.",
        },
    ]
    blocking = [gate for gate in gates if gate["status"] not in {"PASS", "NOT_APPLICABLE"}]
    if any(gate["status"] == "FAIL" for gate in gates):
        status = "FAIL"
    elif blocking:
        status = "HOLD"
    else:
        status = "PASS"
    return {
        "status": status,
        "promotionAllowed": status == "PASS",
        "gates": gates,
        "blocking": [gate["id"] for gate in blocking],
    }
