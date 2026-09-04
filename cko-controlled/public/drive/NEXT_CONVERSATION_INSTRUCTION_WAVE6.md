# Instrução para iniciar a próxima conversa — CKO Wave 6

Continue o projeto **Calculadoras de Enfermagem / CKO** a partir do checkpoint **Wave 5**.

## Não reabrir a arquitetura

As camadas **01–18 já estão documentadas**.  
Waves normativas 1–3 já extraíram requisitos.  
Wave 4 já implementou e executou profiles normativos selecionados.  
Wave 5 já implementou e executou o Executable Control Plane.

Não redesenhar essas camadas sem finding objetivo.

## Estado executado

Wave 4:
- 20 testes;
- 20 PASS;
- 0 FAIL.

Wave 5:
- 27 testes;
- 27 PASS;
- 0 FAIL;
- Universal Freeze Gate = `DENY`.

`DENY` é esperado porque há blockers arquiteturais e falta assurance universal.

## Blockers obrigatórios

- `ACR-001`: conflito de responsabilidade da Series 03.
- `ACR-002`: vocabulário lateral canônico LL-01…LL-30 vs bindings laterais ad hoc.
- `ACR-003`: Series posteriores sem responsibility contracts canônicos completos.

Não resolver por inferência silenciosa.

## Próximo trabalho — Wave 6

Nome:

**Wave 6 — Cross-Fabric Reperformance & Universal Evidence Bundle**

Executar nesta ordem:

### 1. ACR-001
Construir decision package para Series 03:
- opções concortentes;
- dependências;
- impacto downstream;
- authority;
- decisão controlada;
- migration impact;
- tests necessários.

Não escolher uma opção sem explicitar a decisão.

### 2. ACR-002
Normalizar lateral ontology:
- LL-01…LL-30 é o vocabulary canônico atual;
- mapear cada binding ad hoc para LL existente, specialization ou gap;
- nenhum novo LL-ID sem decisão.

### 3. ACR-003
Materializar responsibility contracts das Series posteriores:
- purpose;
- owns;
- doesNotOwn;
- inputs;
- outputs;
- upstream;
- downstream;
- authority;
- validators;
- closure criteria.

### 4. Universal matrices
Gerar:
- Series Responsibility Matrix;
- Series × Fabric Coverage;
- Series × Lateral Coverage;
- Cross-Fabric Binding Matrix;
- Dependency Matrix;
- Authority Matrix;
- Capability-Permission-Authority Matrix;
- Field Ownership Matrix;
- Validator Coverage Matrix;
- Test Coverage Matrix.

### 5. Reperformance
Reexecutar:
- Wave 4 tests;
- Wave 5 tests;
- reference integrity;
- hashes;
- manifests.

Resultado deve ser calculado pela execução, nunca escrito manualmente.

### 6. Cross-Fabric E2E
Executar cenários:
- canonical object;
- regulatory source;
- clinical calculator;
- library object;
- AI agent;
- generated image;
- publication;
- rights block;
- safety block;
- privacy block;
- authority block;
- source supersession;
- rollback/restore.

### 7. Universal Evidence Bundle
Montar:
- registries;
- matrices;
- test reports;
- gaps;
- conflicts;
- decisions;
- manifests;
- hashes;
- coverage universes;
- evidence.

### 8. Universal Closure Gate
Somente rodar quando os blockers definidos pelo closure contract estiverem tratados.

## Regras inegociáveis

- `CAPABILITY != PERMISSION != AUTHORITY`
- `AGENT != MODEL`
- `MODEL OUTPUT != FACT`
- `VALIDATOR != AUTHORITY`
- `RENDERER != CANONICAL SOURCE`
- `PUBLICLY AVAILABLE != PUBLIC DOMAIN`
- `RECOMMENDATION != DECISION`
- `NOT_RUNNABLE != PASS`
- `WAIVED != PASS`
- `COVERAGE != READINESS`
- `READINESS != CONFORMANCE`
- `CONFORMANCE != ASSURANCE`
- `CLOSED != FROZEN`
- provenance deve ser capturada, não reconstruída;
- hashes/counts/coverage/PASS/FAIL são derivados pela execução;
- external standard identity verification não equivale a full-text verification;
- nenhum freeze enquanto blockers/evidence/approval exigidos estiverem ausentes.

## Backup / referências

Usar o checkpoint Drive e os ZIPs Waves 1–5 como fonte de continuidade.

Antes de modificar prodrção, operar closure-first e pilot-first.

**A primeira ação na próxima conversa deve ser: preparar e resolver de forma controlada o ACR-001.**
