# Design System

Tokens em `assets/css/app.css`. Comparação anexo vs runtime: `cko_core/design_token_registry.json` e `/admin/design-system.html`.

| Token | Valor | Uso |
|---|---|---|
| `--navy-primary` | `#1A3E74` | barra de acessibilidade, rodapé, botões, títulos |
| `--header-bg` | `#ffffff` | header público 60px (RESTORED) |
| `--a11y-height` | `36px` | barra de acessibilidade |
| `--navy-medium` | `#1E4D8C` | hover, links |
| `--navy-hover` | `#122C54` | botão primário hover |
| `--navy-secondary` | `#003366` | botão secundário |
| `--blue-light` | `#4A90E2` | destaque |
| `--radius-control` | `8px` | controles |

Tipografia: stack `Inter, Segoe UI, ...` **sem carregar woff2**. Inter/Nunito/OpenDyslexic **não existem** neste tree. CDN é proibido. Fonte dislexia usa fallback Arial/Verdana (GAP).

## Shell público (restaurado neste lote)

- skip link “Ir para o conteúdo”
- barra `#barraAcessibilidade` 36px navy (fonte, linha, letra, contraste, escuro, dislexia, foco, reset)
- header branco 60px com wordmark Drive `assets/img/logotipo-calculadoras-de-enfermagem.webp`
- rodapé navy com logo `logotipo-footer.png`, colunas Institucional / Acessibilidade / Governança
- **sem** captura de e-mail / newsletter / cookies (NO_SENSITIVE_CAPTURE)
- seletor i18n aponta para Admin e permanece HOLD (19 códigos Drive ≠ runtime pt-BR)
- alvos de toque ≥ 44px na navegação; barra a11y compacta 32px com foco visível

Admin mantém sidebar navy + topbar branca **e** a mesma barra de acessibilidade.

## Logos

Recuperados do Drive (L190 candidate):

- `1BlJcgdqn93-JyVkPTw9-QmHnpjTpUH0x` wordmark header
- `1Tez0sazlumxO8EeapH30Xw6bF4KpGGnh` wordmark footer

## Metadados mínimos

- charset UTF-8
- viewport
- theme-color `#1A3E74`
- title e description por objeto

JSON-LD, hreflang e Open Graph completos **não** estão neste lote.
