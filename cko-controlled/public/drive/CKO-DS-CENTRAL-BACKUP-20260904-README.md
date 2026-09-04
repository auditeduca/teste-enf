# CKO — Backup Central Design System / Visual / Builder

**Backup ID:** `CKO-DS-CENTRAL-BACKUP-20260904-0445`  
**Data local de referência:** 2026-09-04 04:45 BRT  
**Escopo:** execução central de Design System, Visual System, Templates, Builder, inventário e auditoria.  

## O que este backup é
Este pacote é um **backup de recuperação da execução central atual**. Ele contém todas as fontes canônicas, registries, manifestos, auditorias, builders e evidências que estavam materializados e utilizados na execução no momento do congelamento, além do estado operacional, conversa organizada, manifesto e hashes.

## O que este backup não é
Ele **não é uma cópia binária integral dos 8.893 itens da ChatGPT Library nem de todo o Google Drive**. O universo físico completo continua referenciado pelos ledgers/manifestos e pela enumeração da execução. O objetivo deste backup é permitir **retomada sem perda do trabalho central**.

## Fontes-chave incluídas
- `official-design-system.v2.json` — autoridade canônica ativa.
- `design-system-binding-registry.v1.json` — 850 bindings.
- `platform_component_registry_37.json` — 37 componentes de plataforma.
- `cko_design_system_internal_atoms.json` — controles internos atômicos.
- `template-registry.json` e `page-template-registry.v2.json`.
- `visual-resource-registry.json`.
- `PACKAGE_MANIFEST_v6_5_0.json` — manifesto técnico de 5.474 arquivos.
- `MASTER_DEPENDENCY_GRAPH_v6_5_1_R3.json`.
- `MASTER_ARTIFACT_INVENTORY_v6_5_1_R3.json`.
- auditoria histórica de 1.284 assets visuais.
- pesquisa visual, direitos/proveniência e candidatos de imagem.
- builders e templates materializados.
- instrução-mestra vigente.

## Retomada
Começar por `07_CONVERSATION_HANDOFF/RECOVERY_HANDOFF.md` e `07_CONVERSATION_HANDOFF/RUN_STATE.json`.
