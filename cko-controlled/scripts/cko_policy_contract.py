"""Shared POLICY_MASTER_CONTRACT specialization helper.

DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED. Specialization is binding, not ACTIVE.
"""
from __future__ import annotations

POLICY_MASTER_ID = "POL-CKO-POLICY-MASTER-CONTRACT-1.0.0"
FAIL_CLOSED_ID = "POL-CKO-FAIL-CLOSED-1.0.0"
CASCADE = [
    "policy-as-code",
    "schemas",
    "graph-constraints",
    "CI-gates",
    "runtime-assertions",
    "automatic-evidence",
]
MASTER_FIELDS = [
    "IDENTITY",
    "AUTHORITY",
    "INTENT",
    "APPLICABILITY",
    "SCOPE",
    "SUBJECT",
    "MODALITY",
    "CONDITIONS",
    "CONSTRAINTS",
    "DECISION",
    "OUTCOME",
    "ENFORCEMENT",
    "CONTRACT",
    "IMPLEMENTATION",
    "TESTS",
    "CI_GATES",
    "RUNTIME_ASSERTIONS",
    "OBSERVABILITY",
    "EVIDENCE",
    "PROVENANCE",
    "GOVERNANCE",
    "EXCEPTIONS",
    "DEPENDENCIES",
    "VERSIONING",
    "LIFECYCLE",
    "CHANGE_IMPACT",
    "READINESS",
    "ASSURANCE",
]


def layer_policy_id(layer_id: str) -> str:
    if layer_id.startswith("CKO-"):
        return f"POL-CKO-LYR-{layer_id[4:]}-1.0.0"
    if layer_id.startswith("LYR-") and layer_id.endswith("-001"):
        return f"POL-CKO-LYR-{layer_id[4:-4]}-1.0.0"
    raise ValueError(f"unmapped layer id {layer_id}")


def specialize(
    *,
    policy_id: str,
    policy_name: str,
    policy_type: str,
    objective: str,
    deny_if: str,
    layers: list[str],
    authority: list[str],
    modality: str = "MUST_NOT",
    extra_identity: dict | None = None,
) -> dict:
    fields = {fid: {"status": "SPECIALIZED_HOLD", "implemented": False, "assured": False} for fid in MASTER_FIELDS}
    identity = {
        "policy_id": policy_id,
        "policy_name": policy_name,
        "policy_type": policy_type,
        "policy_status": "CONTROLLED_LAYER_HOLD" if policy_type == "LAYER" else "CONTROLLED_EXTRACTION_HOLD",
    }
    if extra_identity:
        identity.update(extra_identity)
    fields["IDENTITY"].update(identity)
    fields["AUTHORITY"].update({"sources": authority})
    fields["INTENT"].update(
        {
            "objective": objective,
            "desired_state": "human_signed_or_explicit_hold",
            "prohibited_state": "silent_bypass_or_release",
        }
    )
    fields["APPLICABILITY"].update({"mode": "REQUIRED"})
    fields["SCOPE"].update({"layers": layers})
    fields["SUBJECT"].update({"actors": ["HUMAN", "AGENT"], "objects": ["PLATFORM", "RELEASE"]})
    fields["MODALITY"].update({"type": modality})
    fields["DECISION"].update({"deny_if": [deny_if], "allow_if": ["human.signed == true"]})
    fields["OUTCOME"].update({"on_deny": "HOLD", "on_allow": "HUMAN_REVIEW", "severity": "BLOCKER"})
    fields["ENFORCEMENT"].update({"preventive": ["INSPECT", "CI_GATE"], "detective": ["LEDGER"]})
    fields["GOVERNANCE"].update(
        {
            "owner": "HUMAN",
            "approval_required": True,
            "human_boundary": "FINAL_APPROVAL",
            "blocking_inspect": False,
            "blocking_release": True,
        }
    )
    fields["READINESS"].update({"score": "NOT_READY", "active": False})
    fields["ASSURANCE"].update({"verdict": "HOLD", "release_allowed": False})
    assert list(fields) == MASTER_FIELDS
    return {
        "contract_id": POLICY_MASTER_ID,
        "status": "SPECIALIZED_HOLD",
        "implemented": False,
        "assured": False,
        "field_count": 28,
        "fields": fields,
    }
