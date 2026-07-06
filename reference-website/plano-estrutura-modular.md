# Plano de Estrutura Modular — Header / Footer / Acessibilidade / Main via fetch()

## 1. Diagnóstico da situação atual

Levantei o que já existe no projeto antes de propor a estrutura nova:

**Já existe (protótipo iniciado, provavelmente por outra ferramenta):**
- `partials/header.html`, `partials/footer.html`, `partials/accessibility-toolbar.html` — fragmentos já extraídos, batendo com os 4 arquivos que você enviou.
- `index-test-modular.html` — um `index.html` alternativo com `<div id="header-placeholder">`, `#a11y-placeholder`, `#main-placeholder`, `#footer-placeholder`.
- `scripts/app.js` — orquestrador que faz `fetch()` de cada partial e injeta via `innerHTML`, disparando o evento `partials-ready`.

**Problemas que encontrei nesse protótipo (importante corrigir no plano, não repetir):**
1. `scripts/app.js` tenta carregar `partials/main.html` — mas o **main muda em cada uma das 91+ páginas** (calculadoras, escalas, simulados). Um único `main.html` genérico não funciona; cada página precisa manter seu próprio main.
2. Não existe `partials/cookie-system.html` no protótipo (só header/footer/a11y) — o sistema de cookies enviado por você ficou de fora.
3. O `<head>` do `index-test-modular.html` referencia arquivos que **não existem no projeto real**: `/public/output.css`, `/global-styles.css`, `/css/fontawesome.min.css`, `/fonts/inter/*.woff2`, `/fonts/nunito/*.woff2`, `manifest.json`.
4. **Mais grave: essas mesmas referências quebradas já estão no `index.html` real (produção)**, nas linhas 49–105 e 242. Ou seja, o site em produção hoje faz preload de 8 arquivos que não existem (fontes Inter/Nunito Sans, CSS e manifest), o que gera 404 silenciosos e pode estar fazendo as fontes customizadas caírem para a fonte padrão do sistema no visitante. Isso é independente do plano de modularização — recomendo corrigir junto, pois envolve os mesmos arquivos de `<head>`.

## 2. Objetivo

Sair do modelo atual — onde header, footer, faixa de acessibilidade e sistema de cookies estão **duplicados inline em ~95 arquivos HTML** — para um modelo onde:

- Cada um desses blocos existe em **um único arquivo-fonte** (`partials/*.html`).
- Toda página HTML vira um "shell" fino: `<head>` próprio (SEO/OG/canonical — isso continua por página, não é compartilhável) + placeholders vazios + o conteúdo específico daquela página.
- Um único script carrega os partials via `fetch()` e só then inicializa os demais scripts (menu, i18n, widgets).

Isso reduz o custo de qualquer alteração de footer/header/cookies/acessibilidade de "editar 95 arquivos" para "editar 1 arquivo".

## 3. Estrutura de diretórios proposta

```
/ (raiz do domínio)
├── index.html                         shell — head + placeholders + main específico
├── balancohidrico.html                shell — mesmo padrão (repetido nas 91 páginas)
├── ... (demais calculadoras/escalas/simulados)
├── institucional.html
├── privacidade.html
├── sustentabilidade-digital.html
├── busca.html
│
├── partials/                          fragmentos HTML compartilhados (fonte única)
│   ├── header.html                    já existe — bate com o enviado
│   ├── footer.html                    já existe — bate com o enviado
│   ├── accessibility-toolbar.html     já existe — bate com o enviado (a11y-toolbar)
│   └── cookie-system.html             NOVO — falta no protótipo atual
│
├── i18n/                              NOVO — um JSON por idioma (troca o dicionário
│   │                                  gigante embutido em lang-selector.js)
│   ├── manifest.json                  {"default":"pt","fallback":"en","available":[...]}
│   ├── pt.json
│   ├── en.json
│   ├── es.json
│   └── ... (demais dos 30 idiomas já listados em lang-selector.js)
│
├── js/
│   ├── partials-loader.js             NOVO — substitui/corrige scripts/app.js
│   ├── i18n-loader.js                 REFATORADO de lang-selector.js — busca só o
│   │                                  idioma ativo via fetch, não os 30 de uma vez
│   ├── mega-menu.js                   mantém — passa a escutar "partials:ready"
│   ├── site-widgets.js                mantém — passa a escutar "partials:ready"
│   └── global-scripts.js
│
├── css/
│   └── site-styles.css                mantém — já é compartilhado por todas as páginas
│
├── fonts/                             NOVO — os arquivos woff2 que faltam hoje
│   ├── inter/inter-regular.woff2, inter-600.woff2, inter-700.woff2
│   └── nunito/nunito-regular.woff2, nunito-700.woff2, nunito-900.woff2
│
├── images/, assets/                   mantém como está
└── site.webmanifest.webmanifest       mantém (e corrigir o link no <head> pra apontar
                                       pra este nome, não "manifest.json")
```

**Por que `partials/main.html` não existe nessa proposta:** ao contrário do protótipo, o main de cada página fica **dentro do próprio arquivo shell** (ex.: `balancohidrico.html` mantém a calculadora dele no `<main>`). Só header/footer/a11y/cookies são de fato idênticos entre páginas — o main nunca é.

## 4. Contrato de cada página (shell)

Toda página passa a seguir este esqueleto:

```html
<body>
  <a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>

  <div id="site-header"></div>
  <div id="site-a11y"></div>

  <main id="main-content">
    <!-- ÚNICO bloco que muda por página -->
  </main>

  <div id="site-footer"></div>
  <div id="site-cookie"></div>

  <script src="js/partials-loader.js" defer></script>
</body>
```

`js/partials-loader.js` faz o fetch dos 4 partials em paralelo (não em série como no protótipo atual — não há dependência entre header/a11y/footer/cookie, então `Promise.all` é mais rápido), injeta cada um no seu placeholder, e só depois dispara `document.dispatchEvent(new Event('partials:ready'))`.

`mega-menu.js`, `i18n-loader.js` e `site-widgets.js` passam a se registrar assim, em vez de rodar em `DOMContentLoaded`:

```js
document.addEventListener('partials:ready', initMegaMenu);
```

Isso resolve a causa mais comum de bug em arquitetura fetch-partial: script rodando antes do HTML do header existir no DOM.

## 5. i18n via JSON fetchado (em vez de dicionário embutido)

Hoje `lang-selector.js` tem ~700 linhas com os dicionários de `pt`/`en`/`es` embutidos no próprio JS, e mais 27 idiomas cadastrados no seletor sem tradução real. A proposta:

- Cada idioma vira `i18n/{codigo}.json`, no mesmo formato flat de chaves que já é usado em `data-i18n="tool.balancohidrico.titulo"` — não precisa reescrever nenhum atributo HTML existente, só mover o conteúdo do objeto JS para um arquivo JSON por idioma.
- `i18n-loader.js` busca **só o idioma ativo** (não os 30), reduzindo payload inicial.
- Fallback em cadeia: chave ausente no JSON do idioma ativo → tenta `en.json` → tenta `pt.json`. Isso permite lançar um idioma novo cobrindo só header/footer/a11y (como os lotes que você já gerou para zh/ja/ko/ar/hi/tr/uk/cs/ro/el) sem quebrar nada — o resto cai no fallback.
- `i18n/manifest.json` declara quais idiomas estão realmente prontos, para o seletor de idiomas não oferecer um idioma sem tradução nenhuma.

## 6. Riscos a decidir com você

**SEO/crawl dos links internos.** Hoje o `<nav>` do header e os links do footer existem no HTML puro de cada página — é como o Google descobre as 91 páginas de calculadora navegando pelo menu. Com fetch client-side, esses links só existem depois do JavaScript rodar. O Google moderno normalmente executa JS e indexa mesmo assim, mas com atraso, e outras ferramentas (preview de compartilhamento, leitores de tela mais antigos) podem não executar. Como você já pediu fetch explicitamente, meu recomendação para mitigar sem abandonar a abordagem:
- Manter `sitemap.xml` sempre atualizado com as 91+ páginas (fonte de descoberta independente do menu).
- Manter as tags de `<head>` (title, description, og:*, canonical, hreflang, JSON-LD) sempre no próprio arquivo de cada página, nunca dependentes de fetch — isso já é o caso hoje e deve continuar assim.

**FOUC / layout shift.** Entre o HTML carregar e o fetch do header terminar, a página mostra vazio no topo por uma fração de segundo. Mitigação simples: um skeleton de altura fixa no placeholder (`min-height` reservando o espaço do header) até o partial injetar.

## 7. Correções a fazer junto (bugs encontrados, não fazem parte do pedido original)

1. No `<head>` do `index.html` real, remover ou apontar corretamente os `<link rel="preload">` de `/public/output.css`, `/global-styles.css`, `/css/fontawesome.min.css` e os 8 `@font-face` de `/fonts/*` — hoje todos 404.
2. Trocar `<link rel="manifest" href="manifest.json" />` para `href="site.webmanifest.webmanifest"` (nome real do arquivo no projeto).
3. Decidir: subir os `.woff2` de Inter/Nunito Sans para `fonts/` (fica igual ao protótipo) ou remover os `@font-face` e confirmar que o site já usa fonte via Google Fonts/CDN em algum outro lugar do `<style>` inline.

## 8. Roteiro de implementação sugerido (fases)

1. **Corrigir os 404 de fonte/CSS/manifest** no `index.html` real (rápido, baixo risco, resolve um bug de produção já existente).
2. **Criar `partials/cookie-system.html`** faltante e revisar os 3 partials já extraídos, deixando-os idênticos ao `index.html` de produção (fonte da verdade).
3. **Escrever `js/partials-loader.js`** novo (paralelo, com evento `partials:ready`, com skeleton anti-FOUC) — não reaproveitar o `scripts/app.js` do protótipo, que depende do `partials/main.html` inexistente.
4. **Piloto em 1 página** (ex.: `institucional.html`, que já foi recentemente alinhada ao padrão) — validar visualmente e no console antes de tocar nas 91 páginas de calculadora.
5. **Migrar `index.html`** — maior risco/maior visibilidade, fazer depois do piloto validado.
6. **Script de migração em lote** (Node ou Python) para as 91 páginas restantes: remove o bloco de header/footer/a11y/cookie hardcoded de cada arquivo e substitui pelos placeholders + script tag.
7. **Migrar i18n** de `lang-selector.js` para `i18n/{lang}.json` + `i18n-loader.js`, mantendo os `data-i18n` existentes intactos.

Está feito só o levantamento e o plano — nenhum arquivo de produção foi alterado nesta etapa. Me diga qual fase você quer que eu execute primeiro.
