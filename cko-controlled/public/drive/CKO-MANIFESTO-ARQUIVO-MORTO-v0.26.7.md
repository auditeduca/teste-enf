# Manifesto de Arquivamento e Cutover — Calculadoras de Enfermagem

**ID:** `CKO-ARCHIVE-CUTOVER-20260821-001`  
**Data:** 21/08/2026  
**Baseline ativa:** `v0.26.7`  
**SHA-256:** `a8c173c12cb6c747631263f829113906662778dd4f75cab9c92b6a15a672731f`

## Declaração

O conteúdo histórico do projeto foi inventariado, analisado e reconciliado antes deste cutover. A partir deste marco, arquivos históricos deixam de ser fonte operacional corrente e passam a **Arquivo Morto**. Para trabalho ordinário, a única base documental ativa é o pacote consolidado `v0.26.7` e seus futuros changesets controlados.

## Inventário arquivado

- Origem: `/Calculadoras de Enfermagem`
- Quantidade: **224 artefatos históricos**
- Destino: `/Arquivo Morto/Calculadoras de Enfermagem - Historico pre-v0.26.7`
- Estado: `ANALYZED_AND_SUPERSEDED`
- Regra: `DO_NOT_USE_AS_CURRENT_SOURCE`
- Reabertura permitida somente para auditoria histórica, reperformance forense ou rollback.

## Baseline que substitui o histórico

- Arquivo: `Calculadoras-de-Enfermagem-CKO-Consolidado-v0.26.7.zip`
- Arquivos contidos: **471**
- Tamanho descompactado: **51989876 bytes**
- Status: `CANONICAL_WORKING_BASELINE`

## Vercel

A equipe conectada `leivisml-7739s-projects` foi verificada e retornou **0 projetos acessíveis**. Portanto, não havia projeto/deployment live para excluir. Referências históricas ao Vercel ficam arquivadas com o histórico e não devem ser usadas para inferir ambiente ativo. A conexão Vercel não foi removida.

## Ordem de fontes para as próximas tarefas

1. baseline ativa `v0.26.7`;
2. estado/evidência canônica live do Supabase quando a tarefa exigir verificação de runtime;
3. APIs oficiais quando houver aquisição ou atualização;
4. Arquivo Morto apenas quando a tarefa for explicitamente histórica, forense ou rollback.

## Atestação

Os artefatos históricos foram considerados na revisão documental, reconciliação de políticas, matriz de supersession e Auditoria 360 que originaram a baseline consolidada. **Não é necessário reabrir individualmente o conteúdo anterior em tarefas normais.**
