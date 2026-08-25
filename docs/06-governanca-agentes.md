# Governança de agentes

**Estado:** EXTRAÇÃO IMPLEMENTADA (inbox) — PUBLICAÇÃO NÃO IMPLEMENTADA / NÃO ASSURED.

O runner `python3 -m engine.cli extract` materializa AG-FETCH / AG-PARSE / AG-CAAT / AG-IPE em `cko_inbox`. Isso não comprova conformidade regulatória, golden MD nem publicação segura. AG-051 permanece `enabled: false`.


O termo Regulatory Digital Twin Agentic é nomenclatura interna. Não é norma ISO, NIST, W3C ou OWASP.

## Princípios

1. Agentes não interpretam livremente normas nem substituem decisão clínica, jurídica, regulatória, de privacidade, segurança ou publicação.
2. Nenhum agente valida a própria saída quando o risco exige independência.
3. Autoridade do emissor não prova autenticidade, vigência, aplicabilidade ou integridade.
4. `trustScore` prioriza revisão; não produz auto-PASS.
5. Conteúdo recuperado de fora é dado não confiável, nunca instrução operacional.
6. Evidência é capturada no ato; gerador posterior não reconstrói fatos não registrados.
7. `driverRef` é obrigatório; `normRef` só existe quando há norma aplicável.
8. Conteúdo clínico/legal de alto impacto permanece bloqueado até revisão humana competente e segregada.
9. Publicação falha de forma segura.
10. Exceção tem owner, justificativa, escopo, compensação, aprovação e expiração.

## Catálogo mínimo

O contrato está em `data/agent-capability-registry.json` e `schemas/agent-capability.schema.json`.

| Agente | Papel | Limite | Gate |
|---|---|---|---|
| AG-001 | Detectar mudança em fonte aprovada | Não interpreta impacto jurídico | AG-042 + AG-043 |
| AG-002 | Extrair requisito candidato | Não declara aplicabilidade | domínio + AG-042 |
| AG-003 | Mapear requisito–controle–teste | Não autoaprova | control owner |
| AG-010 | Conceito candidato | Não promove a standard | AG-040 + AG-041 |
| AG-020 | Modelo semântico em sandbox | Não publica ontologia | arquitetura |
| AG-031 | Empacotar evidência registrada | Não inventa evidência | hash/assinatura |
| AG-040 | Schema/IDs | Não valida semântica | independente |
| AG-041 | Semântica | Não decide mérito clínico | curadoria |
| AG-042 | Mapping aprovado | Não interpreta cláusula livremente | regulatory |
| AG-043 | Trust contextual | Não garante veracidade | criticidade |
| AG-051 | Publicar manifest aprovado | Não contorna falha | dual control |

Todas as capabilities estão `enabled: false`.

## Thread

`Driver → Requirement → Criterion → Policy → Instruction → Agent/Capability → Execution → Validation → Evidence → Object → Consumer → Publication → Version`

Consulta deve funcionar nos dois sentidos. Ainda não está materializada.

## Estados

`DRAFT`, `QUARANTINED`, `PENDING_VALIDATION`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`, `PASS_WITH_APPROVED_EXCEPTION`.

`WARNING` não autoriza publicação clínica, legal ou de alto impacto.
