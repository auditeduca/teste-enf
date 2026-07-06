# NIFS-000-15: Change Log

| Field         | Value         |
|---------------|---------------|
| Document ID   | NIFS-000-15   |
| Status        | Active        |
| Version       | 2.0.0         |
| Owner         | Leivis Melo   |
| Reviewers     | —             |
| Last Updated  | 2026-07-05    |

## 1. Purpose

Track all changes to the NIFS specification across versions. Este é o histórico oficial de mudanças da especificação.

## 2. Changes

### v2.0.0 — 2026-07-05 — UI Integration & Fluxo Cognitivo Vertical

| Documento | Mudança |
|-----------|---------|
| NIFS-900-02 | **Major rewrite** — Arquitetura de dados (fonte única de verdade), fluxo cognitivo vertical (6 steps), perfis canônicos, recursos adicionais (10 cards), hashtags + related tools, CSS unificado, responsividade. Remoção de CIP/Nurse-PaLM panel/KG Links. |
| NIFS-900-04 | **Major rewrite** — Documentação de Simulados (ferramenta data-driven) e Flashcards (ferramenta data-driven). Mapeamento de fontes de dados por recurso. |
| NIFS-700-00 | **New section 11** — Integração UI: Nurse-PaLM como lógica integrada, não painel separado. Mapeamento de steps UI → camadas cognitivas. |

**Resumo da versão:**
- Nurse-PaLM deixa de ser um painel/seção separada e passa a ser a lógica integrada ao fluxo cognitivo vertical (6 steps)
- Simulados e Flashcards são ferramentas completas data-driven (não links)
- CSS unificado em `site-styles.css` (remoção de main.css, calc-tool.css, nurse-palm.css)
- Safety goals e medication rights integrados ao perfil Profissional (Step 6)
- Hashtags + ferramentas relacionadas substituem CIP/KG Links no rodapé
- Arquitetura de dados: Banco → Calculadoras + Ferramentas (fonte única de verdade)

### v1.0.0 — 2026-07-05 — Initial Specification

- 272 documentos substantivos cobrindo seções 000-1500
- 10 camadas cognitivas do Nurse-PaLM mapeadas
- DDL SQL v5.0 com 61 tabelas e 35 políticas RLS
- i18n completo para 28 idiomas (9.660 chaves)
- Validação de 57 arquivos JSON do NKOS 2026
