# Visão geral

## Objetivo

O CKO é o engine declarativo de conteúdo clínico e educacional de enfermagem: objetos canônicos, Regulatory Core, Design System, Site Shell, validadores, auditoria 360 e dois modos de renderização.

## Princípios invariantes

- INTERNAL_FIRST
- ACQUIRE_ONCE
- VALIDATE_ONCE
- VERSION_ON_CHANGE
- REUSE_MANY
- PROJECT_MANY
- NO_SILENT_OVERWRITE
- NO_LLM_REGENERATION_OF_CANONICAL_CONTENT

## Escopo consolidado

- conteúdo educacional e clínico (P/M/S/E no desenho; v0.1 entrega um lote piloto);
- Regulatory Core e referências autoritativas;
- engine canônico;
- renderer;
- templates e contratos de assets;
- validators;
- fábrica de provas anteriores (especificada);
- monitor regulatório (especificado);
- CMS/Inspector read-only;
- auditoria 360;
- render inline para preview;
- render fetch para produção sem CDN.

## Regra de ouro

Conhecimento canônico validado não é regenerado. Novos usos são projeções do conhecimento existente.
