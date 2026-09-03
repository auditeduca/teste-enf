# CKO / CALENF — Relatório Técnico Final Controlado (Site)

Implanta o texto de `CKO_Relatorio_Tecnico_Final_Controlado_v1.0.0` como **Firebase Hosting Site** técnico, fail-closed.

- Baseline: `OV-CKO-GLOBAL-FINAL-AUD8L-1.0.0` · `FINAL_CONTROLLED`
- Release: **HOLD / NOT_RELEASED**
- Nurse-PaLM operacional: **NOT_ASSERTED**
- `robots: noindex`

## Cascata (raiz)

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

Tudo inicia em `policy-as-code`. Estágio seguinte só entra como PASS se o predecessor passou. Sem evidência automática se a cadeia quebrou.

```
coverage = 100% do universo conhecido
evidence coverage = 100%
test pass = 100% dos testes definidos
residual uncertainty = X
unknown universe = explicitado
```

Stack: policy-as-code → schemas → graph constraints → CI gates → runtime assertions → automatic evidence.

## Comandos

```bash
cd cko-controlled
python3 scripts/generate_universe.py
node --test tests/suite.test.js
node cli.mjs
python3 -m http.server 4173 --directory public
```

## Deploy

Firebase Hosting lê `firebase.json` na raiz (`public: cko-controlled/public`).

O ambiente deste agente **não está autenticado no Firebase**. Após `npx -y firebase-tools@latest login` e `use <PROJECT_ID>`:

```bash
npx -y firebase-tools@latest deploy --only hosting
```

Este deploy é superfície técnica controlada. **Não** promove B9 nem afirma runtime operacional.
