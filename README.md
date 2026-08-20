# NIS — Nursing Intelligence System

Repositório **greenfield** do Nursing Intelligence System (calculadorasdeenfermagem.com.br).

Este branch começa o produto do zero: especificação JSON → motor de pontuação testável → HTML estático. O dump legado (`reference-website/`, `NIFS/`, `i18n-pipeline/`) permanece no histórico de `teste-enf` como referência e **não** faz parte do runtime novo.

## Por que um start limpo

Os repositórios atuais da org (`teste-enf`, `Calculadoras-de-Enfermagem`) acumulam HTML gerado, duplicatas e experimentos. O NIFS define a arquitetura; este repositório é o código canônico derivado dela.

```
data/tools/*.json     fonte da verdade de cada calculadora
        │
        ▼
packages/nis_engine   valida schema, calcula, gera HTML
        │
        ▼
apps/web              site estático (SEO + calc-engine.js)
```

## Primeira entrega

| Ferramenta | Fórmula | Função |
|---|---|---|
| `apgar` | `sum` | Escala clínica (5 sinais, 0–10) |
| `imc` | `expression` | Cálculo numérico (`peso / (altura * altura)`) |

## Como rodar

Python 3.11+.

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest
python3 -m nis_engine.cli build
python3 -m nis_engine.cli serve --port 8081
```

Abra `http://127.0.0.1:8081`.

## Adicionar uma calculadora

1. Crie `data/tools/{slug}.json` seguindo `data/schemas/tool.schema.json`.
2. Cubra as 6 dimensões: conteúdo, SAE, evidência, aprendizado, FAQ, sobre.
3. Rode `python3 -m nis_engine.cli validate` e `pytest`.
4. Rode `build` e revise `apps/web/tools/{slug}.html`.

## Novo repositório GitHub

O token deste Cloud Agent só alcança `auditeduca/teste-enf`. Para um repositório GitHub novo (recomendado: `auditeduca/nis`, vazio, sem README):

```bash
git remote add nis https://github.com/auditeduca/nis.git
git push -u nis cursor/nis-greenfield-cd31:main
```

Enquanto isso, este PR deixa a fundação revisável aqui.

## Licença

Uso proprietário — Audit Educa / Leivis Melo. Licenciamento aberto ainda não definido (NIFS-000).
