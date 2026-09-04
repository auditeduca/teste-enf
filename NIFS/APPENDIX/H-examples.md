# NIFS-APP-H: Examples

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-APP-H                         |
| Status        | Active                             |
| Version       | 1.1.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-09-03                         |

## 1. Purpose

Worked example of the constitutional chain, from Policy-as-Code to automatic evidence, connected to Calculator → Knowledge Graph → Agent → Digital Twin → Runtime → Audit.

Object: `CAL-IMC-001`  
Name: Calculadora de Índice de Massa Corporal  
Version: `1.0.0`  
Formula: `weight_kg / (height_m * height_m)`

Executable pack: `NIFS/governed-execution/`  
Specification: [NIFS-1100-11](../1100-GOVERNANCE/1100-11-executable-governance.md)

## 2. Why this example

A traditional system does: User → Frontend → JavaScript → Result.  
A modern API does: User → API → Calculator → Result.  
A generic AI system does: User → LLM → RAG → Answer.

This example does something else:

```
GOVERNANCE → POLICY-AS-CODE → SCHEMA + GRAPH → CI GATES → REGISTRY
    → RUNTIME → (AGENT | TWIN | HUMAN) → EXECUTION → EVIDENCE
    → AUDIT → OUTCOME → LEARNING → POLICY EVOLUTION
```

BMI is intentionally non-prescriptive. The same closed contract applies to any `CAL`, `SCL`, protocol, content object, ML model, RAG corpus, agent, Digital Twin, API, tool, workflow, or decision.

## 3. Scenario flow

```
POLICY → SCHEMA → VOCABULARY → ONTOLOGY → GRAPH CONSTRAINTS
    → VALIDATORS → CI GATES → REGISTRY → DEPLOYMENT → RUNTIME
    → CALCULATION → AGENT → DIGITAL TWIN → EVIDENCE → AUDIT
    → LEARNING / DRIFT
```

## 4. Policy-as-Code

`POL-CAL-IMC-001` encodes obligations and prohibitions, including:

| Rule | Meaning | Enforcement |
|------|---------|-------------|
| POL-IMC-001 / 002 | Weight and height required | Schema + runtime |
| POL-IMC-003 / 004 | Non-positive values prohibited | Schema + policy |
| POL-IMC-005 | Formula is deterministic | Policy + engine |
| POL-IMC-006 | LLM arithmetic prohibited | Policy + runtime assertion |
| POL-IMC-007 / 008 | Evidence and provenance required | Evidence contract |

`weight_kg = -5` is not "a bad value". It is a **schema violation**.  
`height_m = 0` is denied before division. The denied attempt still emits `EXECUTION_DENIED`.

## 5. Structural vs semantic validity

JSON Schema accepts structure. Graph constraints catch meaning.

A calculator with input `temperature` and output `BMI` can be structurally valid JSON and still be a **graph violation**, because `CAL-IMC-001` must have `cko:BodyWeight` and `cko:BodyHeight` as inputs and `cko:BodyMassIndex` as output.

## 6. CI vs runtime

"Valid" is not the same as "may enter production".

```
Pull Request → GATE schema → fields → vocabulary → graph → policy
    → security → tests → evidence → accessibility → provenance → DEPLOY
```

On failure: `on_failure: BLOCK`. Invalid code does not reach the registry.

The registry is the operational source of truth for which version may execute.

## 7. Runtime

A request is not executed immediately:

```
REQUEST → IDENTITY → VERSION → POLICY RESOLUTION → AUTHORIZATION
    → SCHEMA → GRAPH CONTEXT → RUNTIME ASSERTIONS → EXECUTION
```

Assertions include: calculator active, version approved, policy active, input valid, graph valid, engine deterministic, evidence capture enabled.

Successful canonical result for `70 kg / 1.75 m`:

```
bmi = 22.857142857142858 kg/m2
presented = 22.9   # rounding does not replace the canonical value
```

## 8. Evidence and provenance

Every execution, including denials, produces:

- what, who, when
- which calculator version, policy version, schema version
- input hash, output hash
- engine
- validation and assertion results

Provenance chain:

```
Policy v1.0.0 → Calculator v1.0.0 → Schema v1.0.0
    → Input hash → Execution → Output hash → Evidence
```

## 9. Agent

`AGENT-NURSE-001` may use `CAL-IMC-001` at autonomy L2. It cannot modify the calculator, modify policy, override runtime, or bypass validation.

User: "Calcule o IMC desse paciente."

```
USER → AGENT → MISSION → TASK → CAPABILITY → POLICY RESOLUTION
    → CALCULATOR REGISTRY → CAL-IMC-001 → RUNTIME → CALCULATION
    → EVIDENCE → AGENT RESPONSE
```

Invalid agent input (`height_m: 0`) is denied with evidence. That is required: a blocked attempt is still an auditable event.

## 10. Digital Twin

`DT-PATIENT-001` stores observations (`70 kg`, `1.75 m`). The twin does not calculate. It supplies context. The calculator derives `body_mass_index` as a **derived observation** supported by evidence `EVT-…`.

Knowledge graph (conceptual):

```
Digital Twin --hasObservation--> Body Weight 70 kg
Digital Twin --hasObservation--> Body Height 1.75 m
CAL-IMC-001 --derives--> BMI 22.857…
BMI --supported_by--> Evidence
```

## 11. Audit questions the log can answer

- Who executed? `AGENT-NURSE-001` or `NURSE-001`
- Which tool and version? `CAL-IMC-001` `1.0.0`
- Which policy and schema?
- Which input, result, engine?
- Which gates passed or failed?

## 12. How to run

```bash
python3 NIFS/governed-execution/run.py scenario
python3 NIFS/governed-execution/run.py ci
python3 NIFS/governed-execution/run.py calculate --weight 70 --height 1.75
python3 -m unittest discover -s NIFS/governed-execution/tests -v
```

## 13. Change Log

| Version | Date       | Change                                         | Author      |
|---------|------------|------------------------------------------------|-------------|
| 1.0.0   | 2026-07-05 | Stub                                           | —           |
| 1.1.0   | 2026-09-03 | CAL-IMC-001 governed execution worked example  | Leivis Melo |
