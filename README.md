# CKO — Clinical Knowledge OS

Aplicação de calculadoras, escalas, guias e simulados de enfermagem.

O conhecimento canônico vive em JSON. HTML é projeção. O browser só recalcula. Nada do canônico é regenerado por LLM.

## O que este repositório é

Este repositório **é** o produto. Toda a documentação, os contratos, o motor, os validadores, os pilotos e o HTML gerado estão aqui. Não há dependência de arquivos, dumps ou sites externos para entender ou rodar o v0.1.

```
data/tools/*.json     fonte da verdade
        │
        ▼
engine + validators   schema, score, audit, dual-render
        │
        ▼
render/fetch          produção (CSS first-party via link)
render/inline         preview (CSS embutido)
```

## Princípios

- INTERNAL_FIRST
- ACQUIRE_ONCE
- VALIDATE_ONCE
- VERSION_ON_CHANGE
- REUSE_MANY
- PROJECT_MANY
- NO_SILENT_OVERWRITE
- NO_LLM_REGENERATION_OF_CANONICAL_CONTENT

Regra de ouro: conhecimento canônico validado não é regenerado. Novos usos são projeções.

## Lote piloto (v0.1)

| Slug | Tipo | Motor | Status |
|---|---|---|---|
| `gotejamento` | calculator | `expression` | review |
| `meows` | scale | `sum` | review |
| `cinco-ts-pcr` | guide | conteúdo | review |
| `simulado-tecnico` | exam | quiz original | review |
| `dimensionamento` | guide | sem fórmula | **hold** |

O cálculo THE/HPPD de dimensionamento **não** está implementado. A página existe para não fingir um quadro de pessoal.

## Como rodar

Python 3.11+.

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
python3 -m engine.cli validate
python3 -m engine.cli build
python3 -m engine.cli audit
python3 -m engine.cli serve --port 8081
```

Abra `http://127.0.0.1:8081`.

- Produção fetch: `/` e `/tools/{slug}.html`
- Preview inline: gerado em `render/inline/`
- Inspector read-only: `/inspector.html`

## Adicionar um objeto

1. Crie `data/tools/{slug}.json` segundo `schemas/tool.schema.json`.
2. Declare `kind`: `calculator`, `scale`, `guide` ou `exam`.
3. SAE com NIC/NOC sem fonte canônica/licenciada permanece `HOLD`.
4. Rode `validate`, `pytest`, `build` e `audit`.

## Estado probatório

A implementação do lote piloto **não** demonstra aderência 360°, certificação, conformidade integral nem agentes em produção.

Redação permitida:

> O CKO possui motor canônico, contratos, validadores e um lote piloto renderizável. A aderência 360° e a publicação clínica completa ainda não foram demonstradas.

## Documentação

Índice em `docs/README.md`.

## Licença

Uso proprietário — Audit Educa / Leivis Melo.
