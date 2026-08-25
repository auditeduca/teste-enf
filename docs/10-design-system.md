# Design System

Tokens v0.1 em `assets/css/app.css`.

| Token | Valor | Uso |
|---|---|---|
| `--navy-primary` | `#1A3E74` | header, botões, títulos |
| `--navy-medium` | `#1E4D8C` | hover, links |
| `--navy-dark` | `#163269` | skip-link |
| `--blue-light` | `#4A90E2` | destaque |
| `--white` | `#FFFFFF` | cartões |
| `--gray-bg` | `#f4f7fb` | fundo |
| `--gray-text` | `#475569` | secundário |

Tipografia: stack do sistema (sem CDN de fontes).

## Shell

- skip link “Ir para o conteúdo”
- header com marca CKO
- footer com disclaimer
- alvos de toque ≥ 44px nos controles
- `aria-label` na trilha e na navegação
- contraste texto navy/branco no header

## Metadados mínimos

- charset UTF-8
- viewport
- theme-color `#1A3E74`
- title e description por objeto

JSON-LD, hreflang e Open Graph completos **não** estão no v0.1.
