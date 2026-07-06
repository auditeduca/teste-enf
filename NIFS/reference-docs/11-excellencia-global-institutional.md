# 11 — Excelência global: institucional, acessibilidade e 100%

Complemento ao [roadmap Nursing OS](10-nursing-os-roadmap.md). Foco em **páginas institucionalizadas por país**, **Accessibility Intelligence Layer** e **15 pilares** para sair de ~90% para referência mundial.

Relacionado: [09-paginas-site-traducao.md](09-paginas-site-traducao.md) · `datasets/content/schemas/regulatory_layer.json`

---

## 1. Maturidade atual vs. meta

| Dimensão | Hoje | Meta 100% |
|----------|------|-----------|
| Arquitetura estratégica (nav + shell + workspace) | **88–92%** | Nursing OS completo |
| Home conteúdo | 8.4/10 | 9.6–9.8 (schema 2026.3) |
| ChromeShell | 9.3/10 | 9.8/10 |
| Institucional pt-BR | ✅ sólido | 70% global + 30% por país |
| Glocal (195 países) | camada definida | Master Data + overlays |

**Próximo salto:** não é mais “páginas” — é **Institutional Pages Globalizadas por País** + **Knowledge Graph** + **Accessibility Intelligence**.

---

## 2. Institucional — regra 70 / 30

| Tipo | % | Exemplos |
|------|---|----------|
| **Global (igual)** | ~70% | Missão/visão global, fundador, processo editorial, metodologia base, IA responsável (princípios), estrutura WCAG |
| **Por país** | ~30% | Reguladores, privacidade local, certificações, licenciamento, SO, benchmarks, mensagem local, contato (fuso/idioma) |

### 2.1 Páginas existentes (`institutional_pages.json`)

| Slug | Arquivo | Localizar por país? |
|------|---------|---------------------|
| `/sobre` | `sobre` | Parcial — bloco `local_message` + agências |
| `/missao` | `missao` | Parcial — `local_priorities[]` |
| `/objetivo` | `objetivo` | Sim — stats (`nurses`, `regulatory_body`) |
| `/acessibilidade` | `acessibilidade` | Sim — leis locais (eMAG, ADA, EAA…) |
| `/contato`, `/fale-conosco` | `contato` | Sim — idioma, SLA, fuso |
| `/mapa-site` | `mapa_site` | Não |
| `/busca` | `busca` | Não (UI traduzida) |

Privacidade e sustentabilidade vivem em `privacy_center.json` e `sustainability_center.json` — mesma regra 70/30.

### 2.2 Páginas faltantes (P1 institucional)

| Slug sugerido | Entidade | Schema scaffold |
|---------------|----------|-----------------|
| `/governanca/ia-responsavel` | ResponsibleAI | `schemas/institutional_pages_v2.json` |
| `/credibilidade/conselho-editorial` | EditorialBoard | idem |
| `/credibilidade/metodologia` | Methodology | idem |
| `/credibilidade/revisao` | EditorialPolicy | idem |
| `/conformidade` | RegulatoryCompliance | integra `regulatory_layer.json` |
| `/seguranca-paciente` (institucional) | PatientSafetyCenter | hub IPSG + NR |
| `/transparencia` | Transparency | status, dados abertos |
| `/status` | PlatformStatus | uptime, incidentes |

### 2.3 Árvore institucional alvo

```
Institucional
├── Sobre · Missão · Objetivo
├── Conselho Editorial · Especialistas · Metodologia · Política Editorial
├── IA Responsável · Privacidade · Acessibilidade · Sustentabilidade
├── Segurança do Paciente · Conformidade Regulatória
├── Transparência · Status da Plataforma
└── Fale Conosco · Mapa do Site · Busca
```

### 2.4 Overlay por país

Padrão de merge (não duplicar JSON inteiro):

```json
{
  "country_code": "US",
  "locale": "en-US",
  "overrides": {
    "sobre.local_message": {
      "title": "Supporting Nurses Across the United States",
      "description": "Evidence-based tools adapted to U.S. nursing standards."
    },
    "objetivo.stats": {
      "nurses": "5000000+",
      "regulatory_body": "ANA / State Boards"
    },
    "privacy_framework": { "laws": ["HIPAA", "CCPA"] },
    "accessibility.local_laws": ["ADA", "Section 508"]
  },
  "agencies": ["FDA", "CDC", "Joint Commission", "NCLEX"]
}
```

Arquivo: `datasets/content/schemas/institutional-global-overlay.json`  
Loader futuro: `merge_institutional(country_code)` sobre `institutional_pages.json` + overlay.

---

## 3. Personalização por país (10 camadas)

Resumo — detalhe em [doc 10 §4](10-nursing-os-roadmap.md#4-personalização-por-país-195-países).

| # | Camada | Personalizar |
|---|--------|--------------|
| 1 | Global | Anatomia, farmacologia base, escalas internacionais, NANDA/NIC/NOC, CID |
| 2 | Idioma | UI, artigos, simulados, IA (~20–25 idiomas) |
| 3 | Regulação | COREN/NCLEX/NMC, ANVISA/FDA/EMA |
| 4 | Medicamentos | Nomes, concentrações, disponibilidade |
| 5 | Protocolos | Global → adaptação país → instituição |
| 6 | Carreira | Concursos, licenciamento, certificações |
| 7 | Seg. paciente | IPSG global + Notivisa vs Joint Commission |
| 8 | Métricas | Benchmarks unidade/hospital/país/global |
| 9 | Cultural | Casos clínicos, simulados |
| 10 | Institucional B2B | Protocolos e KPIs do hospital |

**Master Data (modelar primeiro):** `Country`, `Language`, `RegulatoryAgency`, `ProfessionalRegistry`, `MedicationCatalog`, `ClinicalGuideline`, `Certification`, `OccupationalSafetyRule`, `PatientSafetyRule`, `BenchmarkDataset`.

---

## 4. Quinze pilares para ~100% de excelência

Prioridade sugerida (impacto × diferenciação):

| P | Pilar | Descrição | Depende de |
|---|-------|-----------|------------|
| 1 | **Global Knowledge Graph** | NANDA ↔ NIC ↔ NOC ↔ escalas ↔ protocolos ↔ casos ↔ competências | Master Data |
| 2 | **Clinical Decision Pathways** | Fluxos visuais (sepse, AVC, PCR…) | Graph + protocolos |
| 3 | **Digital Twin profissional** | Skill gap 82% UTI Adulto | Competency Center |
| 4 | **Adaptive Learning Engine** | O que/quando/como estudar | Workspace + analytics |
| 5 | **Career Intelligence (Career OS)** | ATS + lacunas + certificações + mercado | Regulatory + competências |
| 6 | **Regulatory Intelligence** | Alertas quando COFEN/FDA/NMC mudam | regulatory_layer + notifications |
| 7 | **Institutional Intelligence** | Matriz competências 500 enfermeiros | institutional_profile |
| 8 | **Guidelines Center** | OMS, NICE, CDC, COFEN comparados | Graph + regulatory |
| 9 | **Benchmark mundial** | Protocolos/segurança por país | BenchmarkDataset |
| 10 | **Nursing Observatory** | Déficit, burnout, ESG, IPSG global | Analytics agregado |
| 11 | **AI Studio** | Agentes/fluxos institucionais no-code | multi_agent_hub |
| 12 | **Evidence Engine** | Nível evidência + GRADE + data revisão | Editorial + metodologia |
| 13 | **Workspace Graph** | Competências ↔ certificados ↔ conteúdos (grafo) | workspace.json |
| 14 | **Safety OS** (domínio) | IPSG, near miss, cultura justa, med. safety | patient_safety_center |
| 15 | **Digital Public Good** | Calculadoras/escalas/glossário abertos; premium no resto | Modelo freemium |

### Arquitetura alvo 100/100

```
Nursing OS Global Platform
├── Clinical OS · Education OS · Career OS · Management OS
├── Safety OS · Regulatory OS · Research OS · Institutional OS
├── Multi-Agent AI · Competency Graph · Knowledge Graph
├── Regulatory Layer · Adaptive Learning · Evidence Engine
├── Global Observatory · AI Studio
└── Accessibility Intelligence Layer
```

---

## 5. Accessibility Intelligence Layer

**Não traduzir apenas** — localizar culturalmente, tecnologicamente e regulatoriamente.

### 5.1 Arquitetura

```
Accessibility Intelligence Layer
├── WCAG Core (2.2 AA — universal)
├── Country Profiles (BR, US, JP, CN, KR, SA, EU…)
├── Language Engine
├── Assistive Technology Map (NVDA, JAWS, VLibras, iFlytek…)
├── Cultural Icon Library
├── Accessibility Profiles (visual, elderly, student, clinical)
├── AI Accessibility Assistant
└── User Accessibility Memory (prefs persistentes)
```

Schema: `datasets/content/schemas/accessibility-localization.json`

### 5.2 Perfis de acessibilidade (chrome `preferences_modal`)

| ID | Nome | Features |
|----|------|----------|
| `visual` | Baixa visão | texto grande, alto contraste, leitor de tela |
| `elderly` | Modo facilidade | botões grandes, navegação simples, voz |
| `student` | Modo estudo | foco, leitura assistida |
| `clinical` | Modo assistência | ações rápidas, contraste emergência |

### 5.3 Detecção automática (meta)

Entrada: `country` + `locale` + `device` + `profile` + `a11y_prefs` → monta barra/recursos ideais.

Integração: estender `chrome_shell.json` → `accessibility_bar` com `schema_ref: accessibility-localization.json`.

### 5.4 Legislação local por página

| País | Privacidade | Acessibilidade |
|------|-------------|----------------|
| BR | LGPD | eMAG, LBI |
| EU / DE | GDPR | European Accessibility Act |
| US | HIPAA, CCPA | ADA, Section 508 |
| CA | PIPEDA | ACA |
| JP | APPI | Universal Design |
| SG | PDPA | — |

---

## 6. Fases de implementação (institucional + a11y)

### Fase E — Institucional global

1. Scaffolds `institutional_pages_v2.json` + `institutional-global-overlay.json`
2. Páginas novas: IA Responsável, Metodologia, Editorial (render em `institutional_lib.py`)
3. Merge overlay por `country_code` no gerador
4. Traduzir overlays (não páginas inteiras) — ~30% por país

### Fase F — Accessibility Intelligence

1. Carregar `accessibility-localization.json` em `chrome_content_lib.py`
2. Perfis em `preferences_modal`
3. Ícones culturais por locale (CN, JP, AR RTL)
4. Assistente ♿ “Como posso facilitar sua experiência?”

### Fase G — Excelência (pilares 1–5)

Knowledge Graph → Pathways → Competency Twin → Adaptive Learning → Career OS

---

## 7. Arquivos e status

| Arquivo | Status |
|---------|--------|
| `datasets/content/institutional_pages.json` | ✅ pt-BR 2026.1 (8 páginas) |
| `datasets/content/schemas/institutional_pages_v2.json` | 📋 novas páginas (stub) |
| `datasets/content/schemas/institutional-global-overlay.json` | 📋 piloto BR, US, UK, DE |
| `datasets/content/schemas/accessibility-localization.json` | 📋 perfis + países |
| `datasets/content/schemas/regulatory_layer.json` | 📋 BR, US |
| `docs/10-nursing-os-roadmap.md` | ✅ home + chrome + glocal |
| **Este documento** | ✅ institucional + 100% + a11y |

---

## 8. i18n institucional

| Prioridade | Conteúdo |
|------------|----------|
| P0 | `institutional_pages.json` (global pt-BR fonte) |
| P1 | Overlays por país (JSON pequenos) |
| P2 | `privacy_center.json`, `sustainability_center.json` por framework legal |
| P3 | Tradução completa UI institucional (~25 idiomas) |

Idiomas home pendentes: [09 §6.1](09-paginas-site-traducao.md).

---

## 9. Checklist excelência

- [ ] Home 2026.3 renderizada
- [ ] 8 páginas institucionais novas publicadas
- [ ] Overlay BR + US + UK funcional
- [ ] Privacy por framework (LGPD/GDPR/HIPAA)
- [ ] Accessibility profiles no modal
- [ ] Knowledge Graph MVP (1 escala → 5 entidades)
- [ ] Command Palette indexa institucional
- [ ] Evidence badge em artigos/protocolos
