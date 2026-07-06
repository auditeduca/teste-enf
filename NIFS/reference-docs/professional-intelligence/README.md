# Nursing Professional Intelligence Hub (NPIH)

Camada integrada de **legislação + carreira + mercado + desenvolvimento profissional** — transformando calculadoras em **resultado clínico + contexto profissional**.

## Domínio

```
professional_intelligence/
├── laws / regulations / professional_bodies
├── certifications / careers / jobs / public_exams
├── competencies / skills / institutions / salary_data / alerts
```

Master data: `datasets/master-data/professional-intelligence/`

## Capacidades (foundation)

| # | Capacidade | Status |
|---|------------|--------|
| 1 | Regulatory Knowledge Engine (schema + categorias) | ✅ |
| 2 | Tool → contexto profissional (Braden, Infusion, GCS, Apgar, NC) | ✅ |
| 3 | Regulatory Nursing Agent (stub com referências) | ✅ |
| 4 | Banco concursos (seed) + plano 30/60/90 dias | ✅ |
| 5 | Mapa de carreira BR/US/JP/EU | ✅ |
| 6 | Certifications registry + alert rules | ✅ schema |
| 7 | Adaptação por persona na resposta de tool-context | ✅ |
| 8 | Nursing Assessment Engine (questões IA) | 🔜 |
| 9 | Career Dashboard completo | 🔜 |
| 10 | Alertas em tempo real | 🔜 |

## API

```
GET  /api/professional-intelligence/status
GET  /api/professional-intelligence/tool-context?tool_code=TOOL.BRADEN&persona=profissional
POST /api/professional-intelligence/regulatory/query  { "question": "..." }
POST /api/professional-intelligence/exam-plan         { "goal": "...", "days": 30 }
GET  /api/professional-intelligence/career-map?country=BR
```

## CLI

```powershell
python scripts/professional_intelligence_agents/run_batch.py --status
python scripts/professional_intelligence_agents/run_batch.py --tool TOOL.BRADEN --persona estudante
python scripts/professional_intelligence_agents/run_batch.py --question "Posso realizar este procedimento?"
python scripts/professional_intelligence_agents/run_batch.py --exam-goal "Enfermeiro hospitalar" --exam-days 60
```

## Integrações

- `datasets/regulatory/br/legislation_tool_links.json` — 12 links (incl. Braden, Infusion, GCS, Apgar)
- `datasets/community/career_paths.json` — trilhas existentes
- Nursing OS — domínio `NPIH` em `nursing-os/domains.json`
- Agentes — `regulatory`, `exam_prep` em `nursing-ai-agents/agents_registry.json`

## Diferencial

Calculadora entrega **resultado + legislação + deveres + documentação + tópicos de concurso**, adaptado por persona (estudante, profissional, gestor, acadêmico).

## Próximas fases

1. Expandir `tool_professional_context` para todas as ferramentas do catálogo
2. Ingestão real de editais (concursos) + vagas institucionais
3. Nursing Certification Passport no perfil do usuário
4. Alertas monitorando normas COFEN/MS
5. Nursing Assessment Engine — questões com metadados `{ topic, level, exam, skill }`
