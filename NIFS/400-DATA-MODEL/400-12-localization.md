# NIFS-400-12: Localization

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-12                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estratégia de localização do NIS para suportar múltiplos locales.

## 2. Locale Support

| Locale | Language | Direction | Status |
|--------|----------|-----------|--------|
| pt-BR | Português (Brasil) | LTR | Primary |
| en-US | English (US) | LTR | Active |
| es-ES | Español | LTR | Planned |
| fr-FR | Français | LTR | Planned |
| ar-SA | العربية | RTL | Planned |

## 3. NIS Implementation

| Table | Role |
|-------|------|
| `ni_i18n.locales` | Locales suportados (5 planejados) |
| `ni_i18n.translations` | Traduções de conteúdo |
| `ni_i18n.cultural_adaptations` | Adaptações culturais (não só tradução) |

## 4. Localization vs Internationalization

- **i18n** (internationalization): Estrutura que suporta múltiplos locales (campos `label_pt`, `label_en`, `label_es`)
- **l10n** (localization): Tradução e adaptação cultural efetiva

## 5. Clinical Localization Challenges

| Challenge | Example |
|-----------|---------|
| Terminology | NANDA "Risk of Impaired Skin Integrity" → "Risco de Integridade Tissular Prejudicada" |
| Cultural | Protocolos de banho diferem por cultura hospitalar |
| Regulatory | Notificações compulsórias variam por país |
| Units | mmHg vs kPa para pressão arterial |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-13 | Multilingual Support |
| NIFS-800-01 | FHIR (locale in resources) |
