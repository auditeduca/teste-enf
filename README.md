# CKO — Calculadoras de Enfermagem

Plataforma governada de conhecimento, ferramentas clínicas e conteúdo para enfermagem.

Constituição: [`docs/constitution/CKO-INS-AI-PROJECT-001.md`](docs/constitution/CKO-INS-AI-PROJECT-001.md).

O conhecimento canônico e os registries Day Zero vivem em JSON versionado neste GitHub. HTML é projeção. O browser só recalcula. Nada do canônico é regenerado por LLM.

## O que este repositório é

Este repositório **é** o produto no Day Zero. Documentação, constituição, registries, contratos, motor, validadores, candidatos piloto e HTML gerado estão aqui.

```
cko_core / cko_md / cko_reg / cko_assurance   identidade e governança (M0)
data/tools/*.json                             candidatos de domínio do lote piloto
        │
        ▼
engine + validators   schema, bootstrap, score, audit, dual-render
        │
        ▼
render/fetch          produção (CSS first-party via link) + admin.html
render/inline         preview (CSS embutido)
```

Admin e frontend compartilham os mesmos contratos (`admin/contract.json`). O Admin não grava fórmula.

## Princípios

- CKO-MD FIRST, CKO-REG SECOND
- ONE CANONICAL IDENTITY
- NO SILENT OVERWRITE
- NO PASS BY INFERENCE
- NO LLM REGENERATION OF CANONICAL CONTENT
- RECOVER BEFORE REBUILD

## Lote piloto (candidatos de domínio)

| Slug | Tipo | Motor | Status |
|---|---|---|---|
| `gotejamento` | calculator | `expression` | review |
| `meows` | scale | `sum` | review |
| `cinco-ts-pcr` | guide | conteúdo | review |
| `simulado-tecnico` | exam | quiz original | review |
| `dimensionamento` | guide | sem fórmula | **hold** |

O cálculo THE/HPPD de dimensionamento **não** está implementado. A página existe para não fingir um quadro de pessoal.

As 44 camadas constitucionais estão **registradas** (44/44 business keys). Isso não significa população, implementação ou assurance.

## Como rodar

Python 3.11+.

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
python3 -m engine.cli bootstrap
python3 -m engine.cli validate
python3 -m engine.cli build
python3 -m engine.cli audit
python3 -m engine.cli serve --port 8081
```

Abra `http://127.0.0.1:8081`.

- Frontend: `/` e `/tools/{slug}.html`
- Admin: `/admin.html` (Studio integrado: banco, catálogo, renderer, deploy Git)
- Inspector: `/inspector.html` (candidatos piloto)
- Preview inline: `render/inline/`

## Adicionar um objeto de domínio

1. A identidade deve existir ou ser registrada em MD **antes** de QUALQUER binding REG.
2. Crie `data/tools/{slug}.json` segundo `schemas/tool.schema.json` somente como candidato, até promoção.
3. SAE com NIC/NOC sem fonte canônica/licenciada permanece `HOLD`.
4. Rode `validate`, `pytest`, `build` e `audit`.

## Estado probatório

A implementação **não** demonstra aderência 360°, certificação, conformidade COSO/COBIT, base MD completa nem agentes em produção.

Redação permitida:

> O CKO possui constituição CONTROLLED_DRAFT, 44 camadas registradas, motor canônico, contratos, validadores e um lote piloto renderizável. Admin e frontend leem os mesmos JSON no GitHub. A aderência 360° e a publicação clínica completa ainda não foram demonstradas.

## Documentação

Índice em `docs/README.md`. Constituição em `docs/constitution/`.

## Licença

Uso proprietário — Audit Educa / Leivis Melo.
