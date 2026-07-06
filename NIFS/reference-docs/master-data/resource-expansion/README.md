# Resource Expansion — Geradores, Biblioteca, Slides, Games

Programa `RESOURCE_EXPANSION`: currículos, escalas, indicadores, dicionário, assets da biblioteca, slides por ferramenta e roadmap de games.

## Módulos (M19–M25)

| ID | Recurso | Rotas | Status |
|----|---------|-------|--------|
| M19 | Gerador de currículos | `/curriculo`, `/curriculo/criar` | UI existe (40%) |
| M20 | Gerador de escalas | `/escalas`, `/ferramentas/{slug}` | Piloto APGAR 100% |
| M21 | Gerador de indicadores | `/gestao/indicadores` | 100 indicadores NDNQI/COFEN/JCI |
| M22 | Dicionário (enfermagem + medicamentos) | `/glossario`, `/glossario/medicamentos` | 5000 termos enfermagem; 500 DrugReference |
| M23 | Assets biblioteca | `/biblioteca` | Sync calculadorasdeenfermagem.com.br |
| M24 | Slides técnicos | `/ferramentas/{slug}/slides` | JSON por ferramenta |
| M25 | Games | `/games` | Roadmap 3 fases |

## Comandos

```bash
# Registries + manifest biblioteca + slides registry + games roadmap + indicadores M21
python scripts/resource_expansion/build_registry.py

# Gerador M21 — 100 indicadores de enfermagem
python scripts/resource_expansion/build_nursing_indicators.py

# Baixar ícones/heroes do site oficial → website/assets/
python scripts/resource_expansion/sync_library_assets.py --limit 30

# Gerar JSON de slides (100 ferramentas)
python scripts/resource_expansion/build_tool_slides.py

# Orquestrador completo
python scripts/resource_expansion_agents/run_resources.py --all

# Validar
python scripts/resource_expansion/validate_resources.py
```

## Integração biblioteca

- Manifest: `datasets/content/library/library_visual_assets.json`
- Hub: `hub_lib.build_library_items()` usa `thumbnail` quando asset `downloaded`
- Cópia runtime: `website/pt/assets/data/library_visual_assets.json`

## Slides

- Registry: `datasets/master-data/resource-expansion/slides_registry.json`
- Output: `website/assets/data/slides/{slug}.json` (8 seções padrão website)
- Padrão entity: `{CONCEPT}_SLD_001`

## Games (roadmap)

Ver `games_roadmap.json`:

1. **Fase 1:** Quiz battle, flashcard streak  
2. **Fase 2:** Caso clínico gamificado, escala rápida  
3. **Fase 3:** Trilhas XP, gestor-boss (indicadores)

## Outros recursos planejados

- Certificados pós-simulado (CERT)
- Protocolos PDF (PRT_PDF)
- Assistente voz SBAR/curriculum (VOICE)
- AR procedimentos IPSG (AR)
- API FHIR indicadores + escalas (API)

## DeepSeek

Tipos em `content-pending/content_types.json`: CVW, IND, DICT, SLD, AST, GAM — pipeline search→generate→review→validate com Grau A.

## Dicionário de medicamentos (MEDICATION_DICTIONARY)

Entradas `{CONCEPT}_DICT_{NNN}` com **parent_entity_code = drug_ref_code** (`DrugReference`).

```bash
# Fila editorial (DrugReference sem DICT)
python scripts/medication_dictionary_agents/run_batch.py --catalog

# Lote determinístico (sem LLM)
python scripts/medication_dictionary_agents/run_batch.py --limit 10

# Lote DeepSeek (Grau A)
python scripts/medication_dictionary_agents/run_batch.py --limit 5 --llm
```

- Canonical: `datasets/master-data/medication-dictionary/canonical.json`
- Dataset: `datasets/clinical/medication_dictionary.json`
- Catálogo pai: `datasets/clinical/drug_references.json`
- Pipeline: search → generate → review → validate → apply

## API / Plataforma

- `GET /api/resource-expansion/status`
- `POST /api/resource-expansion/run` (inclui `medication_dict_limit`, `run_medication_dictionary`)
- `GET /api/medication-dictionary/status`
- `POST /api/medication-dictionary/catalog/rebuild`
- `POST /api/medication-dictionary/run`
- UI: `/resource-expansion`
