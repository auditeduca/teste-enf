# NIFS-700-19: Hallucination Prevention

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-19                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir as estratégias para prevenir alucinação da IA em contextos clínicos — onde um código inexistente ou uma recomendação sem evidência pode causar dano.

## 2. The Hallucination Problem

LLMs alucinam. Em enfermagem clínica, isto é inaceitável:

| Hallucination Type | Example | Danger |
|--------------------|---------|--------|
| Fake NANDA code | "NANDA 00999" | Código não existe |
| Fake NIC intervention | "NIC 9999: Super Healing" | Intervenção não existe |
| Fake evidence | "Cochrane 2025 says..." | Estudo não existe |
| Wrong probability | "P = 99%" | Falsa certeza |
| Invented relationship | "NANDA 00047 → NIC 0001" | Relação não existe |
| Fabricated drug info | "Noradrenalina is safe in pregnancy" | Pode matar |

## 3. Prevention Architecture (5 Layers)

```
┌─────────────────────────────────────────────────┐
│            HALLUCINATION PREVENTION              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Layer 1: GROUNDING (RAG)                       │
│  LLM só vê conhecimento do grafo                │
│  ↓                                              │
│  Layer 2: CODE VALIDATION                       │
│  Todo código deve existir no grafo              │
│  ↓                                              │
│  Layer 3: RELATIONSHIP VALIDATION               │
│  Toda relação deve existir como edge            │
│  ↓                                              │
│  Layer 4: PROBABILITY VALIDATION                │
│  Toda P(x) deve vir do Bayesian Engine          │
│  ↓                                              │
│  Layer 5: SAFETY CHECK                          │
│  Safety Agent + veto + human review             │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 4. Layer Details

### 4.1 Layer 1: Grounding (RAG)

- LLM recebe **apenas** contexto do knowledge graph
- Nada é gerado "de memória" do modelo
- Prompt template força uso do contexto

```
SYSTEM: "Você é um agente de diagnóstico de enfermagem.
Use APENAS os códigos e relações fornecidos no contexto.
NUNCA invente um código que não esteja no contexto.
Se não houver código apropriado, diga 'dados insuficientes'."

CONTEXT: [NANDA codes from graph traversal: 00047, 00046, 00085]
```

### 4.2 Layer 2: Code Validation

Pós-geração, todo código é validado:

```python
def validate_codes(output, graph):
    for code in extract_codes(output):
        if not graph.node_exists(code):
            raise HallucinationError(f"Code {code} does not exist in graph")
            # Block output, retry with stricter prompt
```

| Check | Action if Fail |
|-------|---------------|
| NANDA code exists in `ni.nanda_diagnoses` | Block + retry |
| NIC code exists in `ni.nic_interventions` | Block + retry |
| NOC code exists in `ni.noc_outcomes` | Block + retry |
| ISO term exists in `ni_iso.axis_terms` | Block + retry |
| CID code exists in `ni.cid_diagnoses` | Block + retry |

### 4.3 Layer 3: Relationship Validation

Toda relação citada deve existir como edge no grafo:

```python
def validate_relationships(output, graph):
    for rel in extract_relationships(output):
        edge = graph.find_edge(rel.source, rel.target, rel.type)
        if not edge:
            log_warning(f"Relationship {rel} not in graph — may be hallucinated")
            # Don't block, but flag for review
```

| Check | Action if Fail |
|-------|---------------|
| NANDA→NIC link exists | Flag warning |
| NANDA→NOC link exists | Flag warning |
| CALC→NANDA link exists | Flag warning |
| Cross-terminology mapping exists | Flag warning |

### 4.4 Layer 4: Probability Validation

Probabilidades **nunca** vêm do LLM. Vêm do Bayesian Engine:

```python
def validate_probabilities(output, bayesian_results):
    for prob in extract_probabilities(output):
        if not bayesian_results.has(prob.diagnosis):
            raise HallucinationError("Probability not computed by Bayesian Engine")
        if abs(prob.value - bayesian_results.get(prob.diagnosis)) > 0.01:
            raise HallucinationError("Probability mismatch with Bayesian Engine")
```

O LLM **não gera probabilidades**. Ele recebe as probabilidades do Bayesian Engine e as incorpora no texto.

### 4.5 Layer 5: Safety Check

O Safety Agent faz verificação final:

| Check | Action |
|-------|--------|
| Output has probability | Block if missing |
| Output has explanation | Block if missing |
| Output has human disclaimer | Append if missing |
| No contraindicated content | Veto if found |
| No fabricated evidence | Block + log |

## 5. Structured Output Enforcement

Em vez de texto livre, o LLM produz JSON estruturado:

```json
{
  "diagnosis_code": "00047",        // must be in graph
  "probability": 0.74,              // must be from Bayesian
  "confidence_interval": [0.68, 0.80],
  "intervention_codes": ["3540", "6540"],  // must be in graph
  "outcome_code": "1101",           // must be in graph
  "evidence_refs": ["grade_uuid_1"], // must exist
  "explanation": "Braden 12 + imobilidade..."  // free text (grounded)
}
```

Validação é campo por campo, não texto livre.

## 6. Hallucination Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code hallucination rate | < 0.5% | Validation checks |
| Relationship hallucination | < 2% | Edge validation |
| Probability hallucination | 0% | Bayesian enforcement |
| Evidence hallucination | < 1% | Reference validation |
| Total hallucination rate | < 2% | All checks combined |

## 7. Fallback Strategy

Se o LLM falha repetidamente (3 tentativas com code validation fail):

```
1. Attempt 1: LLM with RAG context → code validation fails
2. Attempt 2: Stricter prompt + fewer options → fails again
3. Attempt 3: Deterministic fallback (graph traversal only, no LLM)
4. Output: "Dados insuficientes para recomendação. Coletar mais observações."
```

**Determinístico é melhor que alucinado.**

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-01 | Foundation Model (Nurse-PaLM) |
| NIFS-700-02 | RAG (grounding mechanism) |
| NIFS-700-18 | Safety Layer (final guardrail) |
| NIFS-100-06 | Clinical Safety (safety hierarchy) |
| NIFS-1200-02 | Clinical Validation (hallucination testing) |

## 9. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — 5-layer prevention + structured output | Leivis Melo |
