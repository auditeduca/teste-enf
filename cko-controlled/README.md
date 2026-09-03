# CKO / CALENF — Site CALENF + cascata de assurance

## Frontend (runtime)

O Hosting serve a **estrutura CALENF** (`reference-website`, NIFS-900-03):

- `data/tools/*.json` + `data/schemas/tool.schema.json` → páginas de calculadora
- `js/calc-engine.js` / `js/calc-engine-v2.js` → runtime das ferramentas
- `js/nurse-palm.js` → Nurse-PaLM V9 (operacional **NOT_ASSERTED**)
- `js/knowledge-graph.js` → grafo clínico
- Digital twin **NIFS-600-15** projetado em cada ferramenta (B5 HOLD: not observed / not deployed)

As 12 páginas institucionais Wave2 são sobrepostas nessa árvore. A cascata CKO é o contrato no CI/engine — não é UI.

## Cascata (CI / engine — não é UI)

```
policy-as-code
        ↓
schemas
        ↓
graph constraints
        ↓
CI gates
        ↓
runtime assertions
        ↓
automatic evidence
```

Tudo inicia em policy-as-code. Ferramentas e bibliotecas só passam se forem instâncias do schema CALENF, nós do grafo, projeções do digital twin e bindings Nurse-PaLM.

B9 permanece HOLD / NOT_RELEASED.

## Comandos

```bash
cd cko-controlled
python3 scripts/generate_universe.py
python3 scripts/sync_tool_runtime.py
node --test tests/suite.test.js
node cli.mjs
python3 -m http.server 4173 --directory ../reference-website
```

`sync_tool_runtime.py` **não copia** o CALENF para `cko-controlled/public`. Ele converge o overlay Wave2 **para** `reference-website` e gera `data/cko/governance.json`.

## Deploy

Firebase Hosting lê `firebase.json` (`public: reference-website`). Locales extra não entram no Hosting.

Este deploy é superfície técnica controlada. **Não** promove B9 nem afirma runtime operacional do Nurse-PaLM.
