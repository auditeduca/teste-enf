# AGENTS.md

## Product

NIS (Nursing Intelligence System) — clinical calculators for nursing, generated from canonical JSON.

Site: https://www.calculadorasdeenfermagem.com.br

## Layout

- `data/schemas/tool.schema.json` — Draft-07 schema for every calculator
- `data/tools/*.json` — source of truth (never hand-edit generated HTML as the source)
- `packages/nis_engine/` — validate, score (`sum` / `expression`), generate HTML
- `apps/web/` — static site (`css/`, `js/calc-engine.js`, generated `index.html` + `tools/`)
- `NIFS/`, `reference-website/`, `i18n-pipeline/` — **legacy reference only**; do not extend them

## Commands

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest
python3 -m nis_engine.cli validate
python3 -m nis_engine.cli build
python3 -m nis_engine.cli serve --port 8081
```

The Cloud Agent environment may already serve the legacy `reference-website` on port 8080. Use **8081** for this app.

## Rules

- New calculators go in `data/tools/`. After JSON changes, rebuild HTML and keep generated pages in git.
- Scoring logic lives in `packages/nis_engine/score.py` and is mirrored in `apps/web/js/calc-engine.js`. If you change one, change the other and add a test.
- Formula `expression` may only contain digits and `+ - * / ( ) .`.
- Clinical content is decision-support, not a diagnosis. Keep the disclaimer in generated pages.
- Portuguese (pt-BR) is the default UI and clinical language.

## Cursor Cloud specific instructions

- Install: `python3 -m pip install -e ".[dev]"`
- Automated tests: `python3 -m pytest -q`
- Manual check: `python3 -m nis_engine.cli serve --port 8081`, then open `/` and `/tools/apgar.html`
