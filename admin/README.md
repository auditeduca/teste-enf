# Admin

Contrato: `admin/contract.json`.

Superfícies geradas:

- `render/fetch/admin.html` e `render/inline/admin.html` — Layer Registry + contrato
- `render/fetch/inspector.html` e `render/inline/inspector.html` — candidatos piloto
- `render/*/admin/contract.json` e `layer_registry.json` — JSON projetado para o frontend

Admin e frontend comunicam-se pelos mesmos arquivos GitHub. Não há autenticação, POST, CMS de escrita nem telemetria neste lote.
