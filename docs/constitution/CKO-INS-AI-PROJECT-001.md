# CKO-INS-AI-PROJECT-001 — Constituição operacional

**Identificador:** `CKO-INS-AI-PROJECT-001`  
**Versão:** 1.0.0  
**Estado:** `CONTROLLED_DRAFT`  
**Produto público:** Calculadoras de Enfermagem  
**Namespace interno:** CKO  

Este documento governa todo agente, modelo, worker, engine, validator, auditor, renderer, pipeline ou ferramenta automatizada neste repositório.

## 1. Identidade

CKO é plataforma governada de conhecimento, ferramentas clínicas, conteúdo, bibliotecas, evidências e automação para enfermagem.

Não é conjunto de HTML, CMS tradicional, calculadoras isoladas nem base de textos de IA.

Arquitetura orientada a: identidade canônica, master data, regulação, proveniência, evidência, conhecimento, conteúdo, objetos reutilizáveis, relações, automação, validação, assurance, projeções, monitoramento.

## 2. Espinha dorsal

```text
INPUT / NECESSIDADE / FONTE
        ↓
CKO-MD          (identidade)
        ↓
CKO-REG         (qualificação normativa)
        ↓
CAMADA ESPECIALIZADA
        ↓
KNOWLEDGE → CONTENT → ASSURANCE → RENDER / RELEASE → MONITORING
```

CONCEPT, CONTENT, TOOL, AGENT, ENGINE, RENDERER e STUDIO não antecedem MD. REG não cria identidade paralela.

Fonte-first ≠ REG-first:

```text
FONTE → descoberta → MD cria/resolve identidade → REG qualifica
```

Proibido: fonte → REG cria objeto → MD recebe cópia.

## 3. One concept → one identity

Um conceito, vários relacionamentos, várias projeções (idioma, página, template, público, PDF, SAE, mobile). Não criar registros independentes por canal.

## 4. Antialucinação

`SEM EVIDÊNCIA → UNKNOWN / EVIDENCE_PENDING`. Nunca `PASS` por ausência.

Estados: OBSERVED, VERIFIED, SOURCE_DERIVED, INFERRED, PROPOSED, IMPLEMENTED, ASSURED, UNKNOWN, EVIDENCE_PENDING, CONFLICT, HOLD, NOT_APPLICABLE, SUPERSEDED, DEPRECATED, REJECTED.

`DOCUMENTADO ≠ IMPLEMENTADO ≠ VALIDADO ≠ ASSURED ≠ PUBLICADO`.

PASS exige população, critério, teste executado, resultado reproduzível, evidência, hash/versão, validator. Sem isso: PASS_WITH_FINDINGS, EVIDENCE_PENDING, HOLD, UNKNOWN.

Mundo fechado em inventário/auditoria: não preencher lacuna por plausibilidade. Conhecimento externo só quando pedido, marcado como externo.

Hierarquia de evidência: live observado > bytes+hash > artefato versionado > snapshot oficial > doc controlada > decisão formal > relato > inferência.

Recuperação: RECOVER → COMPARE → GAP ONLY → REPERFORM → CLOSE. Reconstrução é último recurso.

## 5. Identidade e história

Não inventar IDs. Campos: canonical_id, UUIDv7, entity_type, business_key, identity_scheme, version, hash, provenance, status.

Política vigente: `cko_core/identity_policy.json`. Gerador UUIDv7 está HOLD. Identidade operacional = `business_key`. `uuid` permanece null.

Nunca UPDATE silencioso. Changeset → nova versão → validação → promotion. Preservar versão anterior, hash, fonte, razão, ator, timestamp, diff, impacto, rollback.

Duplicatas: QUARANTINED / MERGED / SUPERSEDED / DEPRECATED / REJECTED. Nunca apagar para limpar.

## 6. Epistemologia

SOURCE → INFORMATION → ASSERTION → CLAIM → EVIDENCE → KNOWLEDGE ATOM → KNOWLEDGE OBJECT → CONTENT OBJECT → PROJECTION.

Content Object é envelope de comunicação, não fonte clínica. Referencia md/reg/knowledge; não duplica a verdade.

Fórmulas, thresholds, doses, ranges, unidades, populações, interpretações não nascem em HTML/JS/template/renderer/CMS/LLM.

Fórmula governada: formula_id, versão, source_ref, expression, variáveis, unidades, população, precisão, arredondamento, test_vectors, hash. Rounding da fonte prevalece. Separar calculation/display/export precision.

## 7. CKO-REG

Recebe identidade MD. Qualifica authority, issuer, jurisdiction, instrument, provision, requirement, applicability, rights, temporalidade, snapshot, field binding, change, monitoring.

Aplicabilidade exige objeto, campo, jurisdição, população, condição, versão, requirement, provision, evidência. Senão: APPLICABILITY_UNVERIFIED.

Norma técnica sem texto licenciado: registrar metadados; cláusula = CLAUSE_TEXT_UNAVAILABLE.

Prioridade de fonte: oficial > API oficial > repositório oficial > publicação original > profissional oficial > científica primária > secundária > agregador.

Brasil (candidatos, não bindings): Planalto, Câmara, Senado, MS, ANVISA, COFEN, COREN, DOU — conforme tema.

## 8. 44 camadas

Todas nascem no Day Zero como objetos governados (`cko_core/layer_registry.json`). Maturidade inicial: **M0_REGISTERED**.

Cada camada L = L-MD + L-REG + L-DOMAIN.

EXISTS ≠ POPULATED ≠ IMPLEMENTED ≠ ASSURED.

HOLD upstream bloqueia downstream.

Agentes não são camadas. Plano transversal: OBJECT → MAKER → ENGINE → CHECKER → VALIDATOR → CAAT → IPE → AUDITOR → AUDIT 360 / AUD-8L → GATE.

MAKER ≠ CHECKER ≠ AUDITOR. Consenso de LLMs não é evidência. LLM não altera dose, fórmula, threshold, norma, identidade, classificação clínica, aplicabilidade material.

## 9. Assurance

CAAT: população completa quando viável. IPE: Complete, Accurate, Relevant, Reliable, Reproducible. Relatório interno não é evidência sem IPE.

ALCOA++ como profile + testes (não só política). Extensões CKO: Traceable, Versioned, Reproducible, Tamper-evident.

Auditoria 360 / AUD-8L: direta, inversa, vertical, horizontal, diagonal, transversal, complementar, circular.

## 10. Admin e frontend

Admin comunica-se com o frontend **pelo contrato** (`admin/contract.json`), não editando HTML canônico.

- Frontend: PRESENTATION_ONLY.
- Admin: preview, status, exceções, validação, controle de publicação.
- Day Zero: documentação e registries no GitHub. API admin autenticada: UNKNOWN neste repositório.
- Proibido: admin gravar fórmula; frontend gravar canônico.

Privacidade pública: NO_SENSITIVE_CAPTURE. User state referencia canonical_id; não altera verdade.

## 11. Integração, twin, SAE

APIs, adapters e tools são objetos MD. Resposta de API não vira verdade canônica sem snapshot, hash, MD candidate, REG, validação.

Digital Twin: identidade, estado, versão, relações, evidência, risco, agent runs, render, publicação, monitoramento. Não é diagrama.

SAE: busca interna canônica primeiro (MD, REG, grafo, evidência). Web externa só se política permitir. Sem dose/diagnóstico/threshold improvisados.

COSO e COBIT: frameworks de controle/governança de TI. Não autoridade clínica. Texto de cláusula: CLAUSE_TEXT_UNAVAILABLE até publicação licenciada.

ISO 8000: perfil CKO de unicidade, proveniência, WORM e lineage. Não é certificação. Referência operacional brasileira explícita: Programa de Governança de Dados (PGDADOS / SGD / MGI), https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/governancadedados/pgdados. PGDADOS não substitui texto de cláusula ISO licenciada.

W3C / WCAG: nomeados nas camadas L220/L280/L300. Equivalente brasileiro a nomear: eMAG e LBI. Texto de cláusula W3C não é baixado nem armazenado neste repositório até evidência licenciada. JSON-LD público: WebSite/Organization. Nunca MedicalOrganization como prestador de assistência.

## 12. Banco, RLS, produção

Schema: migration, não destrutivo por padrão, auditável. Sem DROP/TRUNCATE/mass DELETE automático.

RLS: não ligar/desligar mecanicamente. Classificação, roles, policies e testes primeiro.

“Produção assegurada” exige runtime/E2E, security, privacy, a11y, rights, integridade, validação clínica/regulatória, release gate, reperformance, monitoring. HTTP 200 não basta.

## 13. Comunicação obrigatória

Ao terminar análise material:

O QUE FOI OBSERVADO / VERIFICADO / IMPLEMENTADO / NÃO VERIFICADO / GAPS / BLOCKERS / FINDINGS / EVIDENCE PENDING / PRÓXIMO GATE.

“Completo” só com população. UNKNOWN > fabricado. HOLD > false PASS.

## 14. Regras finais

CKO-MD FIRST. CKO-REG SECOND.  
ONE CANONICAL IDENTITY.  
NO SILENT OVERWRITE / NORMALIZATION / DEDUPLICATION.  
NO PASS BY INFERENCE.  
NO CLAUSE / HASH / ID / SOURCE INVENTION.  
NO PRODUCTION CLAIM BY DOCUMENTATION.  
NO LLM AS CLINICAL AUTHORITY.  
NO UI AS SOURCE OF TRUTH.  
NO RENDERER CLINICAL LOGIC.  
NO RELEASE WITH MATERIAL UPSTREAM HOLD.  
RECOVER BEFORE REBUILD. FAIL CLOSED.
