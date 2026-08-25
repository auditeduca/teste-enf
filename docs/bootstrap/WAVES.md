# Waves (materialização, não criação tardia)

Todas as 44 camadas já estão em `cko_core/layer_registry.json` (M0).

| Wave | Conteúdo | Maturidade alvo desta wave |
|---|---|---|
| W0 | MD, REG, IDs, fields, locales, units, hash, provenance, version, risk, control | M0–M1 |
| W1 | Validators, CAAT, IPE, ALCOA++, audit, evidence | M1 |
| W2 | API registry, adapters, acquisition, tools | M1 |
| W3 | Agent registry, permissions, orchestrator | M1 |
| W4 | Digital twin | M1 |
| W5 | SAE / search | M1 |
| W6 | COSO/COBIT mappings (sem inventar cláusula) | M1 |
| W7 | A11Y, LGPD, security, SEO, metadata, JSON-LD, OG, i18n, sustainability, DS | M1 |
| W8 | População de domínio (calculators, scales, meds, content) | M2+ |
| W9 | Renderer, runtime, publication, monitoring | M3 |
| W10 | CAAT full population, IPE, AUD-8L, reperformance, release | M4–M5 |

Este changeset cobre **registro W0** e **superfície admin read-only**. Não cobre W10.
