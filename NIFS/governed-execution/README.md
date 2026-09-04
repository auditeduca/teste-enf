# Governed Execution — CAL-IMC-001

Executable reference for the constitutional chain of the Nursing Intelligence OS:

```
POLICY-AS-CODE → SCHEMA → GRAPH CONSTRAINTS → CI GATES → REGISTRY
    → RUNTIME ASSERTIONS → EXECUTION → EVIDENCE → AUDIT → LEARNING
```

This is not a page with a JavaScript formula. `CAL-IMC-001` is a governed object: semantically constrained, blocked in CI if invalid, re-authorized at runtime, and capable of emitting its own evidence — including denied attempts.

## Why BMI?

BMI is simple enough to demonstrate the architecture without becoming a clinical prescription. The same contract applies to any `CAL`, `SCL`, protocol, agent, Digital Twin, model, or API.

## Run

```bash
# Full constitutional scenario (human + agent + twin + deny + drift)
python3 NIFS/governed-execution/run.py scenario

# CI promotion gates
python3 NIFS/governed-execution/run.py ci

# Direct calculation
python3 NIFS/governed-execution/run.py calculate --weight 70 --height 1.75

# Invalid input is denied and still emits evidence
python3 NIFS/governed-execution/run.py calculate --weight 70 --height 0

# LLM arithmetic is forbidden
python3 NIFS/governed-execution/run.py calculate --weight 70 --height 1.75 --engine LLM

# Digital Twin derives an observation; it does not calculate by itself
python3 NIFS/governed-execution/run.py twin

# Tests
python3 -m unittest discover -s NIFS/governed-execution/tests -v

# Desktop console
python3 NIFS/governed-execution/desktop/server.py
# http://127.0.0.1:8090/
```

## Object pack

`objects/CAL-IMC-001/` is the closed object:

| Contract | Role |
|----------|------|
| `canonical.json` | Identity, formula, governance |
| `input.schema.json` | Structural enforcement |
| `fields.json` | Universal field constraints |
| `vocabulary.json` | Controlled terms |
| `ontology.json` / `ontology.ttl` | Semantic mapping |
| `graph-constraints.json` / `graph.shacl.ttl` | Semantic enforcement |
| `policy.json` | Permissions, prohibitions, obligations |
| `ci-gates.json` | Promotion enforcement |
| `registry.json` | Operational truth of the approved version |
| `runtime-assertions.json` | Execution-time revalidation |
| `agent.json` | Use vs mutate |
| `evidence-contract.json` | Automatic proof |
| `twin-contract.json` | Governed operational context |

`objects/knowledge-licensing-registry.json` records that NANDA/NIC/NOC and proprietary corpora require licenses. The OS orchestrates licensed knowledge; it does not clone it.

## Constitutional rules

```
NO REQUIREMENT WITHOUT POLICY
NO POLICY WITHOUT ENFORCEMENT
NO OBJECT WITHOUT SCHEMA
NO RELATION WITHOUT GRAPH CONSTRAINT
NO RELEASE WITHOUT CI GATE
NO ACTION WITHOUT RUNTIME ASSERTION
NO EXECUTION WITHOUT EVIDENCE
NO EVIDENCE WITHOUT PROVENANCE
NO GOVERNED SYSTEM WITHOUT AUDIT
```

LLM ≠ source of truth, calculation engine, policy engine, authorization engine, or evidence store.

Specification: `NIFS/1100-GOVERNANCE/1100-11-executable-governance.md` and `NIFS/APPENDIX/H-examples.md`.
