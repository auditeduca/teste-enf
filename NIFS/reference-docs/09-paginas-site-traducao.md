# 09 — Página inicial, institucionais, modulares e tradução

Guia prático de arquivos e fluxos para manutenção das páginas públicas do site estático.

**Alicerce reorganizado (2026-06):** ver [`datasets/content/README.md`](../datasets/content/README.md) e `scripts/content_paths.py`.

Relacionado: [04-geracao-site.md](04-geracao-site.md) · [06-i18n-seo.md](06-i18n-seo.md)

---

## 1. Página inicial (home)

| Camada | Arquivo | Função |
|--------|---------|--------|
| **Conteúdo** | `datasets/content/site/home_page.json` | Hero, busca, categorias, destaques, blocos educação/gestão, SEO, ecossistema |
| **Dicas do dia** | `datasets/content/editorial/daily_tips.json` | Card rotativo no hero |
| **Gerador** | `scripts/generate_website_pt.py` | Emite `website/pt/index.html` via `render_home_page()` |
| **Render** | `scripts/website_lib.py` → `render_home_page()` | Monta HTML da home |
| **Estilo** | `website/assets/css/home.css` | Hero, busca, categorias, pillar, badge simulados |
| **JS** | `website/assets/js/site.js` | `initHomeSearch()`, dicas, perfil de usuário na home |
| **Perfil** | `website/assets/js/user-profile.js` | Personalização por perfil (estudante, profissional, …) |
| **Marketing** | `datasets/content/chrome/marketing_config.json` + `website/assets/js/marketing.js` | GA4/AdSense com consentimento LGPD |

### Regenerar só a home

```bash
python scripts/generate_website_pt.py --pt-only --no-zip
```

### Editar textos da home

1. Altere `datasets/content/site/home_page.json` (seção `hero`, `featured`, `education_block`, `seo`, etc.).
2. Regenere o site.
3. Valide em `website/pt/index.html`.

---

## 2. Páginas institucionais

| Tipo | Dataset / origem | Render |
|------|------------------|--------|
| Premium (missão, privacidade, sustentabilidade, …) | `datasets/content/site/institutional_pages.json`, `privacy_center.json`, `sustainability_center.json` | `institutional_lib.py` |
| Hubs simples (sobre, objetivo, acessibilidade, …) | `scripts/institutional_lib.py` + `INST` em `generate_website_pt.py` | `render_institutional()` |
| Contato / busca | `institutional_pages.json` | `render_contact_page()`, `render_search_page()` |
| Mapa do site | gerado | `render_sitemap_page()` |

### Arquivos-chave

```
datasets/content/site/institutional_pages.json   # missao, objetivo, sobre, acessibilidade, contato, busca
datasets/content/site/privacy_center.json        # /privacidade
datasets/content/site/sustainability_center.json # /sustentabilidade
scripts/institutional_lib.py                # templates premium + corpo institucional
website/assets/css/institutional.css        # layout das páginas ouro
```

### Slugs institucionais (sem onboarding de perfil)

Lista em `website/assets/data/user-profile-config.json` → `institutional_slugs`.

### Rodapé e navegação

```
datasets/content/chrome/chrome_navigation.json  # menu principal, footer links, mega-menu aside
datasets/content/chrome/chrome_shell.json       # header, footer, a11y, cookies, modais, marca
scripts/chrome_content_lib.py            # loader dos JSON acima
scripts/menu_data.py                     # reexporta chrome_navigation (compatibilidade)
scripts/website_lib.py                   # render_header(), render_footer()
scripts/chrome_lib.py                    # barra a11y, cookies, preferências, FABs
website/assets/partials/                 # header.html, footer.html (exportados no build)
```

---

## 3. Páginas modulares (hubs e detalhe)

| Módulo | Hub (listagem) | Detalhe | Lib |
|--------|----------------|---------|-----|
| Ferramentas / escalas | `/ferramentas`, `/calculadoras`, `/escalas` | `/ferramentas/{slug}` | `tool_lib.py`, `hub_lib.py` |
| Protocolos | `/protocolos` | `/protocolos/{slug}` | `protocol_lib.py` |
| Medicamentos | `/medicamentos` | `/medicamentos/{slug}` | `medication_lib.py` |
| Simulados / quiz | `/simulados`, `/quiz` | `/simulados/{slug}` | `hub_lib.py`, `simulation_lib.py` |
| Artigos / biblioteca | `/artigos`, `/biblioteca` | `/artigos/{slug}` | `hub_lib.py`, `article_lib.py` |
| NANDA/NIC/NOC | `/nanda`, `/nic`, `/noc` | — | `templates_lib.py` (client-side) |
| Trilhas / flashcards | `/trilhas`, `/flashcards` | parcial | `hub_lib.py` |
| Empregos / cursos | `/empregos`, `/cursos` | — | `hub_lib.py` + scrape datasets |
| Calculadoras trabalhistas | `/calculadoras-trabalhistas` | sub-slugs | `labor_lib.py` |
| SBAR / currículo | `/sbar`, `/curriculo` | wizards | `sbar_lib.py`, `cv_lib.py` |

### Datasets de suporte

```
datasets/clinical/clinical_tools_catalog.json   # 100 ferramentas
datasets/content/hubs/hub_orchestrator.json          # layout dos hubs
datasets/content/tools/tool_templates.json            # templates de UI
datasets/content/tools/calculator_scale_options.json  # opções de escalas
scripts/hub_lib.py                              # build_tool_items, build_simulado_items, render_hub_page
scripts/generate_website_pt.py                    # orquestra emissão de todas as rotas
```

### Chrome compartilhado (todas as páginas)

```
website/assets/js/chrome-loader.js      # injeta header/footer
website/assets/js/chrome-templates.js   # bundle gerado no build
website/assets/css/chrome.css           # header, mega-menu, footer, cookies
website/assets/css/layout.css           # shell, ads, utilitários
```

---

## 4. Mega-menu por região (idioma/país)

| Arquivo | Papel |
|---------|--------|
| `scripts/chrome_lib.py` | HTML do painel 3 colunas (Destaques · Por região · Aside) |
| `website/assets/data/locale-options.json` | 195 países + `who_region` (AMRO, EURO, AFRO, EMRO, SEARO, WPRO) |
| `website/assets/js/site.js` | `populateLocaleGrids()`, `initLocaleMega()` |
| `scripts/menu_data.py` | `MEGA_POPULAR_LOCALES`, destaques do aside do nav |

**Regiões WHO usadas nos dados:** `AMRO`, `EURO`, `AFRO`, `EMRO`, `SEARO`, `WPRO` (não abreviar para AMR/EUR).

Imagem do aside: substitua `website/assets/images/homepage-hero.webp` ou adicione `locale-world-map.webp` e aponte em `chrome_lib.py`.

---

## 5. Perfil do usuário (persistência)

| Chave localStorage | Conteúdo |
|--------------------|----------|
| `ce-user-profile-v1` | Perfil escolhido (`estudante`, `profissional`, …) |
| `ce-user-profile-onboarding-v1` | `completed` após primeira escolha |
| `ce-site-prefs-v1` | Downloads, offline, espelho do perfil |

| Arquivo | Função |
|---------|--------|
| `website/assets/js/user-profile.js` | Salvar/restaurar perfil, modal onboarding |
| `website/assets/data/user-profile-config.json` | Definição dos 4 perfis e slugs institucionais |
| `scripts/chrome_lib.py` | HTML do modal no footer partial |

O modal **não** deve reaparecer após refresh se `ce-user-profile-v1` ou `ce-user-profile-onboarding-v1` existir.

---

## 6. Tradução (i18n)

### Estado atual

- **7 locales no site:** pt-BR (raiz), en, es, fr, de, it, ja — ver `scripts/seo_lib.py` → `LOCALES`.
- **Build:** pt-BR + 6 locales re-renderizam a home via `render_home_page()` quando `i18n_status: translated` e schema **2026.3.0**; demais páginas ainda via `localize_html()` (shell i18n, corpo pt-BR).
- **Dataset NKOS:** `datasets/content/i18n/translations.json` (+ shards em `i18n/translations.shards/`) — ~160k registros para integração futura (P1).

### 6.1 Home — `home_page.json` (schema 2026.3.0)

> Roadmap completo (home, chrome V2, camadas por país, master data): **[10-nursing-os-roadmap.md](10-nursing-os-roadmap.md)**  
> Schemas de referência: `datasets/content/schemas/` · manifest: `schemas/manifest.json`

Tradução manual do conteúdo da página inicial, **um locale por vez**, mantendo a estrutura JSON e traduzindo apenas strings visíveis ao usuário.

| Campo | Regra |
|-------|--------|
| `locale` | Código BCP-47 do idioma alvo (ex.: `ro-RO`) |
| `schema_version`, `entity`, `binding`, `tool_code`, `code`, `icon`, cores, números | **Não alterar** |
| `href` | Manter slugs atuais (`/ferramentas`, `/calculadoras`, …) até roteamento i18n por locale |
| `schema_changelog[].summary` | Traduzir (texto descritivo) |
| Destino no repo | `datasets/by-locale/{locale}/home_page.json` (ex.: `datasets/by-locale/pl-PL/home_page.json`) |
| Fonte | JSON pt-BR schema **2026.3.0** (hero, `profile_selector`, `nursing_os_map`, `knowledge_hub`, `clinical_feed`, … — sem `daily_tip` / `education_block`) |

#### No build ativo (schema 2026.3.0 + renderer)

| Locale | Arquivo | Build | Qualidade |
|--------|---------|-------|-----------|
| pt-BR | `by-locale/pt-BR/home_page.json` | ✅ raiz `/` | completo |
| en | `by-locale/en/home_page.json` | ✅ `/en/` | completo (2026.1 migrado + seções novas) |
| es, fr, de, it, ja | `by-locale/{locale}/home_page.json` | ✅ | hero/search + seções 2026.3; corpo legado parcial |

Scripts: `scripts/upgrade_locale_home_2026_3.py` · bundles: `scripts/locale_home_2026_3_bundles.py`

#### Gravados em `by-locale/` — fora do build (7 locales ativos + reserva)

| Locale | Arquivo | Notas |
|--------|---------|-------|
| ro-RO | `by-locale/ro-RO/home_page.json` | ✅ 2026.3 — adicionar a `seo_lib.LOCALES` para publicar |
| el-GR | `by-locale/el-GR/home_page.json` | ✅ 2026.3 completo (grego) |
| uk-UA | `by-locale/uk-UA/home_page.json` | ✅ 2026.3 (sessão de tradução) |
| cs-CZ | `by-locale/cs-CZ/home_page.json` | ✅ 2026.3 (tcheco) |
| pl-PL, nl-NL | `by-locale/{pl-PL,nl-NL}/` | ✅ 2026.3 |
| ar, zh-CN, hi-IN, ru-RU, ko-KR, tr-TR, id-ID, vi-VN, th-TH | `by-locale/{locale}/` | ✅ 2026.3 gravados (`generate_pending_locale_homes.py`) |

#### Concluídos na sessão de chat — todos gravados

Os 11 locales abaixo foram gerados via `scripts/generate_pending_locale_homes.py` (não estavam extraíveis do transcript):

| Locale | Idioma |
|--------|--------|
| `ar` | Árabe |
| `zh-CN` | Chinês simplificado |
| `hi-IN` | Hindi |
| `ru-RU` | Russo |
| `ko-KR` | Coreano |
| `tr-TR` | Turco |
| `id-ID` | Indonésio |
| `vi-VN` | Vietnamita |
| `pl-PL` | Polonês |
| `nl-NL` | Holandês |
| `th-TH` | Tailandês |

> **Nota:** `en`, `es`, `fr`, `de`, `it`, `ja` estão em **2026.3.0** no build ativo (`upgrade_locale_home_2026_3.py`).

#### Pendentes — Tier 3 (cobertura quase universal)

Próximo na fila: **Húngaro (`hu-HU`)**. Tier 3: ro-RO, el-GR, cs-CZ concluídos; 11 locales base gravados.

| # | Idioma | Locale sugerido | Status |
|---|--------|-----------------|--------|
| 19 | Romeno | `ro-RO` | ✅ gravado |
| 20 | Grego | `el-GR` | ✅ gravado |
| 21 | Tcheco | `cs-CZ` | ✅ gravado |
| 22 | Húngaro | `hu-HU` | ⏳ pendente |
| 23 | Sueco | `sv-SE` | ⏳ pendente |
| 24 | Dinamarquês | `da-DK` | ⏳ pendente |
| 25 | Norueguês | `no-NO` | ⏳ pendente |
| 26 | Finlandês | `fi-FI` | ⏳ pendente |
| 27 | Hebraico | `he-IL` | ⏳ pendente |
| 28 | Malaio | `ms-MY` | ⏳ pendente |
| 29 | Filipino (Tagalog) | `fil-PH` | ⏳ pendente |
| 30 | Bengali | `bn-BD` | ⏳ pendente |
| 31 | Urdu | `ur-PK` | ⏳ pendente |
| 32 | Persa (Farsi) | `fa-IR` | ⏳ pendente |
| 33 | Suaíli (Swahili) | `sw-KE` | ⏳ pendente |

#### Pendentes — Tier 4 (mercados regionais)

| # | Idioma | Locale sugerido | Status |
|---|--------|-----------------|--------|
| 34 | Tamil | `ta-IN` | ⏳ pendente |
| 35 | Telugu | `te-IN` | ⏳ pendente |
| 36 | Marathi | `mr-IN` | ⏳ pendente |
| 37 | Gujarati | `gu-IN` | ⏳ pendente |
| 38 | Punjabi | `pa-IN` | ⏳ pendente |
| 39 | Kannada | `kn-IN` | ⏳ pendente |
| 40 | Malayalam | `ml-IN` | ⏳ pendente |
| 41 | Nepali | `ne-NP` | ⏳ pendente |
| 42 | Sinhala | `si-LK` | ⏳ pendente |
| 43 | Khmer | `km-KH` | ⏳ pendente |
| 44 | Laosiano | `lo-LA` | ⏳ pendente |
| 45 | Birmanês | `my-MM` | ⏳ pendente |
| 46 | Mongol | `mn-MN` | ⏳ pendente |
| 47 | Georgiano | `ka-GE` | ⏳ pendente |
| 48 | Armênio | `hy-AM` | ⏳ pendente |
| 49 | Azerbaijano | `az-AZ` | ⏳ pendente |
| 50 | Cazaque | `kk-KZ` | ⏳ pendente |
| 51 | Uzbeque | `uz-UZ` | ⏳ pendente |
| 52 | Quirguiz | `ky-KG` | ⏳ pendente |
| 53 | Tajique | `tg-TJ` | ⏳ pendente |

**Resumo:** 18 concluídos (chat) · **35 pendentes** (Tier 3: 15 · Tier 4: 20) · 1 fonte pt-BR.

#### Outros conteúdos i18n (fora da home)

| Arquivo | Locale | Status |
|---------|--------|--------|
| `datasets/content/chrome/chrome_shell.json` | pt-BR | ✅ fonte (header, footer, a11y, cookies) |
| `datasets/content/chrome/chrome_navigation.json` | pt-BR | ✅ fonte (nav, mega-menu, footer links) |
| `datasets/content/site/institutional_pages.json` | pt-BR | ✅ 8 páginas · overlay por país 📋 [doc 11](11-excellencia-global-institutional.md) |
| `datasets/content/site/institutional_pages.json` | overlays | 📋 `schemas/institutional-global-overlay.json` (BR, US, GB, DE) |
| `datasets/content/editorial/daily_tips.json` | pt-BR | ⏳ substituído por `clinical_feed` na home 2026.3 |

#### Fluxo recomendado (um idioma por vez)

1. Traduzir JSON pt-BR 2026.3.0 → salvar em `datasets/by-locale/{locale}/home_page.json`.
2. Validar JSON (`python -m json.tool datasets/by-locale/{locale}/home_page.json`).
3. Repetir para chrome (`chrome_shell.json`, `chrome_navigation.json`) quando disponíveis por locale.
4. Integrar loader no gerador (P1) — **home ativa** via `locale_content_lib`; chrome/institucional quando existirem em `by-locale/`.
5. Regenerar: `python scripts/generate_website_pt.py --pt-only --no-zip`.

### Como gerar locales hoje

```bash
python scripts/generate_website_pt.py
# Sem --pt-only → gera pt/ + en/, es/, … + sitemaps hreflang
```

### Pipeline de tradução real (P1 — pendente)

1. **Fonte:** registros em `translations.json` com `translation_code`, `target_locale`, campos traduzidos por entidade.
2. **Gerador:** estender `generate_website_pt.py` ou criar passo pós-`localize_html` que substitui blocos marcados (`data-i18n-key`) ou injeta HTML por locale.
3. **SEO:** `post_build_seo.py` / `seo_lib.py` já emitem hreflang e sitemaps — manter canonical por locale.
4. **API admin:** `GET /api/translations/summary` em `scripts/nkp_api.py` para monitorar cobertura.

### Conteúdo editável para tradução manual (curto prazo)

| Prioridade | Arquivo |
|------------|---------|
| Home | `datasets/content/site/home_page.json` |
| Institucional | `datasets/content/site/institutional_pages.json` |
| SEO por rota | `datasets/metadata/seo_metadata.json` (gerador) |
| Menu/rodapé | `datasets/content/chrome/` |
| Hubs | `datasets/content/hubs/` |

### Comandos úteis

```bash
# Build rápido só pt-BR
python scripts/generate_website_pt.py --pt-only --no-zip

# Exportar partials do chrome (header/footer)
python scripts/generate_website_pt.py --pt-only --no-zip
# (export_chrome_partials roda no final do generate)

# Validar NKOS + site
python scripts/run_full_audit.py --skip-a11y
```

---

## 7. Checklist pós-alteração

- [ ] Editar dataset ou script Python
- [ ] `python scripts/generate_website_pt.py --pt-only --no-zip`
- [ ] Testar home, uma institucional, um hub e uma ferramenta
- [ ] Mega-menu idioma: coluna **Por região** populada
- [ ] Perfil: escolher perfil → F5 → modal não reaparece
- [ ] Cookies: analytics/marketing só após consentimento
