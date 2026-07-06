# NIFS-200-13: Ethics

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-13                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os princípios éticos que governam o NIS como sistema de IA clínica.

## 2. Ethical Principles (Beauchamp & Childress)

| Principle | NIS Implementation |
|-----------|-------------------|
| **Autonomy** | Human override always; IA propõe, enfermeiro decide |
| **Beneficence** | EBP, evidence-based, continuous learning |
| **Non-maleficence** | Safety layer, veto, adverse event tracking |
| **Justice** | Equity across populations, bias mitigation |

## 3. AI-Specific Ethics

| Concern | NIS Response |
|---------|-------------|
| Algorithmic bias | Population-specific priors, bias tests |
| Transparency | Full explanation trace, 4 levels |
| Accountability | Every decision has session_id + created_by |
| Privacy | Patient hash, LGPD/HIPAA, consent |
| Human agency | Human-in-the-loop, override mandatory |
| Beneficial AI | Designed to augment, not replace nurses |

## 4. Ethical Decision Points

| Scenario | NIS Action |
|----------|-----------|
| Restraint recommendation | Flag for ethical review, never auto-recommend |
| End-of-life care | Escalate to human + palliative care agent |
| Refusal of treatment | Respect, document, do not override |
| Conflict of interest | Log, escalate to clinical governance |
| Resource scarcity | World Model context, but human decides triage |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-04 | Human-Centered AI |
| NIFS-100-07 | Trustworthy AI |
| NIFS-1000-07 | Consent |
| NIFS-1000-09 | LGPD |
