# NIFS-1000-03: Accessibility (WCAG)

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-1000-03                        |
| Status        | Validated                          |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Documentar os requisitos de acessibilidade WCAG do website e o plano de remediação.

## 2. Current Accessibility Features

O website já implementa:

| Feature | Implementação | Arquivo |
|---------|--------------|---------|
| Skip link | `class="skip-link"` → `#main-content` | Todas páginas |
| ARIA live | `aria-live="polite"` em status messages | Todas páginas |
| Accessibility toolbar | Font size, contrast, dark mode, dyslexia font | `accessibility-toolbar.html` |
| Cookie consent | Banner com aceitar/rejeitar/personalizar | `cookie-system.html` |
| Keyboard navigation | Tab, ESC fecha menus, Enter ativa | `mega-menu.js` |
| ARIA labels | `aria-expanded`, `aria-label`, `aria-hidden` | Header, menu, calculadoras |
| Star ratings | `aria-label="4.9 de 5 estrelas"` | Tool header |
| Breadcrumb | `nav aria-label="Breadcrumb"` | Todas páginas |
| SVG icons | `aria-hidden="true"` em decorativos | Todas páginas |

## 3. Audit Results

| Métrica | Status |
|---------|--------|
| Audit executado | ✅ 100% |
| Passed | ❌ false |
| Erros críticos | 1.350 (WCAG) |
| Report path | `datasets/metadata/full_audit_report.json` |

## 4. WCAG Remediation Plan

### Prioridade 1 — Críticos (corrigir imediatamente):
- Contraste insuficiente em alguns elementos
- Falta de `alt` em algumas imagens
- Formulários sem label associado
- Heading hierarchy inconsistente

### Prioridade 2 — Importantes:
- Focus visible em todos os interativos
- ARIA roles em regions dinâmicas
- Tab order lógico em formulários
- Error identification em inputs

### Prioridade 3 — Melhorias:
- Reduce motion respeitado
- Texto de links descritivo
- Language attribute em conteúdo traduzido
- Status messages com role="status"

## 5. Accessibility Toolbar

```html
<div id="barraAcessibilidade" role="region" aria-label="Barra de utilitários">
  <!-- Font size +/− -->
  <!-- High contrast toggle -->
  <!-- Dark mode toggle -->
  <!-- Dyslexia-friendly font -->
  <!-- Reset all -->
  <!-- Keyboard shortcuts help -->
</div>
```

## 6. 30-Language Accessibility

Cada idioma deve manter:
- `lang` attribute correto no `<html>`
- Direção de texto (RTL para ar, he)
- Fontes que suportem caracteres do idioma
- ARIA labels traduzidos

## 7. NIS v5.0 Accessibility

O NIS adicionará:
- Screen reader optimization para reasoning trace
- Voice navigation
- High-contrast tema clínico (para uso em UTI)
- A11y audit automatizado no CI

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-06 | Clinical Safety |
| NIFS-1000-01 | LGPD/Privacy |
| NIFS-1200-04 | A11y Quality Gates |
