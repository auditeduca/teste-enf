# Regulatory Core

Um único objeto regulatório canônico pode ter múltiplas projeções:

```text
REGULATORY_INSTRUMENT
├── regulatory_reference
├── exam_preparation
├── clinical_reference
├── library_projection
└── tool_projection
```

## Tipos preservados

- REGULATORY_INSTRUMENT
- GOVERNMENT_POLICY
- CLINICAL_GUIDELINE
- TECHNICAL_MANUAL
- TECHNICAL_STANDARD
- AUTHORITATIVE_REFERENCE

## Change impact

Mudanças externas nunca sobrescrevem o canônico:

```text
NEW SNAPSHOT
→ HASH COMPARE
→ NO_CHANGE ou CHANGE_CANDIDATE
→ VALIDATION
→ CHANGESET
→ NEW VERSION
```

## Neste v0.1

O diretório `regulatory/` está reservado. O piloto `dimensionamento` cita COFEN 743/2024 e Parecer 01/2024 como **driver**, sem armazenar o texto da norma e sem calcular o quadro.
