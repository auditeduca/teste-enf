# Nursing Knowledge API (NKA)

Infraestrutura digital global — **Nursing Knowledge API** em `/api/v1`.

## Gateway

```
GET /api/v1
GET /api/v1/status
```

Autenticação (dev): `X-API-Key: nkos_dev_free` ou bypass localhost.  
Identidade: header `X-Nursing-Identity` JSON ou query params `role`, `country`, `level`, `interest`.

## Fase 1 — MVP

### Clinical API
```
GET /api/v1/clinical/scales
GET /api/v1/clinical/scales/braden
GET /api/v1/clinical/calculators
GET /api/v1/clinical/protocols
GET /api/v1/clinical/glossary
```

### Calculator API
```
POST /api/v1/calculator/drip-rate
{ "volume": 500, "time": 4, "factor": 20 }
→ { "drops_per_minute": 42, "ml_per_hour": 125.0 }

POST /api/v1/calculator/bmi
POST /api/v1/calculator/fluid-balance
```

### Content API
```
GET /api/v1/content/articles
GET /api/v1/content/articles/{id}
```

### Identity API
```
GET /api/v1/identity/profile
POST /api/v1/identity/profile
GET /api/v1/identity/profiles
```

### Visual API
```
POST /api/v1/visual/generate
{ "country": "Japan", "persona": "student", "topic": "APGAR", "style": "academic" }
```

## Fase 2 — Institucional

```
GET /api/v1/education/path/icu-nursing
GET /api/v1/regulation/country/BR/topic/medication
GET /api/v1/career/path/intensive-care
```

## Fase 3 — Plataforma aberta

```
POST /api/v1/jobs/match
GET  /api/v1/research/trends
POST /api/v1/agent/career-coach
```

## Segurança

- OAuth2 schema (futuro)
- API keys + tiers: free, education, enterprise, developer, internal
- Rate limiting in-memory
- Access logs em `datasets/master-data/nursing-knowledge-api/logs/`

## Modelo de negócio

Ver `business_model.json` — Free / Educação / Enterprise / Developer marketplace.

## CLI

```powershell
python scripts/nursing_knowledge_api/run_batch.py --status
python scripts/nursing_knowledge_api/run_batch.py --scale braden
python scripts/nursing_knowledge_api/run_batch.py --drip
```

## Serviços

Mapa físico: [`services/README.md`](../../services/README.md)
