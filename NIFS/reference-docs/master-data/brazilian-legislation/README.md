# Legislação Brasileira — BRAZILIAN_LEGISLATION

Base consolidada e atualizável: Constituição, Lei Orgânica do SUS (8080/8142), legislação profissional (7498, COFEN) e vínculos com ferramentas (notificação compulsória, SAE, etc.).

## Hierarquia de IDs (doc 14)

```
Country (BR)
  └── Jurisdiction (JUR.BR)
        └── LegislationDomain (LEX_DOM.BR.*)
              └── LegislationInstrument (LEG.BR.*)
                    ├── LegislationCorpus (CORP.*.001) — resumo condensado
                    ├── LegalProvision ({CONCEPT}_PROV_{NNN}) — artigos/dispositivos
                    └── LegislationToolLink (TLK.*) → ferramenta plataforma
```

## Datasets

| Arquivo | Entidade |
|---------|----------|
| `legislation_domains.json` | 4 domínios (CF, SUS, profissional, vigilância) |
| `legislation_instruments.json` | Instrumentos (+ CF, 8080, 8142, 7498, …) |
| `legislation_corpus.json` | Corpus condensado por lei |
| `legal_provisions.json` | Dispositivos com `parent_entity_code` = LEG.* |
| `legislation_tool_links.json` | TLK.* → TOOL.* |

## Pipeline (7 etapas)

1. **discover** — fontes desatualizadas vs cache  
2. **fetch** — Planalto, BVS, LexML  
3. **extract** — artigos do HTML  
4. **structure** — normaliza corpus + provisions  
5. **relate** — links ferramenta ↔ dispositivo  
6. **validate** — vínculos pai  
7. **apply** — persiste datasets  

```bash
python scripts/brazilian_legislation_agents/run_batch.py --discover
python scripts/brazilian_legislation_agents/run_batch.py --fetch --all-sources
python scripts/brazilian_legislation_agents/run_batch.py --refresh --limit 8
python scripts/brazilian_legislation_agents/run_batch.py --validate
```

## API / UI

- `GET /api/brazilian-legislation/status`
- `POST /api/brazilian-legislation/discover`
- `POST /api/brazilian-legislation/fetch`
- `POST /api/brazilian-legislation/refresh`
- `POST /api/brazilian-legislation/validate`
- UI: `/brazilian-legislation`

## Integração

- **Notificação compulsória:** `LEX_DOM.BR.VIGILANCE` + `TLK.NOTIF_COMP.*` → `COMPULSORY_NOTIFICATIONS`
- **Atualização:** policy `refresh_policy` em `canonical.json` (ETag/Last-Modified/content_hash)
