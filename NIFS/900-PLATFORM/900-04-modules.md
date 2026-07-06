# NIFS-900-04: Modules

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-04                        |
| Status        | Validated                          |
| Version       | 2.1.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Documentar os módulos e ferramentas do website — SAE, SBAR, CV, Catálogo, Simulados, Flashcards e ferramentas data-driven.

## 2. Module Inventory

| Módulo | Arquivo | Tipo | Função |
|--------|---------|------|--------|
| SAE Engine | `js/modules/sae-engine.js` | JS module | Wizard do Processo de Enfermagem |
| SBAR Engine | `js/modules/sbar-engine.js` | JS module | Wizard de comunicação SBAR |
| CV Engine | `js/modules/cv-engine.js` | JS module | Gerador de currículo |
| Catalog Page | `js/modules/catalog-page.js` | JS module | Página de catálogo com filtros |
| **Simulados** | `simulados.html` | **Ferramenta completa** | Simulador clínico data-driven |
| **Flashcards** | `flashcards.html` | **Ferramenta completa** | Repetição espaçada data-driven |

## 3. Simulados — Ferramenta Data-Driven

**Arquivo**: `simulados.html`

Ferramenta completa de simulação clínica que consome os mesmos dados do banco que alimentam as calculadoras. NÃO é um link — é uma página interativa independente.

### Arquitetura:
```
Banco de Dados → JSON da calculadora (tool-config) → Simulados
```

### Funcionamento:
- Apresenta cenários clínicos com parâmetros do paciente
- Usuário responde perguntas de tomada de decisão
- Feedback imediato com NANDA/NIC/NOC relacionados ao cenário
- Persistência de progresso via `localStorage` (key: `sim_progress_{topic}`)
- Histórico de sessões via `localStorage` (key: `sim_history_{topic}`)

### Estrutura de Dados por Cenário:
```javascript
{
  id: "apgar-s1",
  tag: "normal|moderate|critical",
  tagLabel: "Cenário 1",
  text: "Descrição do cenário clínico...",
  params: { fc: "≥100 bpm", respiracao: "Bom", ... },
  question: "Pergunta de tomada de decisão",
  options: [
    { label: "Resposta A", correct: true },
    { label: "Resposta B", correct: false }
  ],
  feedback: {
    correct: "Explicação do acerto",
    incorrect: "Explicação do erro",
    nanda: "Diagnóstico NANDA relacionado",
    nic: "Intervenção NIC relacionada",
    noc: "Resultado NOC relacionado"
  }
}
```

### Tópicos Suportados:
| Tópico | Cenários | Status |
|--------|----------|--------|
| APGAR | 5 | Implementado |
| Glasgow | 0 | Planejado |
| Braden | 0 | Planejado |

### Estado da Sessão:
```javascript
state = {
  topic: 'apgar',
  currentIdx: 0,
  answered: [{ optionIdx, correct }],
  score: 0,
  started: false
}
```

### Tela de Resultado:
- Pontuação percentual
- Breakdown: acertos, erros, total
- Mensagem de feedback conforme faixa (≥80%, ≥60%, ≥40%, <40%)
- Botão "Refazer simulado"

## 4. Flashcards — Ferramenta Data-Driven

**Arquivo**: `flashcards.html`

Ferramenta completa de repetição espaçada que consome os mesmos dados clínicos do banco (NANDA-I, NIC, NOC, interpretação, segurança). NÃO é um link — é uma página interativa independente.

### Arquitetura:
```
Banco de Dados → NANDA/NIC/NOC/interpretação → Flashcards
```

### Funcionamento:
- Cartões com frente (pergunta) e verso (resposta + detalhe)
- Flip animation 3D (CSS `transform: rotateY(180deg)`)
- 3 ações por cartão: **Dominado**, **Revisar depois**, **Pular**
- Persistência de estado via `localStorage` (key: `fc_states_{topic}`)
- Filtros por categoria: Todos, NANDA-I, NIC, NOC, Interpretação, Segurança

### Estrutura de Dados por Cartão:
```javascript
{
  id: "fc-n1",
  cat: "nanda|nic|noc|interpretation|safety",
  catLabel: "NANDA-I",
  q: "Pergunta (frente do cartão)",
  a: "Resposta (verso do cartão)",
  detail: "Explicação detalhada com contexto clínico"
}
```

### Categorias e Fontes de Dados:

| Categoria | Fonte no Banco | Qtd (APGAR pilot) |
|-----------|---------------|-------------------|
| NANDA-I | `sae.nanda[]` | 2 |
| NIC | `sae.nic[]` | 3 |
| NOC | `sae.noc[]` | 2 |
| Interpretação | `interpretation.ranges[]` | 4 |
| Segurança | `safety_goals` + `medication_rights` | 3 |

### Sistema de Repetição Espaçada:
- **New**: cartão nunca visto (prioridade máxima na fila)
- **Review**: marcado para revisar (prioridade média)
- **Known**: dominado (prioridade mínima)
- Ordenação: New → Review → Known
- Stats em tempo real: Total, Dominados, Revisar, Novos

### Estado Persistido:
```javascript
// localStorage key: fc_states_{topic}
{
  "fc-n1": { status: "known", lastReviewed: "2026-07-05T..." },
  "fc-n2": { status: "review", lastReviewed: "2026-07-05T..." }
}
```

## 5. SAE Engine

Wizard interativo do Processo de Enfermagem (5 etapas):

1. **Coleta de Dados** — identificação do paciente
2. **Diagnóstico** — seleção de diagnósticos NANDA-I
3. **Planejamento** — definição de metas NOC
4. **Implementação** — intervenções NIC
5. **Avaliação** — registro de resultados

### NANDA-I hardcoded (protótipo v1):
```javascript
var NANDA = [
  { code: "00032", title: "Risco de Queda", domain: "Segurança/Proteção" },
  { code: "00202", title: "Lesão por Pressão", domain: "Segurança/Proteção" },
  ...
];
```

**Evolução v5.0**: Substituir por retrieval do banco de 244 NANDA-I via API + inferência bayesiana.

### Persistência: `localStorage` key: `sae-draft-v1`

## 6. SBAR Engine

Wizard de comunicação clínica SBAR (4 etapas):

1. **Situação** — identificação + problema atual
2. **Background** — histórico relevante
3. **Avaliação** — análise clínica
4. **Recomendação** — ação sugerida

### Persistência: `localStorage` key: `sbar-draft-v1`

## 7. CV Engine

Gerador de currículo em 5 etapas. Persistência: `localStorage` key: `cv-draft-v1`

## 8. Catalog Page

Página de catálogo com filtros dinâmicos por categoria, busca por texto, grid de cards.

### Data sources:
| Arquivo | Records | Conteúdo |
|---------|---------|----------|
| `modules/data/biblioteca.json` | 12 | Biblioteca de provas |
| `modules/data/calendario-vacinal.json` | 10 | Calendário vacinal |
| `modules/data/doencas-compulsorias.json` | 8 | Doenças de notificação compulsória |
| `modules/data/nanda.json` | 12 | Diagnósticos NANDA (subset) |
| `modules/data/protocolos.json` | 11 | Protocolos institucionais |

## 9. Module Data Gap

Os dados embutidos nos módulos são **subsets simplificados**. O NIS v5.0 substituirá por:
- `nanda.json` (12) → API NIS com 244 diagnósticos completos
- `doencas-compulsorias.json` (8) → API NIS com 54 agravos + CID-10 + SINAN
- `protocolos.json` (11) → API NIS com 200 guidelines
- `calendario-vacinal.json` (10) → API NIS com esquema vacinal completo
- **Simulados** → API NIS com cenários gerados dinamicamente do banco
- **Flashcards** → API NIS com cartões gerados de NANDA/NIC/NOC do banco

## 10. Recursos Adicionais — Mapeamento de Fontes

A grade de "Recursos Adicionais" (10 cards) no rodapé de cada calculadora mapeia cada recurso à sua fonte de dados no banco:

| Recurso | Fonte de Dados | Tipo | URL |
|---------|---------------|------|-----|
| Artigos | `evidence.references` + `evidence.foundation` | Link | `artigos.html` |
| Protocolos | `institutional_protocols` (ANVISA, MS, OMS) | Link | `protocolos.html` |
| Casos Clínicos | `learning.examples` + `clinical_decision_trees` | Link | `casos-clinicos.html` |
| Check-lists | `safety_goals` + `medication_rights` | Download (Excel/PDF) | `checklists.html` |
| **Simulados** | Cenários P&R do banco | **Ferramenta completa** | `simulados.html` |
| **Flashcards** | NANDA/NIC/NOC do banco | **Ferramenta completa** | `flashcards.html` |
| Infográficos | Visualizações dos dados clínicos | Link | `infograficos.html` |
| Guia de Bolso | Resumo condensado (`pocket` dimension) | Link | `guia-bolso.html` |
| Slides | Material de apresentação do banco | Download | `slides.html` |
| Vídeos | Tutoriais e demonstrações | Link | `videos.html` |

## 12. Biblioteca — Netflix-style Content Hub

**Arquivo**: `biblioteca.html`

A biblioteca é o hub central que integra todos os tipos de conteúdo por conceito clínico. Funciona como uma plataforma de streaming (Netflix-style) onde o usuário filtra por calculadora e vê todo o conteúdo relacionado organizado por tipo.

### Arquitetura:
```
Filtro por Calculadora (ex: APGAR)
    ↓
Seções por Tipo de Conteúdo:
    ├── Artigos (conteúdo + evidence + referências)
    ├── Protocolos (ANVISA, MS, OMS)
    ├── Casos Clínicos (cenários com P&R interativa)
    ├── Check-lists (Excel/PDF com checklist interativo)
    ├── Infográficos (visualizações dos dados)
    ├── Guias de Bolso (cartões de referência rápida)
    ├── Mapas Mentais (NANDA → NIC → NOC visual)
    └── Slides (apresentações com navegação)
```

### Componentes:
- **Hero**: Título + busca + stats (97 calculadoras, 8 tipos, 500+ recursos)
- **Filter bar (sticky)**: Chips por calculadora (APGAR, Glasgow, Braden, etc.)
- **Active filter indicator**: Mostra filtro ativo com botão "Limpar"
- **Netflix rows**: Scroll horizontal por tipo de conteúdo com botões de navegação
- **Cards**: Thumbnail com gradiente por tipo, badge da calculadora, título, excerpt, meta

### Data Structure:
```javascript
const LIB_DATA = {
  calculators: [{ slug, name, category }],
  sections: [{
    type: 'artigos|protocolos|casos|checklists|infograficos|guias|mapas|slides',
    title, icon, thumbClass,
    items: [{ id, calc, title, excerpt, meta[], url }]
  }]
};
```

### Templates por Tipo de Conteúdo:

| Template | Arquivo | Estrutura |
|----------|---------|-----------|
| Artigo | `artigo.html` | Hero + body (h2/p/blockquote) + referências + relacionados |
| Protocolo | `protocolo.html` | Hero + steps numerados + info grid + relacionados |
| Caso Clínico | `caso-clinico.html` | Patient card + vitals + quiz interativo + NANDA/NIC/NOC |
| Check-list | `checklist.html` | Checkboxes interativos + progresso + persistência localStorage |
| Infográfico | `infografico.html` | Visual: parâmetros + score table + bands + mnemônico |
| Guia de Bolso | `guia-bolso.html` | Cartão compacto com tabela + bands + nota crítica |
| Mapa Mental | `mapa-mental.html` | Centro + 3 branches (NANDA/NIC/NOC) + leaves |
| Slides | `slides.html` | Stage 16:9 + navegação + thumbnails + keyboard |

### Padrão Visual:
- Todos os templates seguem o Design System (site-styles.css, paleta azul)
- Breadcrumb: Início → Biblioteca → Tipo → Título
- Badges: tipo de conteúdo + calculadora + (evidência/severidade/fonte)
- Seção "Conteúdo relacionado" no rodapé de cada template
- Header/Footer/A11y via partials-loader.js
- Responsividade mobile garantida em todos

## 11. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-02 | Frontend (calc-engine, fluxo cognitivo vertical) |
| NIFS-700-00 | Nurse-PaLM Architecture (cognitive integration) |
| NIFS-600-02 | Reasoning Pipeline (SAE evolution) |
| NIFS-600-18 | Consensus Engine (multi-agent SBAR) |
