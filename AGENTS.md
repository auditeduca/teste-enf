# AGENTS.md

## Produto

Calculadoras de Enfermagem (público) / CKO (namespace interno).

Constituição operacional: `docs/constitution/CKO-INS-AI-PROJECT-001.md`.

Este repositório é autocontido. Documente e implemente apenas o que existe nesta árvore. GitHub é o store Day Zero.

## Espinha dorsal

CKO-MD (identidade) → CKO-REG (qualificação normativa) → camada de domínio. Nenhuma camada posterior é autoridade independente.

- 44 camadas registradas em `cko_core/layer_registry.json` (M0_REGISTERED).
- Candidatos de domínio do lote piloto: `data/tools/`.
- Admin e frontend leem os mesmos JSON. Contrato: `admin/contract.json`.

## Layout

- `docs/constitution/` — constituição e avaliação
- `cko_core/` `cko_md/` `cko_reg/` `cko_assurance/` — registries Day Zero
- `schemas/` — contratos Draft-07
- `data/tools/` — candidatos de domínio (não golden records MD)
- `engine/` — validate, bootstrap, score, generate, serve, audit
- `validators/` — completude clínica, paridade dual-render, release gate, layer CAAT
- `assets/` — CSS/JS first-party
- `render/fetch` e `render/inline` — HTML gerado (inclui `admin.html`)
- `docs/` — especificação desta aplicação

## Comandos

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
python3 -m engine.cli bootstrap
python3 -m engine.cli validate
python3 -m engine.cli build
python3 -m engine.cli audit
python3 -m engine.cli serve --port 8081
```

## Regras

- Não inventar UUID, hash, cláusula, URL oficial ou PASS sem população testada.
- SEM EVIDÊNCIA → UNKNOWN / EVIDENCE_PENDING / HOLD.
- DOCUMENTADO ≠ IMPLEMENTADO ≠ VALIDADO ≠ ASSURED ≠ PUBLICADO.
- Fórmula `expression` só pode conter dígitos e `+ - * / ( ) .`.
- SAE sem fonte canônica/licenciada permanece HOLD.
- Dimensionamento não emite número até a fórmula COFEN estar testada e aprovada.
- Admin não grava fórmula. Frontend não grava canônico.
- Sem CDN. Sem regeneração de conteúdo canônico por LLM.
- Português (pt-BR) é o idioma padrão da UI e da clínica.
- Conteúdo é apoio à decisão, não diagnóstico.

## Cursor Cloud

- Install: `python3 -m pip install -e ".[dev]"`
- Testes: `python3 -m pytest -q`
- Manual: `python3 -m engine.cli serve --port 8081`, abrir `/`, `/admin.html`, `/admin/database.html`, `/admin/renderer.html`, `/admin/deploy.html`, `/tools/gotejamento.html`
- Supabase MCP (read_only, `project_ref=yskgekcjzndptzmnjfke`): `.cursor/mcp.json` e `.mcp.json`. Skills: `npx skills add supabase/agent-skills` → `.agents/skills/supabase`. Não commitar chave publishable/secret. Schema SQL permanece EVIDENCE_PENDING até `list_tables` HTTP/MCP 200.
