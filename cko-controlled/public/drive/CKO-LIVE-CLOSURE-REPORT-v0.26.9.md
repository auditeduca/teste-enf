# CKO Live Closure Report — v0.26.9

**Projeto:** Calculadoras de Enfermagem  
**Baseline:** v0.26.7  
**Checkpoint:** v0.26.9  
**Data:** 21/08/2026

## Resultado executivo

Esta rodada não reabriu o arquivo histórico. A baseline v0.26.7 permaneceu íntegra e o trabalho foi executado sobre estado vivo do Supabase e fontes oficiais. Foram fechados AUD-SEC-003, AUD-SEC-001, AUD-OPS-002 e AUD-REG-001.

O monitor regulatório agora possui enqueue diário, worker agendado, aquisição endurecida, diff, lineage e comportamento fail-closed. Três alertas COFEN inicialmente detectados foram reperformed: o SHA-256 do bloco normativo `<article>` permaneceu idêntico em todos os casos, classificando-os como mudança não normativa de chrome/template. O worker foi elevado para v2 com normalização ARTICLE_FIRST_HTML.

## Estado legal controlado

Lei 7.498/1986 e Decreto 94.406/1987 foram qualificados com a categoria `NO_EXPRESS_REVOCATION_RECORDED`, porque o registro oficial da Câmara informa que não consta revogação expressa. Essa categoria não é sinônimo de uma opinião jurídica irrestrita de vigência universal. O Decreto tem `effective_from=1987-06-09`, com base no art. 16 e na publicação oficial.

## Findings ainda abertos

1. **P0 — FIND-HCD-LIVE-RUNTIME-20260821.** Runtime público ainda diverge da baseline governada: Braden apresenta estado clínico pré-cálculo e mensagem NANDA/raciocínio clínico; Gotejamento apresenta `0 gotas/min` antes do cálculo.
2. **P1 — FIND-AI-001.** `DEEPSEEK_API_KEY` ausente; AI permanece HOLD/fail-closed.
3. **P1 — FIND-REL-VERCEL-BINDING-20260821.** Equipe Vercel conectada sem projetos e GitHub sem repositórios acessíveis; não há canal controlado de promoção para o runtime público.

## Claims

Continuam proibidas alegações de certificação ISO, conformidade HCD integral, conformidade WCAG integral, aprovação clínica de produção ou deploy governado em produção até que as evidências correspondentes existam.

## Próxima fronteira

O próximo passo não é redesenhar Master Data ou Regulatory Core. É obter/bindar o código fonte/host real do site público, aplicar o remediation spec deste delta, reperfazer HCD/browser E2E e então fechar o release binding. A configuração da chave DeepSeek pode ocorrer em paralelo, mas não bloqueia aquisição regulatória determinística.
