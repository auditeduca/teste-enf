# Arquitetura

```text
CKO MAIN GRAPH
   │
   ├── Regulatory Core
   ├── Knowledge Objects
   ├── Assertions / Claims
   ├── Libraries / Tools / Resources
   └── Exam Projections
          │
          ▼
CONTENT ENGINE
   │
   ├── Canonical Engine
   ├── Validators
   ├── Composer / Renderer
   ├── Resource Contracts
   ├── Site Shell Binding
   ├── Design System Binding
   ├── Past Exam Factory
   ├── Regulatory Monitor
   └── Audit 360
          │
          ▼
HTML ASSETS
   ├── inline preview
   └── fetch production
```

No v0.1 o caminho materializado é:

```text
data/tools/{slug}.json
   → engine.validate (Draft-07)
   → engine.score (sum | expression)
   → validators (completude, paridade, release)
   → render/fetch + render/inline
   → audit/*.json
```

## Separações importantes

- Fonte não é conteúdo derivado.
- Assertion não é claim.
- Claim não é recommendation.
- Norma não é projeção educacional.
- Santos/edital é uma projeção contextual; cidade/território é entidade distinta.
- Regulatory Core é compartilhado entre todas as projeções.
- HTML gerado não é a fonte da verdade.
