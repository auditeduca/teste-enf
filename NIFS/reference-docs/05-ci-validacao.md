# 05 — CI e validação

## Pipeline unificado

```bash
python scripts/run_ci.py
```

Ordem de execução:

1. `validate_phases_1_7.py`
2. `validate_phases_8_12.py`
3. `generate_website_pt.py`
4. `audit_website_pt.py`
5. Validação de `build-report.json` + zip (build completo)

Relatório agregado: `datasets/metadata/ci_report.json`.

## Modos

| Comando | Uso |
|---------|-----|
| `run_ci.py` | Gate completo (build + 7 locales + zip) |
| `run_ci.py --pt-only` | Build rápido pt-BR; não exige zip |
| `run_ci.py --no-build` | Só validadores de dataset |

## Audit do site

```bash
python scripts/audit_website_pt.py
```

Verifica:

- Links internos quebrados (corpo + chrome/mega-menu)
- Cobertura de locales (contagem HTML, resolução de assets)
- Métricas resumidas para `ready_for_review`

Meta: **0 links quebrados**, pass rate 100%.

## Build report

Após `generate_website_pt.py`:

| Campo | Significado |
|-------|-------------|
| `file_counts.html` | Páginas HTML geradas |
| `jsonld_validation.passed` | Amostra JSON-LD parseável |
| `a11y_validation.passed` | Amostra com `lang` e meta description |
| `elapsed_s` | Tempo total do build |

O CI falha se `jsonld_validation.passed` for falso, se faltarem artefatos ou se o zip estiver ausente (build completo).

## Validadores isolados

Úteis durante edição de datasets:

```bash
python scripts/validate_phases_1_7.py
python scripts/validate_phases_8_12.py
python scripts/generate_website_pt.py --pt-only
python scripts/audit_website_pt.py
```

## Próximo documento

→ [06-i18n-seo.md](06-i18n-seo.md)
