# Notificação Compulsória — Legislação BR (nacional + estadual)

Programa `COMPULSORY_NOTIFICATIONS`: base de dados de agravos de notificação compulsória vinculados à legislação pai, com agentes de raspagem, estruturação e validação.

## Hierarquia de IDs (doc 14)

```
Country (BR)
  └── Jurisdiction (JUR.BR, JUR.BR.SP, …)
        └── LegislationInstrument (LEG.BR.MS.PC4.2017, LEG.BR.SP.VIG.2024, …)
              └── CompulsoryNotificationEntry ({CONCEPT}_NC_{NNN})
```

Campos obrigatórios de vínculo: `entity_code`, `concept_code`, `parent_entity_code`, `parent_entity_type`, `jurisdiction_code`.

## Datasets

| Arquivo | Entidade |
|---------|----------|
| `datasets/regulatory/br/jurisdictions.json` | Jurisdiction (28: BR + 27 UFs) |
| `datasets/regulatory/br/legislation_instruments.json` | LegislationInstrument |
| `datasets/regulatory/br/compulsory_notifications.json` | CompulsoryNotificationEntry |
| `datasets/master-data/compulsory-notifications/scrape_sources.json` | Fontes HTTP |
| `datasets/master-data/compulsory-notifications/scrape_cache/` | Cache de raspagem |

## Legislação base (nacional)

- **Portaria Consolidação GM/MS nº 4/2017** — lista nacional (Anexo V)
- **Portaria MS 204/2016** — histórica (consolidada)
- **3148/2024** — HTLV
- **5201/2024** — atualização lista + vigilância sentinela
- **6734/2025** — esporotricose humana
- **10175/2026** — anomalias congênitas
- **2010/2023** — redação esferas MS/SES/SMS

## Estados (amostra inicial)

SP (CVE-SP), BA (SESAB), RJ (SESA), MG (SES-MG), PR, RS — complementam a lista nacional.

## Agentes

Pipeline: **search → scrape → structure → validate → apply**

```bash
# Raspagem BVS/DOU/SES (cache local)
python scripts/compulsory_notification_agents/run_batch.py --scrape

# Fila editorial (agravos detectados ainda não estruturados)
python scripts/compulsory_notification_agents/run_batch.py --scrape --catalog

# Estruturar lote (determinístico)
python scripts/compulsory_notification_agents/run_batch.py --scrape --limit 10

# Com DeepSeek
python scripts/compulsory_notification_agents/run_batch.py --scrape --limit 5 --llm

# Validar base inteira
python scripts/compulsory_notification_agents/run_batch.py --validate
```

## API / Plataforma

- `GET /api/compulsory-notifications/status`
- `POST /api/compulsory-notifications/scrape`
- `POST /api/compulsory-notifications/catalog/rebuild`
- `POST /api/compulsory-notifications/run`
- `POST /api/compulsory-notifications/validate`
- UI: `/compulsory-notifications`

## Enfermagem

Cada registro inclui `nursing_guidance_pt` (fluxo SINAN, periodicidade imediata/semanal, esferas MS/SES/SMS) para uso na ferramenta `/ferramentas/notificacao-compulsoria`.
