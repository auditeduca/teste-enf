# NIFS-700-09: Multi-Agent

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-09                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a arquitetura técnica de coordenação multiagente — como múltiplos agentes especializados se comunicam, deliberam e produzem decisões conjuntas no Conselho Clínico.

## 2. Agent Architecture

Cada agente é uma entidade independente com:

```
┌────────────────────────────────────┐
│           CLINICAL AGENT           │
├────────────────────────────────────┤
│  Identity                          │
│  ├─ agent_id (COUNCIL.NANDA.001)   │
│  ├─ agent_type (nanda)             │
│  └─ specialty (diagnóstico)        │
├────────────────────────────────────┤
│  Knowledge Scope                   │
│  ├─ domains (cardio, neuro, ...)   │
│  ├─ populations (adult, ICU, ...)  │
│  └─ terminologies (NANDA, NIC)     │
├────────────────────────────────────┤
│  Cognitive Engine                  │
│  ├─ RAG retriever (own knowledge)  │
│  ├─ Graph traversal (own scope)    │
│  ├─ Bayesian calculator            │
│  └─ Prompt template (specialized)  │
├────────────────────────────────────┤
│  Output                            │
│  ├─ Position (JSON)                │
│  ├─ Confidence (0-1)               │
│  ├─ Evidence refs                  │
│  ├─ Argument text (natural lang)   │
│  └─ Vote (for/against/abstain)     │
├────────────────────────────────────┤
│  Feedback Channel                  │
│  ├─ See other agents' positions    │
│  ├─ Adjust own position            │
│  └─ Veto (if eligible)             │
└────────────────────────────────────┘
```

## 3. Communication Protocol

### 3.1 Message Bus

Agentes se comunicam via um message bus estruturado:

```
Session starts
    ↓
Broadcast: "Here is the clinical case: {observations, context}"
    ↓
Each agent processes independently (Round 1)
    ↓
Broadcast: "All positions: {agent_1: pos, agent_2: pos, ...}"
    ↓
Each agent reviews others (Round 2)
    ↓
Broadcast: "Updated positions"
    ↓
Consensus Agent aggregates (Round 3)
    ↓
Output: Final decision
```

### 3.2 Message Format

```json
{
  "message_type": "deliberation",
  "session_id": "uuid",
  "round": 2,
  "from_agent": "COUNCIL.SAFETY.001",
  "position": {
    "agree_with": "COUNCIL.NANDA.001",
    "diagnosis": "00047",
    "intervention": "3540",
    "concerns": ["recommend protocol C backup"],
    "veto": false,
    "confidence": 0.90
  },
  "evidence_refs": ["grade_uuid_1"],
  "timestamp": "2026-07-05T10:30:15Z"
}
```

## 4. Agent Implementation

### 4.1 LLM-Based Agents (Phase 1)

Cada agente é um LLM com prompt especializado:

| Agent | System Prompt Focus | Knowledge Source |
|-------|-------------------|-----------------|
| Assessment Agent | "Você é especialista em avaliação clínica. Valide a qualidade e completude das observações." | Gordon patterns, assessment tools |
| NANDA Agent | "Você é especialista em diagnóstico de enfermagem. Gere hipóteses NANDA ranqueadas com probabilidades." | NANDA taxonomy, graph traversal |
| NIC Agent | "Você é especialista em intervenções de enfermagem. Selecione NIC apropriados baseado no diagnóstico." | NIC taxonomy, NNN links |
| NOC Agent | "Você é especialista em desfechos de enfermagem. Defina NOC esperados com valores-alvo." | NOC taxonomy, outcome patterns |
| Safety Agent | "Você é o guardião de segurança. Identifique riscos, contraindicações e eventos adversos potenciais." | Safety goals, 9 rights, protocols |
| Medication Agent | "Você é farmacêutico clínico. Verifique interações, doses, vias e contraindicações." | ANVISA, ATC, RxNorm, drug interactions |
| Evidence Agent | "Você é especialista em evidência científica. Valide a qualidade e relevância das evidências citadas." | GRADE framework, literature database |
| Consensus Agent | "Você é o árbitro. Agregue todas as posições e produza a decisão final com agreement score." | All positions, voting protocol |

### 4.2 Hybrid Agents (Phase 2)

Combinação de LLM + módulos determinísticos:

```
NANDA Agent:
  ├── LLM: gera texto explicativo
  ├── Graph traversal: encontra NANDA nodes (determinístico)
  ├── Bayesian calculator: computa P(x) (determinístico)
  └── Output: texto + JSON estruturado + P(x)
```

### 4.3 Specialized Models (Phase 3)

Modelos fine-tuned por especialidade:

| Agent | Training Data | Architecture |
|-------|--------------|--------------|
| NANDA Agent | 10K labeled diagnostic cases | Fine-tuned LLM |
| Safety Agent | 1K adverse event cases | Classifier + LLM |
| Medication Agent | Drug interaction database | Knowledge graph + LLM |

## 5. Agent Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  IDLE    │───→│ ASSIGNED │───→│DELIBERATE│───→│  VOTE    │
│ (waiting)│    │ (session │    │ (process │    │ (submit  │
│          │    │  starts) │    │  case)   │    │  position)│
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                      │
                    ┌─────────────────────────────────┘
                    │
               ┌────▼─────┐    ┌──────────┐    ┌──────────┐
               │  REVIEW  │───→│  ADJUST  │───→│  DONE    │
               │ (see     │    │ (change  │    │ (output  │
               │  others) │    │  position│    │  logged) │
               └──────────┘    │  if needed│   └──────────┘
                               └──────────┘
```

## 6. Consensus Aggregation Algorithm

```python
def aggregate_consensus(positions, protocol):
    """
    positions: list of {agent_id, diagnosis, confidence, vote}
    protocol: {type: 'weighted_majority', threshold: 0.60, quorum: 6}
    """
    # 1. Check quorum
    if len(positions) < protocol.quorum:
        return ConsensusResult(type='no_consensus', reason='insufficient_quorum')
    
    # 2. Tally votes weighted by agent voting_weight
    tally = defaultdict(float)
    for pos in positions:
        tally[pos.diagnosis] += pos.confidence * pos.voting_weight
    
    # 3. Normalize
    total = sum(tally.values())
    probabilities = {d: v/total for d, v in tally.items()}
    
    # 4. Check threshold
    top_diagnosis = max(probabilities, key=probabilities.get)
    top_score = probabilities[top_diagnosis]
    
    if top_score >= protocol.threshold:
        return ConsensusResult(
            type='reached',
            decision=top_diagnosis,
            probability=top_score,
            agreement_score=calculate_agreement(positions)
        )
    else:
        return ConsensusResult(
            type='partial',
            top_candidate=top_diagnosis,
            agreement_score=calculate_agreement(positions),
            recommended_action='human_review'
        )
```

## 7. Failure Modes & Mitigations

| Failure | Cause | Mitigation |
|---------|-------|-----------|
| Agent timeout | LLM latency > 3s | Default to abstain, proceed with others |
| Agent hallucination | LLM invents NANDA code | Code validation against graph |
| All agents agree too fast | Herding / groupthink | Force Round 2 with devil's advocate |
| Persistent disagreement | Genuine clinical ambiguity | Escalate to human review |
| Veto loop | Safety + Medication both veto | Escalate to human + log conflict |
| Agent degradation | Performance drops over time | Performance tracking + retraining |

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-18 | Consensus Engine (clinical protocol) |
| NIFS-700-08 | Agents (individual agent design) |
| NIFS-700-10 | Consensus (aggregation algorithms) |
| NIFS-700-13 | Prompt Strategy (agent prompts) |
| NIFS-700-18 | Safety Layer (veto mechanism) |

## 9. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — agent architecture + coordination | Leivis Melo |
