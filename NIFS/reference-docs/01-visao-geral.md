# 01 — Visão geral

## O que é o CALENF-NKD

O **CALENF-NKD** (Nursing Knowledge Operating System) é um repositório que materializa o modelo de dados **NKOS v4.4** em arquivos JSON e os publica como **site estático** voltado a enfermagem clínica e educacional.

O projeto combina:

- **Datasets estruturados** — terminologias (NANDA, NIC, NOC), ferramentas clínicas, protocolos, conteúdo educacional, metadados SEO e traduções.
- **Geradores Python** — scripts que validam referências cruzadas e renderizam ~222 páginas HTML em pt-BR, com variantes de locale derivadas.
- **Site estático** — ferramentas interativas (calculadoras/escalas), busca client-side, bibliotecas NNN, hub de medicamentos e páginas institucionais.

## Fases NKOS (1–12)

| Fase | Domínio principal |
|------|-------------------|
| 1–3 | Entidades base, terminologias, relações |
| 4–5 | Protocolos, educação, simulados |
| 6–7 | Ferramentas clínicas, templates de página |
| 8–12 | Comunidade, runtime, analytics, publicação |

O status detalhado de cada entidade está em `datasets/metadata/nkos_implementation_status.json`. Todas as 12 fases estão **100% completas** no dataset; pendências restantes são de **conteúdo traduzido** (P1) e **runtime** (P3).

## Números de referência (build completo)

- **~222 páginas HTML** pt-BR
- **7 locales** no site (pt-BR, en, es, fr, de, it, ja)
- **100 ferramentas** clínicas
- **0 links quebrados** (audit)
- **5544** registros Content + derivados RAG/search

## Fluxo de trabalho típico

1. Alterar ou gerar datasets (`scripts/generate_phase*.py`, `generate_phases_8_12.py`).
2. Validar integridade (`validate_phases_1_7.py`, `validate_phases_8_12.py`).
3. Regenerar site (`generate_website_pt.py`).
4. Auditar (`audit_website_pt.py`) ou rodar CI (`run_ci.py`).

## Clinical Intelligence Engine (CAL-001)

Motor SAE estruturado NANDA–NIC–NOC e evolução probabilística V3→V8 (especificação + roadmap; runtime em implementação):

→ [12-clinical-intelligence-engine.md](12-clinical-intelligence-engine.md) · [clinical-engine/README.md](clinical-engine/README.md)

## Próximo documento

→ [02-arquitetura.md](02-arquitetura.md)
