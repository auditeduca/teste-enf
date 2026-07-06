# NIFS-300-22: Professionals

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-22                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir profissionais de enfermagem como agentes clínicos e como o NIS modela seu escopo, competências e decisões.

## 2. Professional Roles

| Role | Scope | NIS Mapping |
|------|-------|-------------|
| Enfermeiro | SAE, prescrição de cuidados, consulta | `ni_user.profiles` (Professional) |
| Técnico de enfermagem | Execução sob supervisão | `ni_user.profiles` (Technician) |
| Gestor de enfermagem | Indicadores, qualidade, compliance | `ni_user.profiles` (Manager) |
| Acadêmico | Pesquisa, ensino | `ni_user.profiles` (Academic) |
| Estudante | Aprendizado, simulados | `ni_user.profiles` (Student) |

## 3. Legal Scope (Lei 7498/86)

| Activity | Who Can Perform | Legal Basis |
|----------|----------------|-------------|
| Plano de cuidados (SAE) | Enfermeiro | Art. 11, Lei 7498/86 |
| Prescrição de cuidados | Enfermeiro | Art. 11 |
| Consulta de enfermagem | Enfermeiro | Art. 11 |
| Execução de cuidados | Técnico (sob supervisão) | Art. 12 |
| Notificação compulsória | Todo profissional | PC4/2017 Anexo V |

## 4. Council Agent ↔ Professional

Cada agente do Multi-Agent Council corresponde a um domínio profissional:

| Agent | Professional Domain |
|-------|-------------------|
| COUNCIL.ASSESS.001 | Assessment specialist |
| COUNCIL.NANDA.001 | Diagnosis specialist |
| COUNCIL.NIC.001 | Intervention specialist |
| COUNCIL.SAFETY.001 | Patient safety officer |
| COUNCIL.MED.001 | Medication safety |
| COUNCIL.EVID.001 | Evidence specialist |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-13 | Ethics (professional scope) |
| NIFS-600-18 | Consensus Engine (multi-agent) |
| NIFS-300-23 | Institutions (organizational context) |
