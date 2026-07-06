# Carreiras Globais — Master Data

Programa `CAREERS_GLOBAL`: empregos, cursos, trilhas de carreira e concursos em enfermagem para **Brasil + 195 países**, evidência **Grau A**.

## Artefatos

| Arquivo | Descrição |
|---------|-----------|
| [`canonical.json`](../../../datasets/master-data/careers/canonical.json) | Política Grau A, padrão `CAREER_{CC}_{ART}_{NNN}` |
| [`country_registry.json`](../../../datasets/master-data/careers/country_registry.json) | 780 itens (195 × JOB/CUR/PATH/CON) |
| [`coverage_report.json`](../../../datasets/master-data/careers/coverage_report.json) | Métricas |

## Tipos por país

| Código | Conteúdo | URL |
|--------|----------|-----|
| `JOB` | Vagas / empregos | `/empregos/` |
| `CUR` | Cursos | `/cursos/` |
| `PATH` | Trilhas de carreira | `/carreiras/` |
| `CON` | Concursos | `/concursos/` |

Brasil (`BR`) referencia datasets existentes: `job_listings.json`, `course_listings.json`, `career_paths.json`.

## Comandos

```bash
python scripts/career_agents/build_registry.py
python scripts/career_agents/run_careers.py --rebuild --no-llm
python scripts/career_agents/run_careers.py --all --llm
python scripts/career_agents/run_careers.py --countries BR,US,PT,GB --llm
```

## API

- `GET /api/careers/status`
- `POST /api/careers/run`

Também integrado ao orquestrador `/api/global-expansion/run`.

## Evidência Grau A

Fontes: WHO workforce, OECD health labour, conselhos nacionais de enfermagem, PubMed/Cochrane sobre mercado de trabalho.
