# Módulos integrados (React TSX → HTML estático)

Os arquivos `.tsx` / `.ts` originais do Downloads foram convertidos para o padrão do site:

- **Shell modular:** `partials-loader.js` (header, footer, a11y, cookies)
- **CSS:** `css/main.css`, `css/site-styles.css`
- **JS:** engines em `js/modules/` + dados em `js/modules/data/`

## Páginas geradas

| Página | Origem TSX/ZIP |
|--------|----------------|
| `sae.html` | SAEPage.tsx |
| `sae-wizard.html` | SAEWizard + SAEContext + etapas |
| `sbar.html` | SBARPage.tsx (zip) |
| `sbar-wizard.html` | SBARWizard (zip) |
| `diagnosticosnanda.html` | DiagnosticoNANDA.tsx |
| `notificacao-compulsoria.html` | DoencasCompulsorias.tsx |
| `calculadoravacina.html` | CalendarioVacinal.tsx |
| `protocolos.html` | ProtocolosPage.tsx |
| `biblioteca-provas.html` | LibraryPage.tsx |
| `gerador-curriculo.html` | GeradorCurriculoPage.tsx |
| `testes-autoconhecimento.html` | TestesAutoconhecimentoPage.tsx |
| `trilha-conhecimento.html` | trilha-conhecimento.zip |

## Scripts

- `scripts/build_resource_modules.py` — regenera HTML a partir dos templates
- Engines: `sae-engine.js`, `sbar-engine.js`, `cv-engine.js`, `catalog-page.js`

Rascunhos SAE/SBAR/CV persistem em `localStorage` no navegador.
