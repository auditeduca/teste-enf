# Tipos de conteúdo — campos e lineage

## FLA — Flashcards

- **entity_code:** `{CONCEPT}_FLA_001`
- **parent:** `{CONCEPT}_SCL_001` (obrigatório)
- **Campos agente:** `deck_structure`, `linked_entity_code`, `evidence_grade`
- **Mínimo:** 10 cards por deck

## SIM — Simulados

- **entity_code:** `{CONCEPT}_SIM_001`
- **Campos:** `exam_structure`, `linked_quizzes`
- **Mínimo:** 20 questões, duração e nota de corte

## MMP — Mapas mentais

- **entity_code:** `{CONCEPT}_MMP_001` *(extensão v2026.2.3)*
- **parent:** SCL
- **Mínimo:** 5 ramificações a partir do conceito central

## PRT — Protocolos

- **entity_code:** `{CONCEPT}_PRT_001`
- **Sem parent SCL** (checklist autônomo)
- **Grau A** obrigatório antes de `published`

## PKT — Guias de bolso

- **entity_code:** `{CONCEPT}_PKT_001` *(extensão v2026.2.3)*
- **Máximo:** 4 páginas, seções `indicacao`, `passos`, `alertas`, `referencias`

## FAQ

- **entity_code:** `{PAGE}_FAQ_001`
- **Mínimo:** 5 pares pergunta/resposta por página
