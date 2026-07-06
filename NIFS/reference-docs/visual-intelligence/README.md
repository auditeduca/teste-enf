# Visual Experience Intelligence Platform (VEIP)

Plataforma de governança visual para **Calculadoras de Enfermagem / NKOS**: geração de imagens Open Graph, auditoria automática (VGA) e **Nursing Visual DNA** para personalização por locale, persona, ferramenta clínica e design system.

## Objetivo

Tratar imagens de compartilhamento como **asset estratégico de distribuição**, não adaptação do hero da página.

| Uso | Hero institucional | OG 1200×630 |
|-----|-------------------|-------------|
| WhatsApp / Facebook | 6–7/10 | Meta **10/10** |
| LinkedIn Article | 9/10 | OG dedicado |
| Banner página | 9,5/10 | Não substituir hero |

## Especificação OG Premium

| Critério | Valor |
|----------|-------|
| Dimensões | 1200 × 630 px (1.91:1) |
| Retina | 2400 × 1260 px |
| Área segura | 60 px |
| Título | ≤ 7 palavras / 55 caracteres |
| Subtítulo | ≤ 120 caracteres |
| Selos | máx. 4 |
| Peso | &lt; 250 KB (ideal 100–180 KB) |
| Layout | 60% texto · 40% hero visual |

### O que incluir

- Logo + marca  
- Título forte  
- Subtítulo  
- Um visual principal  
- Selos estratégicos (🌱 Sustentável, 🔒 Seguro, 🌎 Global, 🤖 IA Responsável)

### O que evitar

- Botões / CTAs (não clicáveis em OG)  
- Cards, menus, breadcrumb  
- Texto excessivo  
- Componentes da página  

## Master Data

```
datasets/master-data/visual-intelligence/
├── canonical.json          # Programa VEIP + pipeline
├── brand_identity.json     # Paleta, tipografia, tokens visuais
├── og_templates.json       # Templates por página/ferramenta
├── cultural_rules.json     # Regras por país (BR, US, JP, CN, DE, FR, SA, IN)
├── visual_personas.json    # estudante, profissional, gestor, acadêmico, emergência
├── scoring_rubric.json     # Módulos VGA + níveis Bronze→Excellence
└── og_manifest.json        # Saída gerada (path → asset)
```

## Agentes

```bash
# Gerar todos os templates OG (pt-BR)
python scripts/visual_intelligence_agents/run_batch.py --generate-all

# Um template (ex.: sustentabilidade)
python scripts/visual_intelligence_agents/run_batch.py --generate sustentabilidade

# Auditoria VGA
python scripts/visual_intelligence_agents/run_batch.py --audit-path /sustentabilidade

# Prompt DNA para IA generativa
python scripts/visual_intelligence_agents/run_batch.py --prompt-dna --page glasgow --persona estudante --json

# Status
python scripts/visual_intelligence_agents/run_batch.py --status
```

Saída: `website/assets/images/og/*.svg` (+ `.jpg` se Pillow disponível).

## API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/visual-intelligence/status` | Status e manifest |
| POST | `/api/visual-intelligence/generate` | `{ "template": "sustentabilidade" }` ou `{ "all": true }` |
| POST | `/api/visual-intelligence/audit` | `{ "canonical_path": "/sustentabilidade" }` |
| POST | `/api/visual-intelligence/prompt-dna` | DNA + prompt estruturado |

UI plataforma: `/visual-intelligence`

## Integração website

`website_lib.render_head_assets()` resolve OG via `og_manifest.json` por `canonical_path`.  
Twitter card: `summary_large_image` + `og:image:width/height`.

Páginas com OG dedicado após `--generate-all`:

- `/sustentabilidade` — Sustentabilidade Digital na Enfermagem  
- `/privacidade` — Privacidade e Segurança de Dados  
- `/` — Home  
- `/ferramentas`, `/escalas`, `/educacao`  
- Ferramentas: Glasgow, Braden  

## Visual Governance Agent (VGA)

Módulos de score (peso em `scoring_rubric.json`):

| Módulo | Foco |
|--------|------|
| brand | Logo, paleta, tipografia, área segura |
| clinical | Uniforme, equipamentos, ambiente |
| cultural | Locale, expressão, vestimenta |
| og | Dimensões, legibilidade miniatura |
| accessibility | Contraste WCAG |
| trust | Tom institucional |
| visual_harmony | Harmonia com design system |
| persona_fit | Perfil usuário |
| device_fit | Tablets, monitores, UI plausível |

Scores compostos: **PNIS**, **VCS**, **GlobalReadiness**  
Níveis: bronze (70+) → excellence (98+)

## Evolução (fases)

1. **MVP** — Prompt + LLM (sem DB) ✅ parcial  
2. **Banco de regras** — Master data visual ✅  
3. **Knowledge Graph** — Relacionar país ↔ cultura ↔ enfermagem  
4. **Visual Intelligence Platform** — Auditoria histórica, aprendizado, API pública  

## Posicionamento

Nenhuma plataforma atual une **inteligência clínica + aprendizagem adaptativa + personalização visual + UX contextual + localização cultural + IA generativa** em enfermagem. VEIP é o primeiro passo do **Nursing Experience Operating System**.
