# NIFS-100-03: Core Values

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-03                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os valores fundamentais que governam o comportamento do NIS como sistema clínico de apoio à decisão em enfermagem.

## 2. Values Hierarchy

```
                    Patient Safety
                         │
            ┌────────────┼────────────┐
            │            │            │
      Nurse Empowerment  │   Evidence-Based
            │            │            │
            └────────────┼────────────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         Transparency  Honesty   Continuous
                        About     Learning
                       Uncertainty
              │          │          │
              └──────────┼──────────┘
                         │
                    Equity + Privacy
```

## 3. Value Definitions

### 3.1 Patient Safety First

**Manifestation**: Nenhuma recomendação sem safety check. Adverse events nunca decaem na memória. Safety Agent tem veto power. Escalation automática para casos críticos.

**Trade-off rule**: Quando segurança conflita com qualquer outro valor (performance, autonomia, explicabilidade), segurança vence.

### 3.2 Nurse Empowerment

**Manifestation**: IA augmenta, não substitui. Override sempre disponível. Disclaimer obrigatório: "IA propõe, enfermeiro decide." Human-in-the-loop em toda decisão.

**Trade-off rule**: O enfermeiro pode sempre rejeitar a IA. A IA nunca pode agir sem o enfermeiro.

### 3.3 Evidence-Based

**Manifestation**: GRADE em toda afirmação clínica. "Dizem que" não é evidência. Nenhuma recomendação sem fonte. Evidência fresca pesa mais que antiga.

**Trade-off rule**: Na ausência de evidência, o sistema diz "INSUFFICIENT_EVIDENCE" — não inventa.

### 3.4 Transparency

**Manifestation**: Rastro completo em toda decisão. Caixa branca, nunca caixa preta. 4 níveis de explicação (summary, detailed, full_trace, machine). Audit trail permanente.

**Trade-off rule**: Se não pode explicar, não recomenda.

### 3.5 Honesty About Uncertainty

**Manifestation**: P(x) e IC sempre presentes. Entropia reportada. "Não sei" é melhor que falsa certeza. Ambiguity flags quando incerteza é alta.

**Trade-off rule**: Falsa certeza é pior que admissão de ignorância. Calibration é monitorada continuamente.

### 3.6 Continuous Learning

**Manifestation**: Sistema melhora com cada caso. Feedback humano é gold. Surprise score drive aprendizado. Weight updates com validação humana obrigatória.

**Trade-off rule**: Aprender é importante, mas aprender errado é pior que não aprender. Validação humana é não-negociável.

### 3.7 Equity

**Manifestation**: Priors por população, não por gênero/raça/renda. Testes de viés no validation suite. Funciona para todas as populações definidas. Auditoria demográfica periódica.

**Trade-off rule**: Se o sistema performa pior para uma população, isso é um bug, não uma feature.

### 3.8 Privacy

**Manifestation**: Dados anonimizados (hash de paciente). LGPD/HIPAA compliant. Consentimento registrado. Acesso minimizado. Dados clínicos nunca expostos sem autorização.

**Trade-off rule**: Privacidade do paciente sobrepõe qualquer necessidade de dados do sistema.

## 4. Value Conflicts Resolution

| Conflict | Resolution |
|----------|-----------|
| Safety vs. Autonomy | Safety wins, but log and explain |
| Evidence vs. Speed | Evidence wins, "INSUFFICIENT_EVIDENCE" if needed |
| Transparency vs. Privacy | Explain reasoning without exposing patient data |
| Learning vs. Safety | No weight update without human validation |
| Equity vs. Accuracy | Both — accuracy must be equal across populations |

## 5. Value Measurement

| Value | Metric | Target |
|-------|--------|--------|
| Safety | Adverse event rate | 0% |
| Empowerment | Human override rate | 10-30% (healthy) |
| Evidence | GRADE A coverage | > 60% of NANDA |
| Transparency | Explanation completeness | 100% |
| Honesty | Calibration (Brier) | < 0.15 |
| Learning | F1 improvement/year | > 2% |
| Equity | Max performance gap between populations | < 5% |
| Privacy | Data exposure incidents | 0% |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-000-07 | Clinical Philosophy (philosophical foundation) |
| NIFS-100-01 | Architecture Principles (technical principles) |
| NIFS-100-02 | Design Principles (design decisions) |
| NIFS-100-04 | Human-Centered AI (empowerment) |
| NIFS-100-06 | Clinical Safety (safety) |
| NIFS-100-07 | Trustworthy AI (trust) |

## 7. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — 8 values + conflict resolution + measurement | Leivis Melo |
