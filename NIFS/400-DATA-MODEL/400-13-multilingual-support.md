# NIFS-400-13: Multilingual Support

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-13                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS armazena e recupera dados em múltiplos idiomas simultaneamente.

## 2. Multilingual Pattern

### 2.1 Dual-Label Columns (Current)
```sql
nanda_code VARCHAR(8) PK,
label_pt   VARCHAR(256),  -- PT-BR (primary)
label_en   VARCHAR(256),  -- EN-US (secondary)
```

### 2.2 Translation Table (Extended)
```sql
ni_i18n.translations
  content_id     → FK to ni_content.items
  locale_code    → FK to ni_i18n.locales
  translated_text TEXT
```

### 2.3 Cultural Adaptation
```sql
ni_i18n.cultural_adaptations
  content_id     → FK
  locale_code    → FK
  adaptation_type: clinical_context, regulatory, visual
```

## 3. Clinical Terminology Translation

| Original (EN) | PT-BR | Notes |
|---------------|-------|-------|
| NANDA: "Impaired Skin Integrity" | "Integridade Tissular Prejudicada" | ISO 18104 compatible |
| NIC: "Pressure Management" | "Manejo da Pressão" | COFEN terminology |
| NOC: "Tissue Integrity: Skin & Mucous Membranes" | "Integridade Tissular: Pele e Mucosas" | Standard translation |

## 4. NKOS Data

- `asset_localizations.json`: 3,000 localizações (pt/en/es) para assets visuais
- `ni_i18n` schema: 3 tabelas planejadas para v6.0
- Content by profile (APGAR pilot): já tem `introduction_pt` + `introduction_en`

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-12 | Localization |
| NIFS-800-01 | FHIR (language element in resources) |
