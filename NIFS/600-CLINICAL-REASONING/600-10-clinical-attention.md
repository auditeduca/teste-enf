# NIFS-600-10: Clinical Attention

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-10                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o mecanismo de atenção clínica que prioriza observações — o filtro cognitivo que separa o que importa do que é ruído.

## 2. The Attention Problem

Um enfermeiro à beira do leito tem acesso a centenas de observações: sinais vitais, escores, exames, relatos, histórico, protocolos. Mas a atenção humana é limitada. O enfermeiro faz **atenção seletiva** — identifica as 6 observações críticas e ignora o resto.

O NIS modela este processo:

```
200 observações
    ↓
Clinical Attention Module
    ↓
6 observações críticas (attention_score > threshold)
194 observações filtradas (ignored, com motivo)
```

## 3. Attention Score Formula

Cada observação recebe um `attention_score` de 0.0 a 1.0:

```
attention_score = w_base × f_domain + w_salience × f_salience 
                + w_urgency × f_urgency + w_priority × f_priority 
                + w_context × f_context + w_learned × f_learned
```

| Component | Weight | Description |
|-----------|--------|-------------|
| `f_domain` | 0.20 | Peso por domínio clínico (cardio > pele em UTI) |
| `f_salience` | 0.25 | Quanto se desvia do baseline |
| `f_urgency` | 0.20 | Urgência temporal (1-5) |
| `f_priority` | 0.15 | Prioridade clínica (1-5) |
| `f_context` | 0.10 | Modificação pelo World Model |
| `f_learned` | 0.10 | Peso aprendido por feedback |

Pesos (`w_i`) são ajustáveis e vivem em `ni_attention.weights`.

## 4. Attention Components

### 4.1 Domain Weight (f_domain)

Diferentes domínios têm pesos diferentes dependendo do contexto:

```
Contexto: UTI adulto, paciente pós-operatório

Cardiovascular:  0.95  (always critical in ICU)
Respiratory:     0.90  (always critical in ICU)
Neurological:    0.85  (postop risk)
Renal:           0.70  (relevant)
Integumentary:   0.60  (Braden relevant but secondary)
Gastrointestinal: 0.40 (lower priority acutely)
Psychosocial:    0.20  (low acuity)
```

### 4.2 Salience (f_salience)

Quanto a observação se desvia do esperado:

```
Baseline PA sistólica: 120 mmHg (population: ICU adult)
Observed PA sistólica: 80 mmHg
Deviation: |120 - 80| / 120 = 0.33

f_salience = min(deviation × 2, 1.0) = min(0.66, 1.0) = 0.66
```

Observações dentro do esperado têm baixa saliência. Desvios grandes têm alta saliência.

### 4.3 Urgency (f_urgency)

| Level | Description | Score | Example |
|-------|-------------|-------|---------|
| 5 | Emergência imediata | 1.0 | SpO2 < 85%, PA < 70 |
| 4 | Urgente (minutos) | 0.8 | PA caindo rapidamente |
| 3 | Importante (horas) | 0.6 | Braden = 12 sem intervenção |
| 2 | Rotina (turno) | 0.4 | Eliminação urinária normal |
| 1 | Não urgente | 0.2 | Estado emocional estável |

### 4.4 Priority (f_priority)

| Level | Description | Score | Example |
|-------|-------------|-------|---------|
| 5 | Life-threatening | 1.0 | Glasgow < 8 |
| 4 | High clinical risk | 0.8 | NEWS2 ≥ 7 |
| 3 | Moderate risk | 0.6 | Braden 12-14 |
| 2 | Low risk | 0.4 | Braden 15-16 |
| 1 | Minimal risk | 0.2 | Braden 19-20 |

### 4.5 Context Modifier (f_context)

O World Model modifica a atenção:

```
Observation: Falta de bomba de infusão
Normal attention: 0.10 (irrelevante para a maioria dos casos)

Context: Paciente em vasopressor + UTI sem bomba disponível
f_context modifier: +0.60

Final attention: 0.10 + 0.60 = 0.70 (AGORA é crítico)
```

### 4.6 Learned Weight (f_learned)

Pesos ajustados por feedback clínico:

```
Situation: Enfermeiro rejeitou recomendação porque observação 
           "temperatura 37.2°C" tinha attention_score = 0.65
           mas era irrelevante para o diagnóstico

Feedback: reject, reason: "temperatura baixa não é prioridade aqui"

Learning: 
  - Reduzir f_salience weight para temperatura em UTI
  - f_learned(temperature, ICU) = 0.15 (era 0.35)

Próxima vez: attention_score(37.2°C, ICU) = 0.22 (era 0.65)
→ Filtrada como não-crítica ✓
```

## 5. Focus Windows

A atenção não é estática — muda ao longo do tempo. Focus Windows definem o que está em foco:

| Window Type | Trigger | Focused Domains | Duration |
|-------------|---------|-----------------|----------|
| `crisis` | Deterioração aguda | Cardio, respiratory, neuro | 30-60min |
| `monitoring` | Paciente estável crítico | All, equal weight | Contínuo |
| `routine` | Paciente estável | Domínios rotineiros | Por turno |
| `discharge_prep` | Preparo de alta | Mobilidade, educação, suporte | 24-48h |
| `medication_review` | Polifarmácia | Medicação, renal, hepático | Episódio |

## 6. Attention Traceability

Cada decisão de atenção é rastreável:

```json
{
  "signal_id": "uuid",
  "observation_ref": "ni_temporal.observations/uuid",
  "attention_score": 0.82,
  "components": {
    "domain": 0.95,
    "salience": 0.66,
    "urgency": 5,
    "priority": 4,
    "context": 0.0,
    "learned": 0.15
  },
  "ignored": false,
  "window_type": "crisis",
  "timestamp": "2026-07-05T10:30:00Z"
}
```

E observações filtradas:

```json
{
  "signal_id": "uuid",
  "observation_ref": "ni_temporal.observations/uuid",
  "attention_score": 0.18,
  "ignored": true,
  "ignore_reason": "below_threshold",
  "components": { ... },
  "timestamp": "2026-07-05T10:30:00Z"
}
```

## 7. Dynamic Threshold

O threshold de atenção não é fixo — adapta-se ao contexto:

| Context | Threshold | Rationale |
|---------|-----------|-----------|
| Crisis | 0.40 | Mais permissivo — captar mais sinais |
| ICU stable | 0.50 | Padrão |
| Ward | 0.60 | Mais seletivo — menos crítico |
| Routine | 0.70 | Altamente seletivo |

Se após filtragem restarem < 3 observações: reduzir threshold em 0.10 e repetir.

## 8. Interaction with Other Modules

```
World Model ──→ Attention (modifica f_context)
                    ↓
               Reasoning (recebe observações priorizadas)
                    ↓
               Memory (armazena attention_score no episódio)
                    ↓
               Learning (feedback ajusta f_learned)
                    ↓
               (loop: Attention usa pesos aprendidos)
```

## 9. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_attention.signals` | Score de cada observação em cada sessão |
| `ni_attention.weights` | Pesos aprendidos por contexto |
| `ni_attention.focus_windows` | Janelas de foco ativas |

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (Stage 1) |
| NIFS-600-04 | Hypothesis Generation (uses attention output) |
| NIFS-700-03 | Embeddings (for similarity-based salience) |
| NIFS-APP-G | Algorithms (attention computation) |

## 11. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full attention model | Leivis Melo |
