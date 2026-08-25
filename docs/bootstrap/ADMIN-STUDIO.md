# Admin Studio integrado

A área administrativa **não** é um CMS de verdade clínica. É uma superfície operacional sobre o GitHub Day Zero.

```text
GitHub JSON (banco Day Zero)
   cko_core · cko_md · cko_reg · cko_assurance · data/tools
        │
        ├── renderer → site público
        └── Studio Admin (módulos abaixo)
```

## Módulos

| Módulo | Rota | Prática |
|---|---|---|
| Painel | `/admin.html` | Mapa dos módulos e HOLD de release |
| Banco GitHub | `/admin/database.html` | Inventário dos JSON (tabelas do lote) |
| Catálogo | `/admin/catalog.html` | 5 pilotos OBSERVED + mapa Studio QUARANTINED |
| Pipeline | `/admin/pipeline.html` | Claim Studio vs status CKO |
| 44 camadas | `/admin/layers.html` | MD + REG por camada |
| Validações | `/admin/validations.html` | CAAT 44/44 e completude HOLD |
| Agentes | `/admin/agents.html` | Classes M0; runtime NÃO IMPLEMENTADO |
| Monitoramento | `/admin/monitoring.html` | KPIs Studio = UNKNOWN (sem IPE) |
| Backlog | `/admin/backlog.html` | Revisão humana SOURCE_DERIVED |
| Design System | `/admin/design-system.html` | Anexo vs runtime |
| Renderer | `/admin/renderer.html` | Botão `POST /__admin/render` |
| Deploy Git | `/admin/deploy.html` | Status + preparar changeset. **push FORBIDDEN** |

## Banco

Neste lote o banco **é** o GitHub. Relato de Postgres/Supabase 172 entities: `EVIDENCE_PENDING`. RLS não foi alterado.

## Renderer e deploy

Sirva com `python3 -m engine.cli serve --port 8081` (control plane só em loopback).

- Renderizar: gera `render/fetch` e `render/inline`.
- Preparar deploy: grava `cko_assurance/deploy_requests/*.json`.
- `git push` a partir do browser é proibido.

## Mapa Studio CMS

Arquivo: `admin/studio_cms_map.v1.json`.

Imagens da conversa: **NÃO ENCONTRADAS**. Tabelas reconstruídas do texto colado. BRADEN e demais IDs lógicos **não** foram promovidos a `data/tools`. Claims 98%/Ativo/Concluído = `DOCUMENT_CLAIM`.
