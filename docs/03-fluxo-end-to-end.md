# Fluxo end-to-end

```text
ESCOPO/EDITAL
→ INTERNAL RESOLUTION
→ SOURCE / SNAPSHOT
→ IDENTITY + HASH
→ FRAGMENT
→ ASSERTION
→ CLAIM
→ CANONICAL OBJECT
→ RELATIONS
→ VALIDATORS
→ CAAT / IPE / ALCOA++
→ CONTENT ARTIFACT
→ RENDERER
→ SITE SHELL + DESIGN SYSTEM
→ HTML
→ AUDIT 360
→ RELEASE MANIFEST
```

No v0.1 o recorte implementado começa em **CANONICAL OBJECT** (JSON em `data/tools`), passa por validators estruturais e de completude, renderer dual, auditoria gerada e release manifest em **HOLD**.

## Reverse lineage

Todo asset publicado deve poder apontar de volta:

```text
HTML / QUESTION / TOOL
→ CONTENT BLOCK
→ CLAIM
→ ASSERTION
→ SOURCE FRAGMENT
→ SOURCE / REGULATORY INSTRUMENT
```

Hoje o HTML carrega o JSON do objeto (`#tool-config` nas páginas calculáveis) e o audit trail grava `slug`, versão e SHA-256 do arquivo-fonte. Fragmentos, assertions e instrumentos regulatórios ainda não estão materializados como registros consultáveis nos dois sentidos.
