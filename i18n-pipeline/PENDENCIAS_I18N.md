# NIFS — Pendências do Pipeline de Internacionalização (i18n)

**Versão:** 1.1.0
**Data:** 2026-07-06
**Status:** Fase 1 e 2 concluídas · Correção de hreflang (Fase 2.5) concluída · Fase 3 pendente
**Entregável:** `nkos-site-i18n-completo-v1.zip` (277MB) salvo no Google Drive — File ID `1zlabZR4xmLLP_FpYb9W-oLAdgYJvLHwU`

---

## Resumo executivo

O site calculadorasdeenfermagem.com.br tinha um problema de **hreflang fantasma**: várias páginas já declaravam `<link rel="alternate" hreflang="...">` para até 20+ idiomas cujas páginas nunca existiram (404 potencial para o Google e para usuários). Esse texto/estrutura era persistente em todas as páginas.

Construímos um pipeline automatizado (scanner → dicionário de termos → injetor) que:
1. Elimina o hreflang fantasma, gerando de fato as páginas correspondentes.
2. Traduz a estrutura comum (chrome, seções, labels) de 100% das 205 páginas em 29 idiomas.
3. Documenta o que ainda falta para tradução clínica completa.

---

## Fase 1 — Scanner (✅ concluído)

Script: `NIFS/i18n-pipeline/scanner.py`

- Varre as 205 páginas HTML do site (exclui templates/partials internos).
- Extrai: SEO (title/description/h1/subtitle), `tool-config` JSON (97 calculadoras), textos estáticos visíveis (labels, headings, tips, etc).
- **Corrigiu bug real de dados**: o campo `"emoji"` dentro do JSON de 97 calculadoras continha HTML com aspas não escapadas (`<i class="fa fa"></i>`), quebrando o parse JSON. Função `repair_json()` resolve isso — 0 erros após a correção.
- Resultado: 2.681 strings únicas extraídas, 86 se repetem em ≥5 páginas (candidatas a dicionário comum).

## Fase 2 — Dicionário comum + Injetor (✅ concluído)

Arquivos: `common_translatable.json`, `common_proper_nouns.json`, `common_translations.json`, `injector.py`

- Das 86 strings comuns, 32 são **nomes próprios de escalas** (Glasgow, Braden, APGAR, NIHSS, SOFA, etc.) — mantidos sem tradução por convenção clínica internacional.
- As **54 termos restantes foram traduzidos para os 29 idiomas** do site (pt-BR é a origem) — 1.566 unidades de tradução, 100% de cobertura, sem lacunas.
- O injetor identifica os **2 formatos de template** existentes no site (calculadoras vs. artigos/biblioteca) e corrige em ambos: `<html lang>`, `canonical`, bloco `hreflang` (recíproco: pt-BR ⇄ idioma ⇄ x-default), links relativos.
- **Rodado em produção**: 205 páginas × 29 idiomas = **5.945 páginas geradas** em `reference-website/{en,es,fr,de,it,zh,ja,ar,hi,ru,ko,tr,pl,nl,sv,no,da,fi,cs,hu,ro,bg,hr,sr,sl,uk,vi,th,id}/`.
- Piloto de tradução clínica **completa** (não só chrome) feito manualmente em `es/apgar.html`, como prova de conceito e template de referência para a Fase 3.

### Idiomas cobertos (29 + pt-BR = 30 total)
en, es, fr, de, it, zh-CN, ja, ar, hi-IN, ru-RU, ko-KR, tr-TR, pl-PL, nl-NL, sv-SE, no-NO, da-DK, fi-FI, cs-CZ, hu-HU, ro-RO, bg-BG, hr-HR, sr-RS, sl-SI, uk-UA, vi-VN, th-TH, id-ID

> Nota: registros anteriores de memória mencionam "28 idiomas" — a lista real e ativa em `site_locales.py` (código-fonte original do NKOS) tem 29 não-portugueses. Usamos essa lista como autoritativa.

---

## Fase 3 — Tradução clínica única (🟡 EM ANDAMENTO — arquitetura de corpus, 2026-07-06)

**Automatizada via API DeepSeek** (chave em `C:\Github\CALENF-NKD\.env`; modelo `deepseek-v4-flash` exige `"thinking": {"type": "disabled"}`). Nova arquitetura em 3 peças:

1. **`scanner_deep.py`** — extrai TODOS os nós de texto do corpo + atributos visíveis + metas (cobre os 108 artigos/calculadoras antigas sem tool-config que a Fase 1 sub-extraía). Saída: `extracted/pages_deep/`.
2. **`build_corpus.py`** — consolida corpus global pt deduplicado: `extracted/corpus_pt.json` — **19.603 strings únicas / 1,2M chars** (dedupe entre páginas economiza 51% das 39.967 ocorrências).
3. **`translate_clinical.py`** — traduz consultando/alimentando o **dicionário global por idioma** (`translations/{lang}/_global.json`, `review_status: machine`): cada string traduzida 1× e reaproveitada; terminologia consistente. Aplica por página: tool-config inteiro (re-serializado válido — corrige o bug do emoji), substituições diretas + delimitadas no corpo, e troca estrutural de title/metas/JSON-LD (idempotente, usa a raiz pt como fonte).

**Status es-419**: top-20 calculadoras prontas e validadas (Glasgow, APGAR, Braden, NEWS2, SOFA, Morse, etc.); rodada `--all` das 205 páginas em execução. Idiomas restantes = re-rodar `--all --lang XX`.

**Pendências da fase**: revisão humana das traduções (`review_status: machine` → `reviewed`); `news.html` é calculadora de formato antigo sem tool-config (só texto profundo); ~86 artigos dependem só do scanner profundo.

### Referência do conteúdo por calculadora (estimativa original)

| Campo | Conteúdo | Qtd. aprox. por calculadora |
|---|---|---|
| `overview` | objetivo, indicação, população-alvo | 3 strings |
| `calculator.inputs` | labels, descrições, opções de cada parâmetro | ~15-25 strings |
| `interpretation.ranges` | implicações clínicas + recomendações por faixa | ~9 strings |
| `sae` | diagnósticos NANDA-I, resultados NOC, intervenções NIC | ~10 strings |
| `evidence` | fundamentação, histórico, validação, limitações, referências | ~5 strings |
| `learning` | dicas, exemplos, quiz | ~10 strings |
| corpo HTML estático (seção "Sobre", "Dicas", FAQ) | textos não capturados pelo dicionário comum | ~15 strings |

**Total estimado: ~2.600 strings únicas × 29 idiomas ≈ 75.000 unidades de tradução.**

Isso não é automatizável por script — requer tradução real (LLM ou humana) calculadora por calculadora, como foi feito manualmente para APGAR/ES neste ciclo (76 substituições, ~40 minutos de trabalho para 1 calculadora em 1 idioma).

### Estratégia recomendada para completar
1. **Priorizar por idioma primeiro**: fechar as 97 calculadoras em espanhol (maior audiência, `es-419`) antes de espalhar para os outros 28.
2. **Priorizar por calculadora**: as ~20 calculadoras mais acessadas (Glasgow, APGAR, Braden, NEWS, SOFA, Morse) primeiro.
3. Usar o padrão já estabelecido em `es/apgar.html` como gabarito de estrutura JSON de tradução (`translation_tier`, `review_status` — convenção já existente no codebase original em `scripts/apgar_agents/prompts/translate.md`).
4. Rodar em sessões dedicadas (esse volume não cabe em uma única sessão de chat).

---

## Fase 2.5 — Correção global de hreflang (✅ concluída em 2026-07-06)

Auditoria da cópia local (`nkos-site-i18n-completo-v1/`) encontrou três defeitos ativos de SEO:

1. **Reciprocidade quebrada**: as 205 páginas raiz (pt-BR) declaravam só 3 alternates (`pt-BR`, `es-419`, `x-default`). As 5.945 páginas geradas apontavam para a raiz, mas a raiz não apontava de volta — o Google ignora alternates sem link bidirecional; só o espanhol estava recíproco.
2. **Hreflang fantasma nos artigos**: páginas de artigo (ex: `5-hs-da-paradacardiorespiratoria.html`) ainda tinham o bloco antigo de 19 idiomas (códigos minúsculos, sem `x-default`) — confirmando o achado técnico da v1.0.0.
3. **Códigos inconsistentes** no mesmo cluster (`es` nas páginas geradas vs `es-419` na raiz).

**Correção aplicada** por `i18n-pipeline/fix_hreflang.py` (novo, re-executável):
- Reconstrói o bloco hreflang com base nos **arquivos que existem no disco** — fantasma eliminado por construção.
- Bloco único e idêntico em todo o cluster: `pt-BR` + 29 idiomas + `x-default` = 31 alternates por página, inserido após o `canonical`.
- **6.150 arquivos reescritos** (205 clusters × 30 páginas), 19.452 tags antigas removidas.
- Limpeza adicional: blocos fantasma removidos de `ativar-admin.html`, `offline.html` e `ja/politicadeacesibilidade.html` (este último é um **órfão** — nome com typo, sem contraparte na raiz; candidato a exclusão).

> Se o idioma faltante for restaurado ou novos idiomas forem gerados, basta rodar `python i18n-pipeline/fix_hreflang.py` de novo (aceita `--dry-run`).

## Achado técnico remanescente

O site original completo tem ~944 páginas adicionais não incluídas neste pipeline (as 205 auditadas são o subconjunto atual). Se essas páginas forem publicadas, rodar o scanner e o `fix_hreflang.py` sobre elas antes.

---

## Arquivos do pipeline

```
NIFS/i18n-pipeline/
├── scanner.py                          # Fase 1
├── injector.py                         # Fase 2
├── PENDENCIAS_I18N.md                  # este arquivo
└── extracted/
    ├── scan_report.json
    ├── common_dictionary.json          # 86 termos brutos (freq ≥5)
    ├── common_translatable.json        # 54 termos a traduzir
    ├── common_proper_nouns.json        # 32 nomes próprios (não traduzir)
    ├── common_translations.json        # 54 termos × 29 idiomas (completo)
    └── pages/*.json                    # conteúdo único extraído por página (205 arquivos)
```

## Entregável salvo no Drive

- **Arquivo:** `nkos-site-i18n-completo-v1.zip` (277MB)
- **File ID:** `1zlabZR4xmLLP_FpYb9W-oLAdgYJvLHwU`
- **Conteúdo:** `reference-website/` completo (site pt-BR original + 5.945 páginas geradas em 29 idiomas) + `i18n-pipeline/` (scripts + dicionários + relatórios)
