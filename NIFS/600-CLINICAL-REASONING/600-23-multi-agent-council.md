# NIFS-600-23 — Multi-Agent Council Engine

**Seção:** 600 (Clinical Reasoning)
**Camada cognitiva:** 10 — Multi-Agent Council
**Status:** ✅ Implementado (v5.0)
**Arquivo de código:** `reference-clinical-engine/council/councilEngine.js`
**Schema DDL:** `ni_council` (6 tabelas)

## 1. Propósito

Orquestra múltiplos agentes especialistas que **deliberam em rodadas**, **votam** em decisões clínicas e **alcançam consenso** (ou registram dissidência). Cada agente tem uma especialidade distinta (diagnóstico NANDA, intervenção NIC, safety, farmácia, evidência) e contribui com sua perspectiva antes que uma decisão final seja tomada.

Esta camada é crítica para:
- **Segurança clínica:** o agente de safety tem poder de veto
- **Robustez:** decisões não dependem de um único modelo
- **Explicabilidade:** o log de deliberação rastreia quem disse o quê e por quê
- **Qualidade:** a evidência é ponderada explicitamente

## 2. Arquitetura

```
┌───────────────────────────────────────────────────────┐
│              Multi-Agent Council Engine                 │
│                                                         │
│  openSession(caseId, question)                          │
│       │                                                 │
│       ├──► insert session + consensus_protocol          │
│       │                                                 │
│  addAgent(sessionId, type, role)                        │
│       │                                                 │
│       ├──► assign agents with voting weights            │
│       │                                                 │
│  deliberate(sessionId, {maxRounds})                     │
│       │                                                 │
│       ├──► Round 1: each agent submits position         │
│       ├──► Round 2: agents revise after seeing others   │
│       ├──► Round 3: final positions + consensus check   │
│       │                                                 │
│       ├──► _computeAgreement() → weighted vote          │
│       ├──► Safety veto check                            │
│       └──► Store consensus_result                       │
│                                                         │
│  getConsensus(sessionId) → final decision + dissent     │
└───────────────────────────────────────────────────────┘
```

## 3. Tabelas (ni_council schema)

| Tabela | PK | Função |
|--------|-----|--------|
| `agents` | agent_id (VARCHAR) | Registro de agentes (tipo, peso de voto, veto) |
| `agent_roles` | role_id (UUID) | Atribuição de agente por sessão |
| `consensus_protocols` | protocol_id (UUID) | Configuração de quórum, threshold, timeout |
| `deliberation_log` | deliberation_id (UUID) | Log completo de cada posição por rodada |
| `consensus_results` | result_id (UUID) | Resultado final (reached/partial/no_consensus/vetoed) |
| `agent_performance` | performance_id (UUID) | Métricas de performance por agente |

## 4. Tipos de Agente

| Tipo | Especialidade | Veto | Padrão |
|------|--------------|------|--------|
| `assessment` | Avaliação clínica comprehensiva | ❌ | primary |
| `nanda` | Diagnóstico NANDA-I | ❌ | primary |
| `nic` | Intervenção NIC | ❌ | primary |
| `noc` | Resultado NOC | ❌ | primary |
| `safety` | Segurança do paciente | ✅ | veto_holder |
| `medication` | Farmácia / 9 Rights | ❌ | primary |
| `evidence` | Prática baseada em evidência | ❌ | secondary |
| `consensus` | Facilitador de consenso | ❌ | arbitrator |
| `specialist` | Especialista customizável | ❌ | secondary |

## 5. Protocolos de Consenso

| Protocolo | Threshold | Descrição |
|-----------|-----------|-----------|
| `majority` | >50% | Maioria simples dos votos |
| `weighted_majority` | ≥60% | Ponderado por voting_weight (padrão) |
| `unanimous` | 100% | Todos concordam |
| `threshold` | custom | Score mínimo configurável |
| `deliberative` | N/A | Decisão por arbitrator após deliberação |

## 6. Fluxo de Deliberação

```
Round 1:
  Cada agente submete sua posição inicial:
    - recommendation (diagnóstico/intervenção/outcome)
    - confidence (0-1)
    - argument (justificativa textual)
    - evidence_refs (UUIDs de evidência)
    - veto (boolean, apenas safety)

Round 2:
  Cada agente vê as posições dos demais e pode revisar:
    - Ajusta confidence baseado na média dos outros
    - Pode mudar recommendation
    - changed_from_prev = true se mudou

Round 3 (se necessário):
  Posições finais. Verifica consenso:
    - Agrupa votos por recommendation
    - Soma voting_weight por grupo
    - score = peso_vencedor / peso_total
    - Se score ≥ threshold → "reached"
    - Se score ≥ 0.4 → "partial"
    - Senão → "no_consensus"
    - Se qualquer veto_eligible → "vetoed"
```

## 7. Integração com o Pipeline

O conselho é executado no **Step 6** do orquestrador, após o planner gerar o plano de intervenção e antes da simulação. O conselho valida:

1. **Diagnóstico** está correto? (agente NANDA)
2. **Intervenção** é apropriada? (agente NIC)
3. **Safety check** — há contraindicações? (agente safety, veto power)
4. **Evidência** suporta a recomendação? (agente evidence)
5. **Medicação** — 9 Rights verificados? (agente medication)

Se o consenso for "vetoed" ou "no_consensus", o pipeline retorna ao planner para revisão.

## 8. Log de Deliberação (Audit Trail)

Cada posição submetida fica registrada em `deliberation_log` com:
- Agente, rodada, posição JSON, argumento textual
- References de evidência citadas
- Confidence level
- Se mudou de posição entre rodadas

Isso proporciona **explicabilidade completa**: para qualquer decisão clínica, pode-se rastrear exatamente qual agente recomendou o quê, com que confiança, e como chegou ao consenso final.

## 9. Roadmap

| Versão | Feature |
|--------|---------|
| v5.0 (atual) | 8 agentes, 5 protocolos, deliberação em rodadas, veto |
| v5.1 | Agentes com LLM próprio (Groq/GPT) em vez de heurística |
| v6.0 | Argumentação estruturada (Toulmin model) |
| v7.0 | Fine-tuning de agentes por especialidade clínica |
