# Modos de renderização

## Preview inline

Arquivos em `render/inline/`.

Objetivo: inspeção visual independente de assets externos.

- CSS embutido no HTML
- conteúdo semanticamente equivalente ao modo de produção
- não é o artefato primário de produção

## Produção fetch

Arquivos em `render/fetch/`.

Objetivo: produção modular.

- sem CDN
- CSS first-party via `<link>` para `assets/app.css`
- `public/output.css` é a cópia publicável do mesmo stylesheet
- header, footer e módulos do Site Shell entram no HTML gerado

## Paridade

Os dois modos devem manter paridade semântica e diferir apenas na estratégia de carregamento de estilos.

Validador: `validators/dual_render.py` (compara o texto visível das páginas HTML).
