# CKO Page Templates — home, institucional, calculadora, ferramenta

**Status:** implantado (pilotos)  
**Data:** 2026-08-05  
**Contrato:** `data/cko-page-templates.json`

---

## Tipos

| Template | `data-cko-template` | Shell | Pilotos |
|----------|---------------------|-------|---------|
| Página inicial | `home` | Não (hero próprio) | `index.html` |
| Institucional | `institutional` | Sim | `missao.html` |
| Calculadora / escala | `calculator` | Sim + workspace | `news.html` |
| Ferramenta | `tool` | Sim | `downloads.html` |
| Conteúdo educativo | `content` | Sim + Content Engine | `time-de-resposta-rapida.html` |

---

## Assets comuns

```html
<link href="/css/pages/cart-emergencia.css" rel="stylesheet">
<link href="/css/pages/cko-page-shell.css" rel="stylesheet"> <!-- se shell -->
<link href="/css/pages/cko-page-templates.css" rel="stylesheet">
<script src="/js/cko-page-shell.js" defer></script> <!-- se shell -->
<script src="/js/cko-page-templates.js" defer></script>
```

```html
<body class="cko-cart-page" data-cko-template="institutional">
```

---

## Estrutura por tipo

### Home
- Sem `cko-layout` obrigatório
- Regiões: `data-cko-home="hero|quick-access|highlights"`
- Brand em evidência no primeiro viewport

### Institucional / Tool / Content
```
chrome → hero → cko-layout (main + sidebar)
```

### Calculadora
```
chrome → hero → cko-layout
  main: .cko-calc-workspace
    .cko-calc-panel[data-cko-calc-form]
    .cko-calc-result[data-cko-calc-result]
  side: sidebar shell
```

Esqueletos prontos em `/templates/`.

---

## Validação

```bash
python tools/validate_page_templates.py
python tools/validate_page_templates.py --file news.html
```

Runtime: `CKOPageTemplates.validate()` após `cko-template:ready`.

---

## Rollout

1. Pilotos (home, missão, NEWS, downloads, TRR) — feito  
2. Demais institucionais (`objetivo`, `politica`, `termos`, `mapa-do-site`)  
3. Escalas de alto tráfego (NEWS → Braden → Morse → IMC…)  
4. Ferramentas (`medicamentos`, `risktools`, geradores)  
