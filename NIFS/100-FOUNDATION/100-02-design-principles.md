# NIFS-100-02: Design Principles

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-02                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os princípios de design que guiam toda decisão técnica do NIS.

## 2. Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | Specification-First | A spec é a fonte da verdade; código é gerado |
| 2 | Knowledge-as-Graph | Conhecimento é relacional, não tabular |
| 3 | Probabilidade-Obrigatória | Toda recomendação tem P(x) |
| 4 | Explicabilidade-Não-Negociável | Sem explicação, sem recomendação |
| 5 | Humano-no-Controle | IA propõe, enfermeiro decide |
| 6 | Rastreabilidade-Total | Toda inferência é auditável |
| 7 | Incerteza-Explícita | Entropia e IC sempre presentes |
| 8 | Aprendizado-Validado | Nenhum peso muda sem aprovação humana |
| 9 | Segurança-Acima-de-Tudo | Safety veto sobrepõe qualquer recomendação |
| 10 | Composição-sobre-Herança | Módulos se compõem, não se herdam |
| 11 | Event-Driven | Eventos disparam raciocínio, não polling |
| 12 | Idempotent | Mesma entrada → mesma saída |
| 13 | Fail-Safe | Em erro, escalar para humano, nunca silenciar |
| 14 | Versionado | Todo conhecimento e código é versionado |
