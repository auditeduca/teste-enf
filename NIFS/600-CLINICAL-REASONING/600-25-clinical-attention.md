# NIFS-600-25 — Clinical Attention Engine

**Seção:** 600 (Clinical Reasoning)
**Camada cognitiva:** 5 — Clinical Attention
**Status:** ✅ Implementado (v5.0)
**Arquivo de código:** `reference-clinical-engine/attention/clinicalAttention.js`
**Schema DDL:** `ni_attention` (2 tabelas)

## 1. Propósito

Substitui a função heurística `vitalsToPrior()` do V8 por um mecanismo de atenção que pondera observações clínicas por múltiplos fatores: desvio de baseline, taxa de mudança, severidade NANDA associada, confiabilidade do sinal e contexto do paciente.

## 2. Modelo de Scoring

```
attentionScore = 
  deviation × 0.40    (quão anormal — z-score)
  + rateOfChange × 0.25  (quão rápido mudando)
  + severity × 0.25      (relevância clínica NANDA)
  + (1-reliability) × 0.10 (sinais ruidosos recebem mais atenção)
```

Score ∈ [0, 1]. Classificação:
- critical (>0.8), high (>0.6), moderate (>0.4), low (>0.2), normal (≤0.2)

## 3. Baselines por Faixa Etária

| Grupo | HR (bpm) | RR (rpm) | SBP (mmHg) | SpO₂ (%) |
|-------|----------|----------|------------|----------|
| Neonato | 130±20 | 40±8 | 70±10 | 98±1.5 |
| Pediátrico | 90±15 | 22±5 | 95±10 | 98±1.5 |
| Adulto | 72±10 | 16±3 | 120±10 | 98±1.5 |
| Idoso | 68±12 | 16±3 | 135±15 | 96±2 |

## 4. Peso de Severidade NANDA

Mapeia sinais vitais para diagnósticos NANDA ativos e pondera por severidade:
- impaired_gas_exchange → 0.95 (SpO₂, RR)
- decreased_cardiac_output → 0.92 (HR, SBP)
- fluid_volume_deficit → 0.85 (HR, SBP, urineOutput)

## 5. Integração com Particle Filter

Os attention scores são normalizados e passados como pesos para o particle filter, fazendo com que sinais de alta atenção tenham mais influência na inferência bayesiana.

## 6. Feedback Learning

O módulo suporta `updateWeights(feedbackData)`: se um sinal foi atendido mas não previu o desfecho → peso reduzido. Se foi ignorado mas previu → peso aumentado. Fecha o loop com a camada 8.
