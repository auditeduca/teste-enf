# NIFS-900-02: Frontend (Calc Engine)

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-02                        |
| Status        | Validated                          |
| Version       | 2.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Documentar o frontend do website — o motor interativo de calculadoras, ferramentas clínicas data-driven, e o fluxo cognitivo vertical integrado.

## 2. Arquitetura de Dados — Fonte Única de Verdade

```
Banco de Dados (NIFS / Supabase)
│
├── Dados clínicos (NANDA-I, NIC, NOC, interpretações)
├── Dados de evidência (GRADE, referências, artigos)
├── Dados de protocolos (ANVISA, Ministério da Saúde, OMS)
├── Dados de medicação (9 certos, IPSG, LASA)
├── Dados de casos clínicos (cenários, exemplos)
├── Dados de segurança (metas IPSG, check-lists)
├── Dados educacionais (tips, quiz, FAQ)
│
├──→ Calculadoras (APGAR, Glasgow, Braden...)
│    └── consomem: inputs, fórmulas, interpretação, SAE
│
└──→ Ferramentas (Simulados, Flashcards, etc.)
     ├── Simulados → P&R (banco de dados)
     ├── Flashcards → P&R (banco de dados)
     ├── Artigos → conteúdo + evidence + referências
     ├── Protocolos → protocolos ANVISA, MS, OMS
     ├── Casos Clínicos → conteúdo ANVISA, MS, OMS
     ├── Check-lists → excel, PDFs ANVISA, MS, OMS
     ├── Infográficos → visualizações geradas do banco
     ├── Guia de Bolso → resumos do banco
     ├── Slides → material de apresentação do banco
     └── Vídeos → tutoriais e demonstrações
```

Cada ferramenta NÃO possui dados próprios — ela consulta o mesmo banco que a calculadora correspondente. O JSON embutido na página (`<script id="tool-config">`) é um snapshot desse banco. Na migração para Supabase, tanto calculadoras quanto ferramentas passam a consumir da mesma API.

## 3. Fluxo Cognitivo Vertical (6 Steps)

Cada página de calculadora segue um fluxo cognitivo vertical sequencial que representa o pensamento clínico do enfermeiro. O fluxo NÃO usa tabs horizontais para o raciocínio — tudo é vertical e contínuo.

### Estrutura dos 6 Steps:

| Step | Título | Visibilidade | Conteúdo |
|------|--------|-------------|----------|
| 1 | Parâmetros (Avaliação) | Sempre visível | Inputs da calculadora (selects, campos) |
| 2 | Resultado | Sempre visível | Score + banner de status + fórmula visual |
| 3 | Raciocínio NANDA · NIC · NOC | Oculto até calcular | Grid 3 colunas: diagnóstico, intervenção, resultado |
| 4 | Plano de Ação | Oculto até calcular | Lista de ações baseadas no resultado |
| 5 | Avaliação & Monitoramento (NOC) | Oculto até calcular | Texto descritivo do monitoramento esperado |
| 6 | Segurança do Paciente | Oculto até calcular | 9 Certos + Metas IPSG (parte do perfil Profissional) |

### Comportamento:
- Steps 3-6 ficam ocultos (`display:none`) até o usuário clicar em "Calcular"
- Após calcular, o JS revela os steps 3-6 com `scrollIntoView({ behavior: "smooth" })`
- O conteúdo dos steps 3-6 é dinâmico — preenchido conforme o resultado da calculadora

### Contrato HTML:
```html
<div class="flow-divider" id="calcFlowDivider" style="display:none;">
  <span>Raciocínio Clínico Integrado</span>
</div>
<div id="calcClinicalFlow" class="clinical-flow-wrap">
  <!-- Step 3: NANDA/NIC/NOC -->
  <!-- Step 4: Plano de Ação -->
  <!-- Step 5: Avaliação NOC -->
  <!-- Step 6: Segurança do Paciente (9 Certos + IPSG) -->
</div>
```

## 4. Perfis de Visualização

### Ordem Canônica dos Tabs:

| Ordem | Perfil | Ícone | Foco |
|-------|--------|-------|------|
| 1 | Padrão | `#i-person` | Fluxo clínico completo (6 steps) |
| 2 | Modo Urgência | `#i-bolt` | Decisão rápida, alarmes, cores de risco |
| 3 | Gestor | `#i-trend` | KPIs, auditoria, métricas institucionais |
| 4 | Estudante | `#i-cap` | Passo-a-passo, quiz, dicas pedagógicas |
| 5 | Acadêmico | `#i-book` | Evidência, referências, base teórica |

### Segurança e Medicação no Perfil Profissional:
- Os **9 Certos da Medicação** e as **Metas IPSG (International Patient Safety Goals)** são parte integrante do Step 6 do perfil Padrão (Profissional)
- NÃO são uma seção separada nem um painel isolado
- Fazem parte do raciocínio cognitivo do enfermeiro — safety goals e medication rights são inerentes ao pensamento clínico profissional

## 5. Recursos Adicionais (10 Cards)

Após o fluxo cognitivo (steps 1-6) e a seção "Sobre esta ferramenta" (FAQ + disclaimer), cada calculadora exibe uma grade de 10 cards de recursos adicionais, sempre visíveis.

### Fonte de Dados por Recurso:

| Card | Fonte de Dados | Tipo |
|------|---------------|------|
| Artigos | `evidence.references` + `evidence.foundation` | Link |
| Protocolos | `institutional_protocols` (ANVISA, MS, OMS) | Link |
| Casos Clínicos | `learning.examples` + `clinical_decision_trees` | Link |
| Check-lists | `safety_goals` + `medication_rights` (Excel/PDF) | Download |
| Simulados | Cenários P&R do banco (data-driven) | **Ferramenta completa** |
| Flashcards | NANDA/NIC/NOC/interpretação do banco (data-driven) | **Ferramenta completa** |
| Infográficos | Visualizações geradas dos dados clínicos | Link |
| Guia de Bolso | Resumo condensado (`pocket` dimension) | Link |
| Slides | Material de apresentação gerado do banco | Download |
| Vídeos | Tutoriais e demonstrações externos | Link |

### Simulados e Flashcards são FERRAMENTAS COMPLETAS:
- Não são apenas links/cards — são páginas interativas independentes
- Consomem os mesmos dados da calculadora (NANDA, NIC, NOC, interpretação, segurança)
- Usam `localStorage` para persistência de progresso
- São data-driven: o mesmo JSON da calculadora alimenta os cenários e flashcards

## 6. Hashtags + Ferramentas Relacionadas

### Seção Removida (v1.0.0):
As seguintes seções foram **removidas** da parte inferior das páginas de calculadora:
- ~~Clinical Intelligence Package (CIP)~~ — era um placeholder vazio
- ~~Nurse-PaLM Cognitive Analysis~~ — era um painel separado, agora integrado ao fluxo cognitivo
- ~~Knowledge Graph Links / Recursos Conectados~~ — substituído por hashtags + related tools

### Seção Nova (v2.0.0):
```html
<section class="tool-footer-zone">
  <div class="tool-tags">
    <a href="..." class="tool-tag">#Neonatologia</a>
    <a href="..." class="tool-tag">#Apgar</a>
    <!-- 8-11 hashtags por calculadora -->
  </div>
  <div class="related-tools">
    <h2>Ferramentas relacionadas</h2>
    <div class="related-tools-grid">
      <!-- 6 cards de calculadoras da mesma categoria -->
    </div>
  </div>
</section>
```

### Regras:
- Hashtags: 8-11 por página, incluindo categoria, nome da ferramenta, termos clínicos, NANDA/SAE/Protocolos
- Ferramentas relacionadas: 6 cards de calculadoras da mesma categoria clínica
- Ambos ficam dentro de `<main>`, antes do fechamento, após a seção "Sobre"

## 7. calc-engine-v2.js

**Arquivo**: `js/calc-engine-v2.js`

Motor genérico de calculadoras (evolução do `calc-engine.js`) que lê o JSON embutido na página (`<script id="tool-config">`) e gerencia:

### Funcionalidades:
- **Sincronização de inputs**: Mesmo campo em múltiplos painéis fica sincronizado
- **Cálculo em tempo real**: Recalcula ao mudar qualquer campo
- **2 famílias de fórmula**:
  - `sum` — escalas de escore (Braden, Glasgow, Morse, APGAR)
  - `expression` — cálculo numérico (gotejamento, IMC, insulina)
- **Banner de status**: `#calcStatusBanner` com cor/ícone/título/texto
- **Resultado**: `#calcResultValue` + `#calcResultUnit`
- **Painel Acadêmico**: `[data-aca-value]` mostra valores intermediários
- **Painel Estudante**: `[data-fd-step]` passo-a-passo + badge de risco
- **Painel Urgência**: `#urgResultNum` + `#urgAlarmBadge`
- **Exemplos/presets**: `[data-example]` com `data-values='{"id":valor,...}'`
- **Histórico**: `#calcHistoryList` salva cálculos anteriores
- **Favoritar/Compartilhar**: `#calcFavoriteBtn` / `#calcShareBtn`
- **Revelar Steps 3-6**: Após submit, revela `#calcClinicalFlow` com NANDA/NIC/NOC, Plano, NOC, Segurança

### Contrato HTML:
```html
<script type="application/json" id="tool-config">{...}</script>
<input data-calc-input="fc" type="select">
<div data-formula-box="fc">2</div>
<div data-formula-box="__result__">10</div>
```

## 8. CSS Unificado

| Arquivo | Tamanho | Função |
|---------|---------|--------|
| `css/site-styles.css` | 2.664 linhas | CSS unificado — substitui main.css, calc-tool.css, nurse-palm.css |

### Arquivos Removidos (v2.0.0):
- ~~`css/main.css`~~ (32KB) — consolidado em site-styles.css
- ~~`css/calc-tool.css`~~ (28KB) — consolidado em site-styles.css
- ~~`css/nurse-palm.css`~~ — consolidado em site-styles.css (estilos cognitivos integrados)

### Design System:
- **Paleta azul**: obrigatória para componentes de decisão e interface principal
- **Verde**: restrito exclusivamente a notificações (toasters)
- **Fontes**: Manrope (corpo) + Sora (títulos) via Google Fonts
- **Ícones**: SVG sprite inline (`<symbol>`) + Font Awesome 6.5.2 para ícones complementares
- **Nurse-PaLM**: NÃO é um painel/seção separada — é a lógica integrada às ferramentas. Cada campo, cada card, cada step reflete o pensamento cognitivo do enfermeiro

## 9. Demais Módulos JS

### lang-selector.js
- 30 idiomas com bandeiras
- Popula dropdowns, aplica traduções a `[data-i18n]`
- Persiste em `localStorage`, fallback: idioma → en → pt

### i18n-loader.js
- `fetch("i18n/{lang}.json")` com cache
- API: `window.I18N_LOADER.loadDictionaryWithFallback(lang)`

### partials-loader.js
Carrega partials HTML dinamicamente:
- `partials/header.html` → `#site-header`
- `partials/footer.html` → `#site-footer`
- `partials/accessibility-toolbar.html` → `#site-a11y`
- `partials/cookie-system.html` → cookie banner

### Arquivos JS Removidos (v2.0.0):
- ~~`js/nurse-palm.js`~~ — era um bundle separado do motor cognitivo, agora integrado ao fluxo
- ~~`js/cognitive-ui.js`~~ — era um painel visual separado, removido
- ~~`js/knowledge-graph.js`~~ — era uma seção de links, substituída por related tools

## 10. Responsividade

### Breakpoints:
- **Desktop** (>1024px): grid completo, 2-3 colunas
- **Tablet** (641-1024px): grids adaptativos, `auto-fit` + `minmax`
- **Mobile** (≤640px): tudo em coluna única, tabs com scroll horizontal

### Regras Mobile (≤640px):
```css
.calc-grid, .info-stack, .nnn-grid, .safety-grid → 1 coluna
.learning-track-grid → 2 colunas
.related-tools-grid → 1 coluna
.profile-tabs-bar → scroll horizontal (flex-wrap:nowrap)
.kpi-grid → 2 colunas
.formula-row → flex-wrap com gap reduzido
```

## 11. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-04 | Modules (Simulados, Flashcards, SAE, SBAR) |
| NIFS-700-00 | Nurse-PaLM Architecture (cognitive integration) |
| NIFS-1000-03 | Accessibility (WCAG compliance) |
