# Admin ↔ Frontend

Contrato: `admin/contract.json`.

O admin **não** é CMS de verdade clínica. Ele lê os mesmos registries que o renderer projeta.

```text
GitHub (Day Zero store)
   ├── cko_core / cko_md / cko_reg / cko_assurance
   └── data/tools  (candidatos de domínio)
            │
            ├──────────► Renderer (PRESENTATION_ONLY) ──► site público
            │
            └──────────► Admin surface (read-only neste lote)
                         preview · status · HOLD · findings
```

Comunicação direta, neste v0.1.1:

- Shell compartilhado (header CKO, Design System local).
- Página `/admin.html` gerada a partir de `cko_core/layer_registry.json`.
- Inspector `/inspector.html` gerada a partir de `data/tools`.
- Sem POST, sem login, sem escrita canônica.

Escrita futura (PROPOSED): apenas changeset/nova versão. Proibido UPDATE silencioso de fórmula.
