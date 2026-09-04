# NIFS-1100-11: Executable Governance

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-1100-11                       |
| Status        | Active                             |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-09-03                         |

## 1. Purpose

Definir a **espinha dorsal constitucional** do Nursing Intelligence OS: governança executável.

Policy não é documentação. Policy é código. Schema não é apenas estrutura: é enforcement estrutural. Graph constraint não é apenas ontologia: é enforcement semântico. CI gate não é apenas teste: é enforcement de promoção. Runtime assertion não é apenas log: é enforcement operacional. Evidence não é relatório produzido depois: é subproduto automático da execução.

## 2. Constitutional formula

```
POLICY + SCHEMA + GRAPH + CI + RUNTIME + EVIDENCE
= GOVERNED EXECUTION
```

Ciclo superior:

```
GOVERNANCE → ENFORCEMENT → EXECUTION → EVIDENCE
    → ASSURANCE → LEARNING → POLICY EVOLUTION
```

## 3. Executable governance cycle

```
                 GOVERNANÇA EXECUTÁVEL
                         │
                         ▼
                 POLICY-AS-CODE
                         │
                         ▼
                      SCHEMAS
                         │
                         ▼
                 GRAPH CONSTRAINTS
                         │
                         ▼
                     CI GATES
                         │
                         ▼
                 RUNTIME ASSERTIONS
                         │
                         ▼
                 AUTOMATIC EVIDENCE
                         │
                         └──────────────┐
                                        ▼
                              FEEDBACK / DRIFT
                                        │
                                        ▼
                                  POLICY UPDATE
```

| Layer | Constitutional question | Function |
|-------|-------------------------|----------|
| Policy-as-Code | É permitido? | Rules, limits, obligations, prohibitions |
| Schemas | Está formalmente correto? | Structure, types, cardinality, contracts |
| Graph Constraints | Está semanticamente correto? | Relations, dependencies, coherence |
| CI Gates | Pode ser promovido? | Invalid artifacts cannot advance |
| Runtime Assertions | Continua permitido agora? | Revalidation in execution context |
| Automatic Evidence | Podemos provar o que aconteceu? | Verifiable evidence as a byproduct |

## 4. Mother rules

These rules are binding on every object, agent, model, calculator, twin, and API:

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

If a requirement does not reach enforcement, it is only documentation.

```
REQUIREMENT → POLICY → SCHEMA → CONSTRAINT → VALIDATOR
    → CI GATE → RUNTIME ASSERTION → EVIDENCE
```

## 5. Object readiness

An object is not ready because its JSON is valid. It is ready when it has crossed:

```
DEFINED → SCHEMA VALIDATED → GRAPH VALIDATED → POLICY VALIDATED
    → CI VALIDATED → RUNTIME VALIDATED → EVIDENCE VALIDATED
    → AUDITED → CLOSED
```

Definition of Done for a governed object:

```
OBJECT + IDENTITY + SCHEMA + VOCABULARY + ONTOLOGY + GRAPH + POLICY
 + VALIDATOR + CI GATES + REGISTRY + RUNTIME + EVIDENCE + PROVENANCE
 + AUDIT + TESTS + SECURITY + PRIVACY + ACCESSIBILITY + VERSIONING
 + RECOVERY + DOCUMENTATION
 = CLOSED
```

A canonical object (for example `CALCULATOR`) therefore carries identity, schema, vocabulary, ontology mapping, graph constraints, policies, validators, CI gates, runtime assertions, evidence contract, provenance, audit contract, security, privacy, accessibility, renderer/API/event contracts.

## 6. Agents

An agent does not receive "do X". It receives:

```
MISSION → OBJECTIVE → PLAN → TASK → CAPABILITY → POLICY RESOLUTION
    → AUTHORIZATION → RUNTIME ASSERTIONS → TOOL EXECUTION
    → OUTPUT VALIDATION → EVIDENCE → AUDIT
```

No agent may execute an action merely because a model decided to. The model may propose. The architecture decides whether execution is allowed. Agents may **use** a tool; they may not **alter** policy, schema, or runtime.

## 7. Digital Twin

```
TWIN STATE → CONTEXT → POLICY → SCHEMA → GRAPH CONSTRAINT
    → RISK EVALUATION → AGENT DECISION → RUNTIME ASSERTION
    → ACTION → TWIN STATE UPDATE → EVIDENCE
```

The twin is governed operational state. It supplies context; it does not become the calculation engine.

Observations remain observations. A BMI value is a **derived observation** with derivation provenance.

## 8. Nurse-PaLM subordination

```
USER / AGENT → TASK → CONTEXT → POLICY → MODEL ROUTER → APPROVED MODEL
    → RAG / KNOWLEDGE GRAPH → REASONING → SAFETY CHECK
    → OUTPUT VALIDATION → RUNTIME ASSERTION → RESPONSE / ACTION → EVIDENCE
```

Non-negotiable:

```
LLM ≠ SOURCE OF TRUTH
LLM ≠ CALCULATION ENGINE
LLM ≠ POLICY ENGINE
LLM ≠ AUTHORIZATION ENGINE
LLM ≠ EVIDENCE STORE
```

The model is an intelligence component inside a larger architecture.

## 9. Competitive posture

ClinicalKey, Nursing Central, Davis, NANDA/INKA and Med-PaLM are best-in-class in content, reference, vertical depth, nursing language, and foundation intelligence. This kernel does not clone their corpora. It is the infrastructure layer that connects licensed sources, native knowledge, terminologies, evidence, models, calculators, Digital Twins and agents — with explicit licensing and provenance.

See `NIFS/governed-execution/objects/knowledge-licensing-registry.json`. Commercial use of NANDA/NIC/NOC requires a formal license.

## 10. Reference implementation

The first closed object is `CAL-IMC-001`:

- Kernel: `NIFS/governed-execution/`
- Worked example: [NIFS-APP-H](../APPENDIX/H-examples.md)

BMI is used because it demonstrates the full chain without becoming a clinical prescription. The same contract is reusable for any governed object.

## 11. Change Log

| Version | Date       | Change                                      | Author      |
|---------|------------|---------------------------------------------|-------------|
| 1.0.0   | 2026-09-03 | Constitutional kernel and CAL-IMC-001 example | Leivis Melo |
