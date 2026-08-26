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

No v0.1.1 o caminho materializado é:

```text
cko_core/layer_registry.json     44 camadas M0 (MD profile + REG profile)
admin/contract.json              admin ↔ frontend
data/tools/{slug}.json           candidatos de domínio
   → engine.bootstrap
   → engine.validate (Draft-07)
   → engine.score (sum | expression)
   → validators (completude, paridade, release, layer CAAT)
   → render/fetch + render/inline  (inclui admin.html)
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
