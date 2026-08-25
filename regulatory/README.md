# Regulatory Core

Este diretório guarda instrumentos regulatórios canônicos e o índice de linhagem.

Nenhum snapshot de norma está materializado no v0.1. O objeto `dimensionamento` aponta o driver COFEN 743/2024 / Parecer 01/2024, mas **não** armazena o texto da norma.

Contratos:

- `schemas/regulatory-event.schema.json`
- `schemas/trust-assessment.schema.json`
- `schemas/evidence-manifest.schema.json`

Regra: snapshot externo nunca sobrescreve o canônico. Hash compare → CHANGE_CANDIDATE → validação → changeset → nova versão.
