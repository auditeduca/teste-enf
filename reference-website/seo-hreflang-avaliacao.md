# Avaliação de hreflang e SEO internacional

## Diagnóstico

O `index.html` de produção continha 18 tags `<link rel="alternate" hreflang="...">` (en, es, fr, de, it, ja, zh, hi, ar, ru, tr, ko, nl, pl, sv, id, vi, uk) mais `x-default`, todas apontando para caminhos do tipo:

```
https://www.calculadorasdeenfermagem.com.br/en/index.html
https://www.calculadorasdeenfermagem.com.br/es/index.html
https://www.calculadorasdeenfermagem.com.br/fr/index.html
...
```

Nenhuma dessas URLs existe. O site inteiro é servido a partir de uma única URL (`/`, ou `/index.html`), e a troca de idioma acontece inteiramente no navegador, via JavaScript (`lang-selector.js`), que troca o texto visível através dos atributos `data-i18n` sem nunca mudar a URL nem gerar uma versão HTML separada por idioma.

Isso é uma implementação de hreflang que não faz sentido tecnicamente: o padrão hreflang existe para dizer ao Google "esta URL é a versão em inglês da página X, esta outra é a versão em espanhol", e pressupõe que cada uma dessas URLs é rastreável de forma independente. Quando as 18 URLs declaradas não existem, o resultado prático é: o Google eventualmente tenta rastrear `/en/index.html` etc., recebe 404, e ignora ou desconta a confiabilidade das tags hreflang da página — na melhor hipótese um sinal ignorado, na pior um sinal de qualidade técnica ruim para o domínio.

## Causa raiz

O texto institucional do site (seção "Uma plataforma global") faz a alegação de alcance em **"mais de 195 países"**. Em algum momento essa alegação de alcance/abrangência de público foi confundida com uma promessa de **localização técnica em 195 idiomas/URLs**, o que nunca foi implementado — o site oferece apenas troca visual de idioma (atualmente pt nativo + en + es completos, mais 18 idiomas com tradução parcial abandonada em uma sessão anterior, cobrindo só ~15% das chaves de texto).

## Correção aplicada agora

Removidas as 16 tags falsas (fr, de, it, ja, zh, hi, ar, ru, tr, ko, nl, pl, sv, id, vi, uk) e a tag `en`/`es` que também apontavam para subpastas inexistentes. Mantidas apenas:

```html
<link rel="canonical" href="https://www.calculadorasdeenfermagem.com.br/" />
<link rel="alternate" hreflang="pt-BR" href="https://www.calculadorasdeenfermagem.com.br/" />
<link rel="alternate" hreflang="x-default" href="https://www.calculadorasdeenfermagem.com.br/" />
```

Isso é honesto com a arquitetura real do site hoje: uma única URL, conteúdo nativo em português, sem páginas alternativas rastreáveis. Zero risco de 404 ou sinal incorreto para o Google.

## Caminhos para uma implementação completa e correta de hreflang

Se o objetivo for obter benefício de SEO internacional de verdade (o que hreflang exige: URLs distintas e rastreáveis por idioma), existem duas rotas — nenhuma delas foi executada nesta sessão, pois envolve decisão de arquitetura e trabalho de geração de páginas, fora do escopo de "não alterar CSS/layout, só modularizar":

**Opção A — Páginas estáticas por idioma (recomendada a médio prazo).**
Gerar `/en/index.html` e `/es/index.html` como snapshots estáticos reais (HTML pré-renderizado com o texto já em inglês/espanhol, não dependente de JS para o conteúdo textual principal), a partir dos dicionários que já existem prontos e completos em `i18n/en.json` e `i18n/es.json` (345 chaves cada, criados nesta sessão). Cada página teria sua própria tag canonical e o conjunto de hreflang ligando as três versões entre si:

```html
<!-- em /index.html -->
<link rel="alternate" hreflang="pt-BR" href=".../" />
<link rel="alternate" hreflang="en" href=".../en/" />
<link rel="alternate" hreflang="es" href=".../es/" />
<link rel="alternate" hreflang="x-default" href=".../" />
```
(e o espelho equivalente nas páginas /en/ e /es/). Isso é viável hoje porque en/es já têm 100% das chaves traduzidas — não é viável ainda para os outros 18 idiomas, que têm tradução parcial.

**Opção B — Manter apenas 1 URL, sem hreflang multilíngue.**
Tratar "mais de 195 países" como alcance de audiência/usuários (pessoas nesses países conseguem ler o conteúdo em português, inglês ou espanhol), não como promessa de indexação em 195 variantes de idioma. Nesse caso a correção já aplicada (hreflang mínimo e verdadeiro) é a configuração final, e a alegação "195 países" deve ficar restrita ao texto de marketing da seção "Uma plataforma global", não ao `<head>` da página.

## Recomendação

Curto prazo: usar a Opção B (já aplicada) — ela é honesta com o que existe e remove um bug real de SEO sem exigir novo trabalho de infraestrutura.

Médio prazo, se o negócio quiser reivindicar SEO internacional de fato: seguir a Opção A apenas para os 2 idiomas com tradução 100% completa (en, es), gerando páginas estáticas reais a partir de `i18n/en.json`/`i18n/es.json` — e só expandir para os outros 18 idiomas depois que os arquivos `{code}.json` correspondentes forem completados com as ~345 chaves (hoje eles cobrem só uma fração, conforme documentado em `i18n/manifest.json`).
