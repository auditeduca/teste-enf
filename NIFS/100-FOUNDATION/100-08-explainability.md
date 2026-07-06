# NIFS-100-08: Explainability

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o princípio de explicabilidade como fundação — toda inferência do NIS deve ser explicável, rastreável e auditável.

## 2. The Explainability Mandate

> "Sem explicação, não há recomendação. Ponto."

Toda saída do NIS responde 8 perguntas:
1. Por quê este diagnóstico?
2. Quais evidências suportam?
3. Quais evidências contradizem?
4. Qual a probabilidade e incerteza?
5. Quais alternativas foram rejeitadas?
6. Qual o rastro passo a passo?
7. Quem votou no conselho?
8. Que casos similares existem?

## 3. Levels

| Level | Audience | Content |
|-------|----------|---------|
| summary | Enfermeiro à beira do leito | Card resumido |
| detailed | Enfermeiro revisor | Card + evidências + plano |
| full_trace | Auditor | Tudo + rastro + logs |
| machine | API/Sistema | JSON completo |

## 4. Implementation

- Template-based (estruturado, garantido)
- LLM-enhanced (linguagem natural, grounded nos dados)
- Trace armazenado permanentemente em `ni_explain.*` e `ni_reasoning.trace`
- Sempre acessível via API: `GET /api/v1/reasoning/sessions/{id}/trace`

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-19 | Explainability (full implementation) |
| NIFS-600-20 | Reasoning Trace (format) |
| NIFS-100-07 | Trustworthy AI |
