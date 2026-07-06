# NIFS-1300-01: Getting Started — Adding a Calculator

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-1300-01                        |
| Status        | Validated                          |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Guia prático para adicionar uma nova calculadora/escala ao website.

## 2. Prerequisites

- Python 3.8+
- Acesso ao repositório do site
- Conhecimento do `tool.schema.json` (Draft-07)

## 3. Step-by-Step

### Step 1: Criar o JSON da ferramenta

Criar `data/tools/{slug}.json` seguindo `data/schemas/tool.schema.json`:

```json
{
  "id": "UUID-v4-aqui",
  "code": "SCALE-NAME-001",
  "slug": "nome-da-escala",
  "version": "1.0.0",
  "status": "published",
  "seo": {
    "title": "Nome da Escala - Descrição | Calculadoras de Enfermagem",
    "description": "Descrição para SEO (max 160 chars).",
    "canonical": "https://www.calculadorasdeenfermagem.com.br/nome-da-escala.html"
  },
  "breadcrumb": {
    "category": "Categoria",
    "categoryHref": "index.html#calculadoras"
  },
  "overview": {
    "name": "Nome da Escala",
    "acronym": "NOME",
    "categoryBadge": "Categoria",
    "icon": "i-shieldcheck",
    "objective": "Objetivo da ferramenta.",
    "indication": "Quando aplicar.",
    "targetPopulation": "População-alvo.",
    "specialty": ["Enfermagem"],
    "averageTime": "2 minutos",
    "evidenceLevel": "I",
    "originalAuthors": ["Autor 1"],
    "organizations": ["Organização 1"],
    "complexity": "basic",
    "rating": 4.8,
    "ratingCount": 0
  },
  "calculator": {
    "inputs": [
      {
        "id": "param1",
        "type": "select",
        "label": "Parâmetro 1",
        "description": "Descrição do parâmetro.",
        "defaultValue": 0,
        "options": [
          { "value": 0, "label": "Opção A", "score": 0, "description": "Desc A" },
          { "value": 1, "label": "Opção B", "score": 1, "description": "Desc B" },
          { "value": 2, "label": "Opção C", "score": 2, "description": "Desc C" }
        ]
      }
    ],
    "formula": {
      "type": "sum",
      "resultLabel": "Escore Total",
      "resultUnit": "pontos",
      "decimals": 0
    }
  },
  "interpretation": {
    "ranges": [
      {
        "min": 0, "max": 2,
        "label": "Risco Baixo",
        "riskLevel": "low",
        "color": "#16a34a",
        "clinicalImplications": "Implicações clínicas.",
        "recommendations": "• Recomendação 1\n• Recomendação 2"
      },
      {
        "min": 3, "max": 5,
        "label": "Risco Alto",
        "riskLevel": "high",
        "color": "#dc2626",
        "clinicalImplications": "Implicações clínicas.",
        "recommendations": "• Recomendação 1"
      }
    ]
  },
  "sae": {
    "nanda": [{ "diagnosis": "Diagnóstico NANDA", "definition": "Definição." }],
    "noc": [{ "outcome": "Resultado NOC", "indicators": ["Indicador 1"] }],
    "nic": [{ "intervention": "Intervenção NIC", "activities": ["Atividade 1"] }]
  },
  "evidence": {
    "foundation": "Fundamentação teórica.",
    "history": "Histórico da escala.",
    "validation": "Validação na literatura.",
    "limitations": "Limitações.",
    "references": [{ "text": "AUTOR. Título. Revista, ano." }]
  },
  "learning": {
    "tips": ["Dica 1", "Dica 2"],
    "examples": [{ "label": "Exemplo", "sublabel": "Score 5", "emoji": "✅", "values": { "param1": 2 } }],
    "quiz": [{ "q": "Pergunta?", "opts": ["A", "B", "C", "D"], "correct": 0, "expl": "Explicação." }]
  },
  "faq": [{ "q": "Pergunta frequente?", "a": "Resposta." }],
  "about": { "title": "Como funciona", "html": "<p>Explicação detalhada.</p>" }
}
```

### Step 2: Gerar HTML

```bash
python3 scripts/generate_tool_page.py data/tools/nome-da-escala.json > nome-da-escala.html
```

### Step 3: Adicionar ao i18n

Adicionar chaves `tool.nome-da-escala.titulo` e `tool.nome-da-escala.desc` em:
- `i18n/en.json`
- `i18n/es.json`
- Outros idiomas conforme necessário

### Step 4: Adicionar à home

Adicionar card na `index.html` na seção apropriada (calculadoras/escalas/simulados).

### Step 5: Testar

- Abrir `{slug}.html` no navegador
- Verificar cálculo interativo
- Testar 5 perfis (Padrão/Estudante/Urgência/Acadêmico/Gestor)
- Validar SEO (title, meta, canonical)
- Testar em mobile

## 4. Formula Types

### `sum` (escalas de escore):
```json
"formula": { "type": "sum", "resultLabel": "Escore", "resultUnit": "pontos", "decimals": 0 }
```
Soma os `score` de cada input selecionado.

### `expression` (cálculo numérico):
```json
"formula": { "type": "expression", "expression": "peso / (altura * altura)", "resultLabel": "IMC", "resultUnit": "kg/m²", "decimals": 1 }
```
Avalia expressão matemática com variáveis dos inputs.

## 5. 6-Dimension Checklist

Cada ferramenta DEVE ter as 6 dimensões do Clinical Intelligence Package:

- [ ] **Conteúdo** — overview + calculator + interpretation
- [ ] **SAE** — nanda + noc + nic
- [ ] **Evidência** — foundation + references (com GRADE quando possível)
- [ ] **Aprendizado** — tips + examples + quiz
- [ ] **FAQ** — pelo menos 2 perguntas
- [ ] **Sobre** — HTML explicativo

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-01 | Backend (SSG) |
| NIFS-900-03 | Architecture |
| NIFS-1100-03 | Content Governance (review process) |
