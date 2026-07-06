# NIFS-700-14: Tool Calling

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-14                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o Nurse-PaLM invoca ferramentas externas (calculadoras, APIs clínicas, bases de conhecimento) durante o raciocínio.

## 2. Tool Architecture

```
LLM receives clinical context
    ↓
LLM decides: "I need to calculate Braden score"
    ↓
Tool call: { tool: "braden_calculator", params: {...} }
    ↓
Tool executes (NKOS calculator engine)
    ↓
Result: { score: 12, risk: "high" }
    ↓
LLM incorporates result into reasoning
    ↓
Next tool call or final recommendation
```

## 3. Available Tools

| Tool | Function | NKOS Reference |
|------|----------|----------------|
| `calculator_run` | Execute clinical calculator | `clinical/calculator_definitions.json` (100 tools) |
| `nanda_lookup` | Query NANDA by code/symptom | `clinical/nursing_diagnoses.json` |
| `nic_lookup` | Query NIC by code | `clinical/nursing_interventions.json` |
| `drug_interaction_check` | Check drug interactions | `clinical/drug_interactions.json` |
| `evidence_search` | Search evidence base | `clinical/evidence.json` |
| `guideline_search` | Search clinical guidelines | `clinical/clinical_guidelines.json` |
| `legislation_check` | Verify compliance | `regulatory/br/legal_provisions.json` |
| `graph_traverse` | Traverse knowledge graph | `ni_graph.edges` |
| `memory_recall` | Recall similar episodes | `ni_memory.episodes` |
| `simulation_run` | Run MCTS/particle filter | `clinical-engine/` |

## 4. NKOS Calculator Engine

O CALENF-NKD tem 100 calculadoras clínicas definidas:

```json
// From calculator_definitions.json
{
  "tool_code": "APGAR",
  "parameters": [{ "name": "appearance", "type": "select", "options": [0,1,2] }, ...],
  "formula": "sum(appearance + pulse + grimace + activity + respiration)",
  "interpretation_bands": [
    { "range": "0-3", "label": "Severe distress" },
    { "range": "4-6", "label": "Moderate distress" },
    { "range": "7-10", "label": "Normal" }
  ]
}
```

## 5. Tool Calling Protocol

```json
{
  "tool": "calculator_run",
  "parameters": { "tool_code": "BRADEN", "inputs": {...} },
  "expect": { "type": "object", "properties": { "score": "number", "risk": "string" } }
}
```

Response:
```json
{ "score": 12, "risk": "high", "recommendation": "NANDA 00047 likely" }
```

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-13 | Prompt Strategy (tool calling in prompts) |
| NIFS-700-08 | Agents (agents call tools) |
| NIFS-900-03 | Calculators (tool definitions) |
