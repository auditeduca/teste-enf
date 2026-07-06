# NKOS v5 — Auditoria Final de Conformidade
**Data:** 2026-07-06 05:05 (America/Sao_Paulo)
**Total de páginas:** 1.084
**Dimensões auditadas:** 42
**Conformidade geral:** 100.0%
**Páginas 100% conformes:** 1.084/1.084 (100%)

## Distribuição
| Localização | Páginas |
|---|---|
| Root | 206 |
| biblioteca/ | 816 |
| blog/ | 7 |
| Outros | 55 |
| **Tamanho total** | **38.0 MB** |

## 42 Dimensões — Resultado

| # | Dimensão | % | Status |
|---|---|---|---|
| 1 | header_modular | 100.0% | ✅ |
| 2 | footer_modular | 100.0% | ✅ |
| 3 | cookie_bar | 100.0% | ✅ |
| 4 | partials_loader | 100.0% | ✅ |
| 5 | css_site_styles | 100.0% | ✅ |
| 6 | css_print_template | 100.0% | ✅ |
| 7 | no_font_cdn | 100.0% | ✅ |
| 8 | no_google_fonts | 100.0% | ✅ |
| 9 | ga4 | 100.0% | ✅ |
| 10 | adsense | 100.0% | ✅ |
| 11 | i18n_loader | 100.0% | ✅ |
| 12 | nurse_palm | 100.0% | ✅ |
| 13 | cognitive_ui | 100.0% | ✅ |
| 14 | breadcrumb_nav | 100.0% | ✅ |
| 15 | tool_header | 100.0% | ✅ |
| 16 | tool_actions | 100.0% | ✅ |
| 17 | btn_print | 100.0% | ✅ |
| 18 | svg_sprite | 100.0% | ✅ |
| 19 | no_old_svg | 100.0% | ✅ |
| 20 | tool_footer_zone | 100.0% | ✅ |
| 21 | tool_tags | 100.0% | ✅ |
| 22 | tool_tag | 100.0% | ✅ |
| 23 | json_ld | 100.0% | ✅ |
| 24 | skip_link | 100.0% | ✅ |
| 25 | no_old_skip | 100.0% | ✅ |
| 26 | no_broken_cls | 100.0% | ✅ |
| 27 | no_empty_divs | 100.0% | ✅ |
| 28 | h1_balanced | 100.0% | ✅ |
| 29 | h2_balanced | 100.0% | ✅ |
| 30 | h3_balanced | 100.0% | ✅ |
| 31 | h4_balanced | 100.0% | ✅ |
| 32 | h5_balanced | 100.0% | ✅ |
| 33 | h6_balanced | 100.0% | ✅ |
| 34 | font_inter | 100.0% | ✅ |
| 35 | font_nunito | 100.0% | ✅ |
| 36 | font_local | 100.0% | ✅ |
| 37 | no_tailwind | 100.0% | ✅ |
| 38 | hreflang | 100.0% | ✅ |
| 39 | site_a11y | 100.0% | ✅ |
| 40 | no_persistent_cip | 100.0% | ✅ |
| 41 | no_persistent_ac | 100.0% | ✅ |
| 42 | no_persistent_mc | 100.0% | ✅ |

## Correções aplicadas nesta sessão

### Headings balanceados (h1–h6)
- 1.032 páginas com tags não-fechadas corrigidas
- 205 páginas com tags `</hN>` órfãs removidas
- 128 páginas com h1 multilinha balanceados

### CSS padronizado
- `/css/site-styles.css` + `/css/print-template.css` em 100% das páginas (paths absolutos)
- Font Awesome CDN removido — migrado para woff2 local
- Google Fonts CDN removido — migrado para Inter + Nunito Sans locais
- DNS prefetch de CDNs externos removido

### Fontes padronizadas
- **Inter** (400/600/700) — corpo de texto e UI
- **Nunito Sans** (400/700/900) — títulos e headings
- **Font Awesome 6** (Free + Brands) — woff2 local
- Fontes não-padrão removidas: Sora, Manrope, Plus Jakarta Sans, Cormorant Garamond, Segoe UI, Calibri, Arial, Times New Roman, OpenDyslexic, Japanese

### Texto persistente removido
- "Clinical Intelligence Package" — heading removido de 206 páginas
- "6 dimensões de inteligência clínica integradas ao resultado da calculadora" — descrição removida
- "Análise Cognitiva" — heading removido de 205 páginas
- "Motor Clínico" — span removido
- 1.078 comentários HTML limpos
- Containers JS preservados (cipContainer, cognitivePanel, cognitivePanelContent)
