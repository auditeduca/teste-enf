# NIFS-600-18: Consensus Engine

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-18                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o motor de consenso multiagente — o mecanismo pelo qual múltiplos agentes especializados deliberam, votam e produzem uma decisão clínica conjunta com dissidências registradas.

## 2. Why Multi-Agent?

Um único agente tem viés, pontos cegos e não consegue deliberar. Na prática clínica real, decisões complexas são tomadas em equipe. O NIS modela isto:

```
Em vez de:
  [Agente Único] → "Diagnóstico: 00047"

O NIS faz:
  [Assessment Agent]  → "Observações válidas, qualidade 8/10"
  [NANDA Agent]       → "00047 (74%), 00046 (18%), 00085 (6%)"
  [NIC Agent]         → "Recomendo NIC 3540 + NIC 6540"
  [NOC Agent]         → "Espero NOC 1101 de 2→4 em 72h"
  [Safety Agent]      → "Sem conflitos de segurança detectados"
  [Medication Agent]  → "Noradrenalina + cuidado com extravasamento"
  [Evidence Agent]    → "GRADE A: Braden ≤ 12 → UP risco 87%"
  [Consensus Agent]   → "Consenso: 00047 + NIC 3540/6540 + monitorar NOC 1101"
                          Agreement score: 0.87
                          Dissenting: Safety Agent (parcial, quer protocol C backup)
```

## 3. Agent Catalog

### 3.1 Core Agents

| Agent ID | Type | Specialty | Role |
|----------|------|-----------|------|
| `COUNCIL.ASSESS.001` | assessment | General | Valida qualidade das observações |
| `COUNCIL.NANDA.001` | nanda | Diagnóstico | Gera e ranqueia hipóteses diagnósticas |
| `COUNCIL.NIC.001` | nic | Intervenção | Propõe intervenções apropriadas |
| `COUNCIL.NOC.001` | noc | Desfecho | Define desfechos esperados e métricas |
| `COUNCIL.SAFETY.001` | safety | Segurança | Verifica conflitos, riscos, contraindicações |
| `COUNCIL.MED.001` | medication | Farmacologia | Verifica medicamentos, interações, doses |
| `COUNCIL.EVID.001` | evidence | Evidência | Valida qualidade e relevância da evidência |
| `COUNCIL.CONS.001` | consensus | Arbitragem | Agrega votos e produz decisão final |

### 3.2 Specialist Agents (Optional, by context)

| Agent ID | Specialty | Activated When |
|----------|-----------|----------------|
| `COUNCIL.CARDIO.001` | Cardiologia | Paciente cardíaco ou sinais cardio anormais |
| `COUNCIL.NEURO.001` | Neurologia | Glasgow < 15 ou sintomas neurológicos |
| `COUNCIL.RENAL.001` | Nefrologia | Creatinina alterada ou diurese reduzida |
| `COUNCIL.INFECT.001` | Infectologia | Suspeita de sepse ou infecção |
| `COUNCIL.GERI.001` | Geriatria | Paciente ≥ 65 anos |
| `COUNCIL.PEDIAT.001` | Pediatria | Paciente pediátrico |
| `COUNCIL.NEONAT.001` | Neonatologia | Paciente neonatal |

## 4. Deliberation Process

### Round 1: Independent Assessment

Cada agente recebe os dados e produz sua posição independentemente:

```json
{
  "agent_id": "COUNCIL.NANDA.001",
  "round": 1,
  "position": {
    "primary_diagnosis": "00047",
    "probability": 0.74,
    "alternatives": ["00046 (0.18)", "00085 (0.06)"],
    "reasoning": "Braden 12 + imobility + ICU + postop → 00047"
  },
  "confidence": 0.82,
  "evidence_refs": ["grade_id_1", "grade_id_2"]
}
```

### Round 2: Cross-Examination

Agentes veem as posições dos outros e podem:
- **Maintain**: manter posição original
- **Adjust**: modificar confiança ou diagnóstico
- **Concede**: aceitar posição de outro agente
- **Object**: discordar formalmente com argumento

```json
{
  "agent_id": "COUNCIL.SAFETY.001",
  "round": 2,
  "changed_from_previous": true,
  "position": {
    "agreement_with_nanda": "partial",
    "concern": "00047 ok, mas recomendo protocol C como backup se NIC 3540 falhar",
    "veto": false
  },
  "confidence": 0.90
}
```

### Round 3: Consensus Formation

O Consensus Agent agrega todas as posições:

1. **Vote tally**: conta posições por diagnóstico
2. **Weighted vote**: pondera por `voting_weight` de cada agente
3. **Dissent analysis**: registra quem discordou e por quê
4. **Confidence aggregation**: combina confianças individuais

## 5. Consensus Protocols

| Protocol | When Used | Threshold | Quorum |
|----------|-----------|-----------|--------|
| `majority` | Decisões rotineiras | > 50% | 5/8 agents |
| `weighted_majority` | Padrão | weighted > 0.60 | 6/8 agents |
| `unanimous` | Alto risco | 100% | 8/8 agents |
| `threshold` | Decisões críticas | score ≥ 0.75 | 7/8 agents |
| `deliberative` | Casos complexos | iterative until stable | all must speak |

## 6. Veto Mechanism

Agentes com `veto_eligible = true` podem bloquear uma decisão:

| Agent | Veto Power | When |
|-------|-----------|------|
| Safety Agent | ✅ | Safety concern não endereçado |
| Medication Agent | ✅ | Interação medicamentosa grave |
| Human Reviewer | ✅ | Sempre (final authority) |

Veto gera `ni_council.veto_events` com:
- Agent ID
- Motivo
- Condição para levantar veto
- Escalação se necessário

## 7. Agreement Score

```
agreement_score = 1 - (variance of agent positions / max possible variance)
```

| Score | Interpretation | Action |
|-------|---------------|--------|
| > 0.85 | Forte consenso | Propor decisão |
| 0.70–0.85 | Consenso moderado | Propor com ressalvas |
| 0.50–0.70 | Consenso fraco | Rodada adicional ou human review |
| < 0.50 | Sem consenso | Escalar para revisão humana |

## 8. Arbitration

Quando não há consenso e há conflito direto (`ni_cog.conflicting_evidence`):

1. Arbitration Agent avalia ambas as posições
2. Considera: evidence grade, agent track record, context fit
3. Escolhe `winner_node_id`
4. Registra em `ni_council.arbitration_decisions`
5. Se não resolver: **human review obrigatório**

## 9. Human-in-the-Loop

```
Council Decision
    ↓
Human Reviewer
    ↓
┌─────────────────┐
│ Accept          │ → Aplicar, feedback positivo
│ Modify          │ → Aplicar modificada, feedback parcial
│ Reject          │ → Não aplicar, feedback negativo
│ Escalate        │ → Segunda opinião, especialista humano
└─────────────────┘
    ↓
ni_council.human_decisions
    ↓
ni_learning.feedback → weight_updates
```

## 10. Agent Performance Tracking

Cada agente é avaliado continuamente:

| Metric | Description | Target |
|--------|-------------|--------|
| Vote accuracy | % de votos alinhados com desfecho real | > 80% |
| Calibration | |predicted confidence - actual accuracy| | < 0.10 |
| Veto precision | % de vetos que evitaram dano | > 90% |
| Response time | Latência média de deliberação | < 1.5s |
| Contribution | Score de utilidade por sessão | > 0.5 |

Agentes com performance ruim podem ser:
- Re-treinados (ajustar prompt/weights)
- Desativados (`active = false`)
- Substituídos (nova versão)

## 11. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_council.agents` | Registro de agentes |
| `ni_council.agent_roles` | Papéis por sessão |
| `ni_council.consensus_protocols` | Protocolo de cada sessão |
| `ni_council.deliberation_log` | Log de cada rodada |
| `ni_council.consensus_results` | Resultado final |
| `ni_council.votes` | Votos individuais |
| `ni_council.veto_events` | Vetos |
| `ni_council.human_decisions` | Decisões humanas |
| `ni_council.arbitration_decisions` | Arbitragem |
| `ni_council.agent_performance` | Métricas de performance |

## 12. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (Stage 6) |
| NIFS-700-08 | Agents (implementation) |
| NIFS-700-09 | Multi-Agent (coordination) |
| NIFS-700-10 | Consensus (protocol detail) |
| NIFS-600-19 | Explainability (dissent is explainable) |

## 13. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full council specification | Leivis Melo |
