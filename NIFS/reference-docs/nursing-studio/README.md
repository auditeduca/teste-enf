# NKOS Studio — Calculadoras de Enfermagem Studio

Editor visual de alto padrão integrado ao **Knowledge Graph** com agentes IA para redes sociais.

## Pipeline

```
Grafo (entity_code) → Template Creator → Social Generate → Publication Evaluator → Image Reviewer
```

## Agentes

| Agente | Função |
|--------|--------|
| Template Creator | Cria spec de template + blocos a partir do grafo |
| Template Editor | Adapta copy/locale/persona |
| Publication Evaluator | Score por perfil, país, clínica, marca |
| Image Reviewer | brand / clinical / cultural / accessibility (VEIP) |

## Formatos sociais

Instagram Post/Story, Facebook, LinkedIn, X/Twitter, WhatsApp preview.

## Blocos premium

headline, subheadline, clinical_badge, hero_visual, cta_button, brand_bar, evidence_footer, persona_strip, locale_disclaimer, tool_chip, hashtag_row

## API

```
GET  /api/studio/status
GET  /api/studio/formats
GET  /api/studio/blocks
GET  /api/graph/studio/context?tool_code=TOOL.BRADEN&persona=estudante&country=BR
POST /api/studio/generate   { tool_code, format, persona, country }
POST /api/studio/evaluate
POST /api/studio/review
GET  /api/studio/asset/{filename}.svg
```

## CLI

```powershell
python scripts/nursing_studio_agents/run_batch.py --status
python scripts/nursing_studio_agents/run_batch.py --tool TOOL.BRADEN --format instagram_post --persona estudante
```

Output: `website/assets/images/studio/`

## UI

- `/nursing-studio` — Studio completo
- `/graph-ai` — link direto para Studio
