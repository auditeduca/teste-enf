# Apgar — pacote completo para edição externa

Gerado em: 2026-07-07 03:51 UTC
Branch de origem: cursor/cko-profiles-pdf-c848

## Visualizar localmente

```bash
cd apgar-export
python3 -m http.server 8765
```

Abra no navegador:
- http://localhost:8765/preview_apgar.html  (entrada principal de desenvolvimento)
- http://localhost:8765/apgar.html
- http://localhost:8765/html/apgar.html     (caminho alternativo com base `../`)

## Estrutura

| Pasta/arquivo | Conteúdo |
|---------------|----------|
| `preview_apgar.html`, `apgar.html` | Página completa com perfis CKO, motor clínico e PDF |
| `html/apgar.html` | Cópia para rota `/html/` (symlinks resolvidos em `css/`, `js/`, `partials/`) |
| `css/` | `site-styles.css`, `print-template.css` |
| `js/` | Motor de cálculo, CKO, Nurse-PaLM, partials-loader |
| `js/modules/data/` | `apgar-cko.json`, `apgar-edges.json`, `apgar-medications.json` |
| `partials/` | Header, footer, acessibilidade, cookies |
| `scripts/` | Scripts Python de build e patch |
| `reference-datasets/` | Fontes para `build_apgar_cko.py` |
| `i18n/` | Dicionários básicos (pt-BR, en, es) |

## Perfis (ordem das abas)

Padrão → Urgência → Gestor → Estudante → Acadêmico

Conteúdo alimentado por `js/modules/data/apgar-cko.json` via `tool-cko-loader.js` e `tool-profile-engine.js`.

## Motor clínico

Após calcular, o fluxo único `#calcClinicalFlow` exibe:
NANDA·NIC·NOC → Nurse-PaLM → Plano/Monitoramento/Segurança/Medicamentos → Evidência & Pérolas → Recursos.

## Sincronizar CKO a partir dos datasets

```bash
python3 scripts/build_apgar_cko.py
```

## PDF / Relatório fiel

Template reutilizável: `partials/relatorio-fiel.html` + `css/print-template.css`

- Pré-visualização editável: `relatorio_fiel.html`
- Preenchimento automático via `calc-engine-v2.js` → `populatePrintReport()` (lê IDs da página)
- Botão **Imprimir** gera PDF via `window.print()` (2 páginas: clínico + segurança/referência)
- `js/report-payload.js` — monta JSON do relatório a partir do DOM

Para integrar em outra ferramenta: use `<div id="printTemplateMount"></div>` e carregue via `partials-loader.js`.

## API de relatórios (opcional)

Pasta `api/` — gera o mesmo HTML via POST JSON (FastAPI):

```bash
pip install -r api/requirements.txt
uvicorn report_server:app --app-dir api --reload --port 8000
```

- `POST /generate-report` — corpo JSON conforme `api/report_schema.json`
- `GET /docs` — Swagger
- `ReportPayload.build()` no browser monta o mesmo payload

## Notas

- Fontes e Font Awesome carregam de CDN (requer internet).
- Imagens do header (`images/logotipo_website.webp`) podem não estar incluídas; adicione em `images/` se necessário.
- `#tool-config` embutido no HTML contém a definição da calculadora; o CKO complementa com conteúdo por perfil.
