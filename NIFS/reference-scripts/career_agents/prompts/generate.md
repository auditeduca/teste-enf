# Career content generation — DeepSeek — Grau A

Gere conteúdo de carreira em enfermagem para o país indicado.

## Saída JSON

```json
{
  "country_code": "XX",
  "evidence_grade": "A",
  "sources": [
    {"citation": "...", "doi_or_url": "...", "organization": "WHO", "year": 2024}
  ],
  "jobs": [
    {"title": "...", "region": "...", "employment_type": "...", "seniority": "...", "licensing_body": "..."}
  ],
  "courses": [
    {"title": "...", "provider": "...", "modality": "online|presencial", "credential": "..."}
  ],
  "career_paths": [
    {"title": "...", "milestones": ["..."], "licensing_steps": ["..."]}
  ],
  "concursos": [
    {"title": "...", "body": "...", "frequency": "..."}
  ]
}
```

Priorize WHO, OECD, conselho/regulador nacional. Mínimo 2 vagas, 1 curso, 1 trilha, 1 concurso por país quando aplicável.
Nunca incluir API keys.
