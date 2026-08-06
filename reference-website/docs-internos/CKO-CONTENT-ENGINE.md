# CKO Content Engine — identidade visual + módulos + validador

**Status:** implementado (piloto TRR)  
**Data:** 2026-08-05  
**Alinha a:** `PADRAO_PAGINAS_SAUDE_EXCELENCIA.md` §0–§10 · `CKO-PAGE-SHELL.md`

---

## 1. Pesquisa — o que define “página de conteúdo padronizada”

Benchmarks usados (não cópia visual):

| Fonte | Adoção CKO |
|-------|------------|
| NHS Service Manual — health content | Clareza, evidência, atualização, HTML primeiro |
| NHS / WCAG 2.2 AA | Contraste, teclado, um H1, landmarks |
| MedlinePlus / CDC educativas | Sumário, seções curtas, FAQ, refs |
| COFEN / MS / ANVISA / PlanificaSUS | Disclaimer POP + enquadramento BR |

**Conclusão de produto:** excelência ≠ só texto bonito. É **mesmo cluster visual** (shell) + **mesmos módulos editoriais** (engine) + **contrato verificável** (validator).

---

## 2. Identidade visual (contrato)

Arquivo: `data/cko-content-identity.json`

| Token / regra | Valor |
|---------------|--------|
| Navy | `#1A3E74` |
| Tint de página | `#f8fafc` |
| Corpo | Inter |
| Display | Nunito Sans |
| Largura | `max-w-7xl` |
| Grid | `.cko-layout` = main + sidebar 280px ≥1024px |
| Body | classe `cko-cart-page` |
| Proibido | breadcrumb legado, `title-bar`, `</div>in>`, hero navy local |

CSS:

- `css/pages/cart-emergencia.css` — hero, botões, tokens produto  
- `css/pages/cko-page-shell.css` — breadcrumb, layout, sidebar  
- `css/pages/cko-content-modules.css` — FAQ, related, refs, credits  

---

## 3. Duas camadas (não misturar)

```
┌─ Shell (cko-page-shell.js + cko-shell-pages.json)
│   chrome · hero · sidebar · aside
│
└─ Content Engine (cko-content-engine.js + data/content/<id>.json)
    módulos C–F (tools, faq, related, references, media)
    TOC da sidebar continua no shell (auto H2 ou manifesto)
```

| Camada | Responsável | Dados |
|--------|-------------|--------|
| Cluster / chrome | Shell | `data/cko-shell-pages.json` |
| Módulos editoriais | Engine | `data/content/<pageId>.json` |
| Aceite automático | Validator | `tools/validate_content_identity.py` |

---

## 4. Como ligar uma página

```html
<link href="/css/pages/cart-emergencia.css" rel="stylesheet">
<link href="/css/pages/cko-page-shell.css" rel="stylesheet">
<link href="/css/pages/cko-content-modules.css" rel="stylesheet">
<script src="/js/cko-page-shell.js" defer></script>
<script src="/js/cko-content-engine.js" defer></script>
```

Dentro de `.cko-layout__main`, após o artigo:

```html
<div
  data-cko-content="trr"
  data-cko-modules="tools,faq,related,references,media">
</div>
```

Criar `data/content/trr.json` conforme `schemas/cko-content-page.schema.json`.

### Módulos (`data-cko-modules`)

| Nome | Classe DOM | Mínimo |
|------|------------|--------|
| `toc` | `.cko-mod--toc` | opcional (sidebar já faz TOC) |
| `tools` | `.cko-mod--tools` | recomendado |
| `faq` | `.cko-mod--faq` | ≥ 4 Q&A |
| `related` | `.cko-mod--related` | ≥ 3 links tipados |
| `references` | `.cko-mod--refs` | ≥ 1 |
| `media` | `.cko-mod--media` | créditos; protocol-figure com `mobile` |

API runtime:

```js
CKOContentEngine.validateDom()
CKOContentEngine.validateManifest(manifest, identity)
CKOContentEngine.getManifest('trr')
```

Evento: `cko-content:ready`.

---

## 5. Validador

```bash
cd calculadorasdeenfermagem.com.br
python tools/validate_content_identity.py
python tools/validate_content_identity.py --file time-de-resposta-rapida.html
python tools/validate_content_identity.py --strict
python tools/validate_content_identity.py --json tmp/identity-report.json
```

| Severidade | Exemplos |
|------------|----------|
| **error** | sem shell CSS/JS, sem `cko-layout`, slot faltando, manifesto quebrado, `</div>in>` |
| **warn** | sem engine ainda, sem FAQ mount, H1 estático, midia `PENDENTE`, FAQ &lt; 4 |
| **info** | hero do produto carrinho |

Exit code `1` se houver errors (`--strict` também falha em warns).

---

## 6. Rollout

1. **TRR** — piloto com manifesto + engine (feito)  
2. Protocolos do nav (`SAV`, `5 Hs`, `5 Ts`) — um manifesto cada  
3. Guias de segurança (`checagem`, `metas`, `vigilancia`…)  
4. Bibliotecas — FAQ/related leves  
5. Não aplicar a calculadoras puras até decisão explícita  

---

## 7. Critério de aceite (“identidade ok”)

- [ ] Validator sem **errors**  
- [ ] Shell mounts + `cko-layout`  
- [ ] `data-cko-content` + manifesto JSON válido  
- [ ] FAQ ≥ 4, related ≥ 3, references ≥ 1  
- [ ] Sem padrões proibidos do contrato  
- [ ] Desktop: sidebar sticky; mobile: cards empilhados  

---

## 8. Arquivos-chave

| Path | Função |
|------|--------|
| `data/cko-content-identity.json` | Contrato de identidade |
| `data/content/*.json` | Manifestos por página |
| `js/cko-content-engine.js` | Renderer de módulos |
| `css/pages/cko-content-modules.css` | Visual dos módulos |
| `tools/validate_content_identity.py` | Gate de qualidade |
| `schemas/cko-content-page.schema.json` | Schema do manifesto |
