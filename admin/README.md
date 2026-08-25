# Admin

Contrato: `admin/contract.json`. Mapa Studio (quarentena): `admin/studio_cms_map.v1.json`.

Superfícies geradas em `render/fetch` e `render/inline`:

- `/admin.html` — painel
- `/admin/*.html` — banco, catálogo, pipeline, camadas, validações, agentes, monitoramento, backlog, design system, renderer, deploy
- JSON projetado em `/admin/*.json`

Control plane local (loopback): `GET /__admin/git-status`, `POST /__admin/render`, `POST /__admin/deploy-prepare`.

Não há autenticação, telemetria nem `git push` a partir do browser.
