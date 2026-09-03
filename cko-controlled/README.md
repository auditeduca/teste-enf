# CKO / CALENF — Site em runtime + cascata de assurance

## Frontend (runtime)

O Hosting serve **somente a plataforma** do Drive (cluster institucional Wave2):

`/` `missao.html` `objetivo.html` `ecossistema.html` `acessibilidade.html` `tecnologiaverde.html` `privacidade.html` `politica-editorial.html` `notificacoes-legais.html` `fale.html` `forum-enfermagem.html` `mapa-do-site.html`

A cascata é o contrato do projeto no CI/engine — não é UI. Tudo inicia em policy-as-code. Estágio seguinte só entra se o predecessor PASS. Voltar o dashboard do relatório no frontend falha em policy-as-code e não emite evidência.

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
