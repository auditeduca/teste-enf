# Contributing

1. Add or edit a tool in `data/tools/{slug}.json` against `data/schemas/tool.schema.json`.
2. Keep scoring changes in both `packages/nis_engine/score.py` and `apps/web/js/calc-engine.js`.
3. Add or update tests in `packages/tests/`.
4. Run `python3 -m pytest` and `python3 -m nis_engine.cli build`.
5. Open a PR against `main` with a short clinical + technical summary.

Branch names for Cloud Agents: `cursor/<topic>-cd31`.
