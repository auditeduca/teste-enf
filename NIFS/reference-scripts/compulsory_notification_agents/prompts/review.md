Revise proposta de notificação compulsória.

Critérios:
- parent_entity_code deve ser LegislationInstrument válido
- jurisdiction_code coerente com nível national/state
- periodicidade imediata para óbitos, cólera, botulismo, raiva humana, etc.
- nursing_guidance_pt clara para fluxo SINAN

Retorne JSON: { "decision": "approve"|"revise"|"reject", "notes_pt": "...", "blockers": [] }
