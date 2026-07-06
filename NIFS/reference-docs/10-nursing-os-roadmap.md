# 10 — Nursing OS: roadmap de produto (2026)

Evolução de **portal de calculadoras** para **Nursing Digital Ecosystem** — plataforma operacional global com personalização glocal (idioma + regulação).

Relacionado: [09-paginas-site-traducao.md](09-paginas-site-traducao.md) · [06-i18n-seo.md](06-i18n-seo.md) · [11-excellencia-global-institutional.md](11-excellencia-global-institutional.md)

---

## 1. Avaliação estratégica (baseline)

| Área | Nota | Meta |
|------|------|------|
| Arquitetura da informação | 9.0 | 9.6+ |
| UX/UI | 8.5 | 9.5+ |
| Conteúdo | 8.5 | 9.5+ |
| SEO | 8.0 | 9.0+ |
| Autoridade científica | 7.5 | 9.0+ |
| Conversão / retenção | 7.0 | 9.0+ |
| Sustentabilidade digital | 9.5 | manter |
| ChromeShell (navegação) | 9.3 | 9.8+ |
| **Home (schema atual 2026.1)** | **8.4** | **9.6–9.8** |

**Problema central:** a home responde *“o que existe?”*, mas ainda não responde *“por que voltar todo dia?”*.

**Salto de produto:** personalização por perfil, feed clínico, hub de conhecimento, competências, IA contextual, governança visível e camada regulatória por país.

---

## 2. Home — schema 2026.3.0

### 2.1 O que muda

| Removido (breaking) | Substituído por |
|---------------------|-----------------|
| `daily_tip` | `clinical_feed` |
| `education_block` | `knowledge_hub` |

### 2.2 Novas seções (12 blocos)

| Seção JSON | Objetivo |
|------------|----------|
| `profile_selector` | Personalização por perfil (estudante → instituição) |
| `nursing_os_map` | Mapa orbital do ecossistema |
| `knowledge_hub` | Trilha Artigo → Flashcard → Quiz → Caso → Certificado |
| `clinical_cases` | Treinamento por especialidade |
| `competency_track` | Desenvolvimento profissional |
| `ai_assistant` | Assistente clínico com supervisão humana |
| `patient_safety_center` | IPSG, eventos adversos, near miss |
| `occupational_health` | NR-01, NR-32, PGR, GRO, burnout |
| `impact_dashboard` | Métricas agregadas da plataforma |
| `sustainability_block` | Impacto ambiental digital |
| `governance_center` | Privacidade, IA, credibilidade científica |
| `cta_final` | Conversão final |

### 2.3 Ordem ideal (`page_sections_order`)

```
hero → search → profile_selector → featured → nursing_os_map →
knowledge_hub → clinical_cases → competency_track → ai_assistant →
management_block → patient_safety_center → occupational_health →
impact_dashboard → global_platform → sustainability_block →
governance_center → cta_final
```

### 2.4 Arquivos de referência

| Arquivo | Status | Uso |
|---------|--------|-----|
| `datasets/content/home_page.json` | **2026.1.0 (ativo no build)** | Fonte do gerador atual |
| `datasets/content/schemas/home_page.2026.3.pt-BR.json` | **Alvo** | Schema completo pt-BR |
| `datasets/content/schemas/home_page.2026.3.en.json` | **Alvo** | Schema completo en (href localizados) |
| `datasets/by-locale/{locale}/home_page.json` | Parcial (7 locales, schema antigo) | Partições i18n |

### 2.5 Pendência de implementação (P0 home)

- [ ] Estender `scripts/website_lib.py` → `render_home_page()` para renderizar seções 2026.3
- [ ] Estender `website/assets/css/home.css` (orbital map, feed, dashboards)
- [ ] Estender `website/assets/js/site.js` (profile selector na home, clinical feed)
- [ ] Promover `home_page.2026.3.pt-BR.json` → `home_page.json` após renderer pronto
- [ ] Gravar traduções chat → `datasets/by-locale/` (ver [09 §6.1](09-paginas-site-traducao.md))

---

## 3. ChromeShell — evolução 2026.2

**Nota atual:** 9.3/10 · **Meta:** 9.8/10

### 3.1 Pontos fortes (manter)

- Barra de acessibilidade (WCAG+, VLibras, prefs persistentes)
- Onboarding de perfil
- Locale + país + região WHO
- Cesta de downloads / offline
- Governança (cookies LGPD, preferências)

### 3.2 Prioridades P0 (shell)

| # | Recurso | Schema proposto | Atalho |
|---|---------|-----------------|--------|
| 1 | Command Palette global | `command_palette.json` | `Ctrl+K` |
| 2 | Meu Nursing OS (workspace) | `workspace.json` | `/me` |
| 3 | Notification Center | `notifications.json` | sino no header |
| 4 | Multi-Agent Hub | `multi_agent_hub.json` | `Ctrl+J` |
| 5 | Perfil institucional | `institutional_profile.json` | B2B |
| 6 | Camada regulatória por país | `regulatory_layer.json` | pós-seleção de país |
| 7 | Centro de competências (shell) | `competency_center.json` | integrado ao workspace |

### 3.3 Ajustes UX recomendados

- Consolidar A+/A−/tema em **Preferências**; header mantém só toggle rápido 🌙
- Selo discreto **195+ países** junto ao logotipo
- Expandir perfis onboarding: + urgência, docente, pesquisador, instituição (alinhar com `profile_selector` da home)

### 3.4 Arquivos propostos

| Arquivo | Entidade | Status |
|---------|----------|--------|
| `datasets/content/schemas/navigation-v2.json` | ChromeNavigation v2 | 📋 scaffold |
| `datasets/content/schemas/chromeshell-enhanced.json` | ChromeShell 2026.2 | 📋 scaffold |
| `datasets/content/schemas/command_palette.json` | CommandPalette | 📋 scaffold |
| `datasets/content/schemas/workspace.json` | UserWorkspace | 📋 scaffold |
| `datasets/content/schemas/notifications.json` | NotificationCenter | 📋 scaffold |
| `datasets/content/schemas/multi_agent_hub.json` | MultiAgentHub | 📋 scaffold |
| `datasets/content/schemas/institutional_profile.json` | InstitutionalAccount | 📋 scaffold |
| `datasets/content/schemas/regulatory_layer.json` | RegulatoryLayer | 📋 scaffold |
| `datasets/content/schemas/competency_center.json` | CompetencyCenter | 📋 scaffold |

Scaffolds em `datasets/content/schemas/` — estrutura mínima para validação e implementação incremental. **Não** carregados pelo build até integração em `chrome_content_lib.py`.

### 3.5 Navegação V2 (domínios)

Substituir portal por **fluxos de trabalho**:

```
Início
Assistência      → calculadoras, escalas, protocolos, medicamentos, casos, árvores
Educação         → trilhas, flashcards, quiz, simulados, biblioteca, certificações
Segurança        → IPSG, eventos adversos, NR-01/32, burnout
Gestão           → KPIs, dashboards, compliance, ESG
Carreira         → ATS, competências, empregos
Comunidade       → fórum, especialistas (fase 2 — moderar com cuidado)
Sobre            → institucional, editorial, governança
```

**Fase 3 (futuro):** domínio **Pesquisa** (evidências, GRADE, revisões sistemáticas).

---

## 4. Personalização por país (195 países)

**Regra de ouro:** não personalizar tudo — usar camadas.

| Camada | % esforço | Personalizar | Não personalizar |
|--------|-----------|--------------|------------------|
| 1 Global | ~80% | — | Anatomia, farmacologia base, escalas internacionais, NANDA/NIC/NOC, CID, cálculos |
| 2 Idioma | ~15% | UI, artigos, simulados, IA | Estrutura JSON, bindings |
| 3 Regulação | ~3% | COREN/NCLEX/NMC, ANVISA/FDA/EMA, NR/OSHA | Conceitos clínicos universais |
| 4 Medicamentos | ~1% | Nomes comerciais, concentrações, disponibilidade | Mecanismo de ação |
| 5 Protocolos | ~0.5% | Adaptação nacional sobre protocolo global | Protocolo global base |
| 6 Carreira | local | Concursos, licenciamento, certificações | Competências globais |
| 7 Seg. paciente | local | Notivisa vs Joint Commission, reporte | IPSG, JCI conceitos |
| 8 Métricas | local | Benchmarks país/estado | Definições de indicador |
| 9 Cultural | leve | Casos clínicos, simulados | — |
| 10 Institucional | B2B | Protocolos/dash do hospital | — |

### 4.1 Master Data (modelar primeiro)

Entidades núcleo antes de escalar locales:

```
Country · Language · Currency
RegulatoryAgency · ProfessionalRegistry
MedicationCatalog · ClinicalGuideline
Certification · OccupationalSafetyRule
PatientSafetyRule · BenchmarkDataset
```

Todo módulo (Assistência, Educação, Gestão, IA, Competências) **consome** essas entidades — evita multiplicar manutenção × 195.

### 4.2 Integração com locale existente

| Hoje | Próximo passo |
|------|---------------|
| `locale-options.json` (195 países, WHO) | + `regulatory_layer.countries[]` por `country_code` |
| `chrome_shell.json` → `locale_panels` | + painel “Regulação local” após seleção |
| `seo_lib.LOCALES` (7) | Expandir conforme `by-locale/` maduro |

---

## 5. Diferenciais futuros (pós-V2)

| Módulo | Descrição | Prioridade |
|--------|-----------|------------|
| Medication Intelligence Layer | ATC, LASA, alta vigilância, Beers | Alta |
| Clinical Pathways | Fluxos visuais (sepse, AVC, PCR…) | Alta |
| Nursing Knowledge Graph | NANDA ↔ NIC ↔ NOC ↔ escalas ↔ protocolos | Muito alta |
| Clinical Data Hub | Benchmarks globais de indicadores | Média |
| Nursing Research OS | GRADE, revisões, diretrizes | Média |

---

## 6. Fases de implementação

### Fase A — Conteúdo (sem quebrar build)

1. Schemas 2026.3 em `datasets/content/schemas/`
2. Traduções home → `datasets/by-locale/` (1 locale/vez)
3. Documentação i18n ([09 §6.1](09-paginas-site-traducao.md))

### Fase B — Home renderer

1. `render_home_page()` + CSS + JS para seções 2026.3
2. Promover schema pt-BR
3. Regenerar e validar a11y

### Fase C — Chrome V2

1. `navigation-v2.json` → `chrome_navigation.json` (migração gradual)
2. Command palette + workspace (JS)
3. Notifications + multi-agent (API/mock)

### Fase D — Glocal

1. `regulatory_layer.json` + filtros por país
2. Perfil institucional
3. Master data mínimo (BR + US piloto)

---

## 7. Idiomas pendentes (home 2026.3)

Ver tabela completa em [09-paginas-site-traducao.md §6.1](09-paginas-site-traducao.md).

**Resumo:** 18 JSONs gerados (chat) · **35 pendentes** · próximo: **ro-RO**.

---

## 8. Checklist de validação

- [ ] Schema 2026.3 valida (`python -m json.tool`)
- [ ] Renderer emite todas as seções de `page_sections_order`
- [ ] Profile selector persiste (`ce-user-profile-v1`)
- [ ] Clinical feed carrega via CMS/API mock
- [ ] Chrome V2 não regrediu a11y (barra + skip links)
- [ ] hreflang/canonical por locale após tradução real
