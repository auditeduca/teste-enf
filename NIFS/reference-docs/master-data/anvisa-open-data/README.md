# ANVISA Open Data — Dados Abertos (dados.gov.br)

Programa `ANVISA_OPEN_DATA`: ingestão mensal dos CSVs oficiais da ANVISA via [Portal de Dados Abertos](https://dados.gov.br/dados/organizacoes/visualizar/agencia-nacional-de-vigilancia-sanitaria-anvisa) e mirror em [dados.anvisa.gov.br/dados/](https://dados.anvisa.gov.br/dados/).

## Fontes

| Portal | Papel |
|--------|-------|
| [dados.gov.br — ANVISA](https://dados.gov.br/dados/organizacoes/visualizar/agencia-nacional-de-vigilancia-sanitaria-anvisa) | Catálogo oficial gov.br (metadados) |
| [dados.anvisa.gov.br/dados/](https://dados.anvisa.gov.br/dados/) | Download direto CSV (86+ arquivos) |

## Datasets prioritários (enfermagem)

- `DADOS_ABERTOS_MEDICAMENTOS.csv` — registro ANVISA
- `TA_PRECOS_MEDICAMENTOS.csv` — preços CMED
- `TA_RESTRICAO_MEDICAMENTO.csv` — restrições hospitalares
- `FILA_ANALISE_MEDICAMENTO.csv` — fila regulatória
- `VigiMed_Medicamentos.csv` — farmacovigilância (amostra inicial)

## Pipeline

```
sync_catalog → discover → fetch → extract → structure → relate → validate → apply
```

## Comandos

```bash
# Sincronizar catálogo (lista CSVs em dados.anvisa.gov.br)
python scripts/anvisa_open_data_agents/run_batch.py --sync-catalog

# Atualização mensal completa (só fontes stale >30d)
python scripts/anvisa_open_data_agents/run_batch.py --monthly

# Forçar todos os datasets prioritários
python scripts/anvisa_open_data_agents/run_batch.py --monthly --all-sources --limit 5

# Validar
python scripts/anvisa_open_data_agents/run_batch.py --validate
```

## Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `datasets/regulatory/br/anvisa/datasets_catalog.json` | Catálogo de fontes |
| `datasets/regulatory/br/anvisa/medications_registry.json` | Medicamentos registrados |
| `datasets/regulatory/br/anvisa/medication_prices.json` | Preços CMED |
| `datasets/regulatory/br/anvisa/medication_restrictions.json` | Restrições |
| `datasets/regulatory/br/anvisa/drug_reference_links.json` | Vínculos DrugReference |

## API plataforma

- `GET /api/anvisa-open-data/status`
- `POST /api/anvisa-open-data/sync-catalog`
- `POST /api/anvisa-open-data/monthly`
- `POST /api/anvisa-open-data/validate`

UI: **ANVISA Dados Abertos** em `/anvisa-open-data`

## Atualização mensal (CI)

Workflow `.github/workflows/monthly-anvisa-sync.yml` — dia 1 de cada mês, 06:00 UTC.

Política em `datasets/master-data/anvisa-open-data/canonical.json`: `check_interval_days: 30`.

## Integração

- Vincula registros ANVISA a `drug_references.json` por número de registro ou nome
- Complementa `medication_dictionary_agents` (definições clínicas enriquecidas)
- Evidência Grau **A** (fonte governamental oficial)
