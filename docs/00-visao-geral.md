# Visão geral

## Objetivo

O CKO é a plataforma governada Calculadoras de Enfermagem: Master Data, Regulatory Core, camadas governadas, objetos canônicos, Design System, Site Shell, validadores, auditoria 360 e dois modos de renderização.

A constituição operacional é `docs/constitution/CKO-INS-AI-PROJECT-001.md`. GitHub é o store Day Zero.

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
- Admin e Inspector read-only sobre os mesmos JSON;
- auditoria 360;
- render inline para preview;
- render fetch para produção sem CDN.

## Regra de ouro

CKO-MD FIRST, CKO-REG SECOND. Conhecimento canônico validado não é regenerado. Novos usos são projeções do conhecimento existente.
