# NIFS-100-12: Extensibility

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-12                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS se estende — novos schemas, agentes, calculadoras, terminologias e módulos sem breaking changes.

## 2. Extension Points

| Extension | How | Example |
|-----------|-----|---------|
| New terminology | Add CodeSystem + mappings | ICNP addition |
| New calculator | Add to `ni_cog.calculator_mappings` | New sepsis score |
| New agent | Add to `ni_council.agents` | COUNCIL.PALLIATIVE.001 |
| New schema | CREATE SCHEMA + tables | ni_palliative |
| New protocol | Add to `ni_protocol.protocols` | New stroke protocol |
| New population | Add to `ni.populations` | Obstetrics |
| New FHIR profile | Add to `ni_interop.profiles` | FHIR_R4_OBSTETRICS |
| New plugin | Add to `ni_platform.plugins` | Telemedicine plugin |

## 3. Extension Rules

1. **Aditive, não destrutivo**: nunca remover, sempre adicionar
2. **Versionado**: nova extensão = nova versão
3. **Testado**: extensão passa por validation cases
4. **Aprovado**: clinical governance aprova extensões clínicas
5. **Compatível**: não quebra consumidores existentes

## 4. Plugin Architecture

O NIS tem uma arquitetura de plugins (`ni_platform.plugins`):

```
Core Engine (obrigatório)
├── Rendering Engine
├── Content Engine
├── Clinical Engine (core reasoning)
├── Knowledge Graph Engine
└── API Engine

Optional Plugins:
├── Telemedicine Plugin
├── Obstetrics Plugin
├── Palliative Care Plugin
├── Mental Health Plugin
├── Quality Reporting Plugin
└── Custom Hospital Plugin
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-13 | Modularity |
| NIFS-900-04 | Modules |
| NIFS-900-05 | Services |
