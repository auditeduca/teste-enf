# Marco de instituições homologadas — CKO-CART-001

Documento interno de governança. A página pública exibe apenas selos resumidos (`Fonte homologada` / `Leitura complementar`), sem a rubrica completa de scoring.

> Índice completo dos arquivos do delivery: [`CKO-CART-001-LEIA-ME.md`](./CKO-CART-001-LEIA-ME.md).

## Objetivo

Classificar fontes usadas no recurso Carrinho de Emergência quanto a relevância clínica/regulatória e confiabilidade editorial, alinhado ao domínio: carrinho/PCR/segurança de medicamentos/urgência.

## Critérios (checklist interno)

| Critério | Peso | Evidência esperada |
|----------|------|--------------------|
| Missão assistencial ou de pesquisa em saúde | 1.0 | Estatuto, página institucional |
| Publicação peer-review ou POP institucional auditável | 1.5 | DOI, SciELO, PDF de POP com versão |
| Órgão regulador (COFEN/COREN/MS/ANVISA) | 2.0 | Norma, parecer, resolução |
| Hospital de excelência / acreditação (JCI etc.) | 0.8 | Contexto; não substitui norma BR |
| Atualização recente (≤ 5 anos ou norma vigente) | 1.0 | Data no documento |
| Idioma acessível à equipe BR (pt-BR preferencial) | 0.5 | Conteúdo principal |
| Conflito de interesse declarado / baixo risco comercial | 0.7 | Disclosure ou órgão público |

## Status

- `homologada` — pode receber selo público “Fonte homologada”.
- `complementar` — selo “Leitura complementar”; útil, mas não normativa BR principal.
- `pendente_revisao` — aguarda nova verificação.
- `rejeitada` — não usar na página.

## Relatedness (0–1)

Score programado no validador: URLs da página devem existir na base; se o tema não tocar carrinho/PCR/segurança de meds, flag `relatedness_low` (< 0.5) no inventário interno.

## Validação programada

`tools/validate-manifest.py` carrega `data/institutions.homolog.internal.json` e:

1. Confere que `homologInstitutions.publicSeals[].institutionId` existe na base.
2. Confere que `references[].institutionId` (quando presente) existe e tem `relatedness >= 0.5` ou registra warning.
3. Não expõe notes internas no HTML público.

## Revisão

- Última revisão do marco: 2026-08-04
- Próxima revisão sugerida: 2027-02-04
