# Plano faseado — globais primeiro, particularizadores depois

Roadmap para evoluir o repositório com **execução 100% de cada fase** antes de avançar. Foco em **padronização** (schemas, CKO, DOM, CSS) e **responsividade total** (mobile, tablet, desktop) em todo artefato entregue.

**Não é um plano de documentação:** cada fase melhora código e dados existentes ou cria o que falta de implementação.

## Meta do programa

| Princípio | Significado |
|-----------|-------------|
| **100% por fase** | Nenhuma fase é dada por encerrada com itens parciais; checklist da fase zerado antes da próxima |
| **Padronização** | Mesmos contratos (CKO 3.0, IDs DOM, bundles gerados, breakpoints CSS) em todas as ferramentas |
| **Responsividade total** | Layout, formulários, painéis clínicos e PDF pré-visualização usáveis em viewport estreita e ampla |
| **Sem retrabalho de tradução** | Fases 5–6 **não iniciam** tradução em massa sem autorização explícita (há trabalho paralelo em andamento) |

## Por que globais primeiro?

| Se começarmos pelas calculadoras | Se começarmos pelos globais |
|----------------------------------|-----------------------------|
| NANDA/NIC/NOC copiados em cada CKO/HTML | Uma fonte; CKO só referencia IDs |
| 97 × 29 traduções de termos iguais | Termo traduzido 1× no dataset |
| Edição clínica em N lugares | Atualização em 1 JSON + rebuild |
| Inferência inconsistente entre escalas | CIR lê o mesmo grafo/terminologia |

**Regra:** nenhum texto clínico canônico (diagnóstico, intervenção, medicamento, meta internacional) deve ser duplicado dentro de `apgar-cko.json` ou HTML — apenas referências (`nanda_id`, `nic_code`, …) e texto **exclusivo** da ferramenta (ex.: “recém-nascido ≥35 semanas”).

---

## Fase 0 — Higiene do repositório ✅ (esta entrega)

**Objetivo:** um único caminho canônico por artefato.

| Entrega | Status |
|---------|--------|
| `_archive/` com exports, snapshots, scripts one-shot | ✅ |
| `docs/` com índice, estrutura, arquitetura, plano | ✅ |
| `scripts/README.md` (ativos vs arquivados) | ✅ |
| Raiz sem `preview_apgar.html`, `apgar-completo/` | ✅ |

**Critério de saída Fase 0:** ✅ concluída.

---

## Fase 1 — Dados globais e contratos (prioridade máxima)

**Objetivo:** congelar camada de conhecimento compartilhado antes de adicionar calculadoras.

**Inclui responsividade:** tokens CSS globais e grids do chrome (`site-styles.css`, partials) validados em breakpoints definidos (ex.: 360px, 768px, 1280px).

### 1.1 Inventário e schema

- [ ] Validar `schema_version` em todos os JSON de `reference-datasets/`
- [ ] Documentar mapa entidade → arquivo (ou gerar de `metadata/canonical_registry.json`)
- [ ] JSON Schema por domínio (`clinical/`, `ontology/`, `global/`)
- [ ] CI: `scripts/ready.sh` ou job que falha se JSON inválido

### 1.2 Terminologia clínica unificada

| Dataset | Uso |
|---------|-----|
| `clinical/nursing_diagnoses.json` | NANDA-I |
| `clinical/nursing_interventions.json` | NIC |
| `clinical/nursing_outcomes.json` | NOC |
| `clinical/nnn_linkages.json` | Ligações NNN |
| `clinical/medication_dictionary.json` | Medicamentos |
| `clinical/patient_safety_goals.json` | Metas IPSG |
| `ontology/*_edges.json` | Arestas por domínio/escala |

- [ ] Padronizar campos `id`, `code`, `label`, `localized_labels: { "pt-BR", "en", … }`
- [ ] Remover cópias redundantes em `DELIVERY/js/modules/data/nanda.json` (passar a fetch do dataset ou bundle gerado)

### 1.3 CKO schema 3.0 congelado

- [ ] Publicar schema em `NIFS/DELIVERY/js/modules/schemas/cko-v3.schema.json` (evoluir v1)
- [ ] Definir blocos obrigatórios: `meta`, `calculator`, `profiles`, `clinical_links`, `localization`
- [ ] Apgar como **referência de conformidade** (`CKO-APGAR-001.json`)

### 1.4 i18n — infraestrutura apenas (sem tradução em massa)

Preparação técnica para quando as Fases 5–6 forem autorizadas. **Não** dispara tradução clínica nem sobrescreve trabalho já feito em paralelo.

| Sub-fase | Ação |
|----------|------|
| 1.4a | Estrutura `i18n/global/{lang}.json` (chrome) — chaves, não conteúdo novo |
| 1.4b | `lang-selector.js` consumir JSON via `i18n-loader.js` |
| 1.4c | Campo `localized_labels` nos datasets clínicos (schema pronto; pt-BR preenchido) |
| 1.4d | Lista única de locales alinhada a `languages.json` e `i18n-pipeline` |

**Critério de saída Fase 1 (100%):**

- [ ] Todos os itens 1.1–1.4 marcados
- [ ] Apgar consome NANDA/NIC/NOC **somente por ID**
- [ ] CI valida JSON e schemas
- [ ] Chrome responsivo nos partials compartilhados (header, footer, toolbar a11y)

---

## Fase 2 — NIFS Compiler (artefatos derivados)

**Objetivo:** scripts que **geram** bundles para runtime — humanos editam datasets/CKO, não JS.

| Artefato gerado | Fonte |
|-----------------|-------|
| `DELIVERY/js/modules/data/apgar-cko.json` | `CKO-APGAR-001.json` + sync |
| `DELIVERY/js/bundles/clinical-terminology.{lang}.json` | `reference-datasets/clinical/*` |
| `DELIVERY/js/bundles/edges-apgar.json` | `ontology/apgar_edges.json` |
| Índice de ferramentas | `clinical/clinical_tools_catalog.json` |

- [ ] Unificar `build_apgar_cko.py` em `compiler/build_tool.py --tool apgar`
- [ ] Manifest de versões (`artifacts/manifest.json`) para cache busting
- [ ] Proibir edição manual de artefatos gerados (comentário + CI diff)

**Critério de saída Fase 2 (100%):**

- [ ] `python3 compiler/build_all.py` regenera DELIVERY a partir de fontes
- [ ] Manifest de versões publicado; diff CI bloqueia edição manual de bundles

---

## Fase 3 — CIR mínimo (inferência clínica)

**Objetivo:** score → recomendações usando grafo + datasets, não strings fixas no JS.

- [ ] Conectar `apgar-edges.json` / `ToolCKO.edges` em `calc-engine-v2.js`
- [ ] Extrair regras Nurse-PaLM para módulo `cir/inference-apgar.js` (testável)
- [ ] Resolver NANDA/NIC/NOC via IDs → labels localizados em runtime
- [ ] Testes unitários com casos clínicos (score 3, 7, 10…)

**Critério de saída Fase 3 (100%):**

- [ ] Alterar aresta em `apgar_edges.json` muda o plano sem editar HTML
- [ ] Todos os painéis do fluxo clínico (`#calcClinicalFlow`) populados via IDs + datasets

---

## Fase 4 — Presentation e PDF

**Objetivo:** uma shell; N calculadoras como particularizadores.

- [ ] Template calculadora único (`templates/calculator-shell.html`) + `#tool-config` + CKO
- [ ] IDs DOM estáveis documentados (`#calcNandaText`, `#calcSafetyIpsgList`, …)
- [ ] `populatePrintReport()` + botão Imprimir → `window.print()` **ou** API
- [ ] Segunda calculadora (ex.: Glasgow) só com CKO novo + edges — **sem copiar Apgar HTML**

**Critério de saída Fase 4 (100%):**

- [ ] Template shell reutilizável documentado e usado pela 2ª calculadora
- [ ] PDF/API ligados ao botão Imprimir
- [ ] Apgar + piloto **100% responsivos** (formulário, abas de perfil, fluxo clínico, relatório pré-impressão)
- [ ] Checklist de IDs DOM estáveis passa em ambas as ferramentas

---

## Fase 5 — Scanner 100% em português (pt-BR)

**Objetivo:** inventário exaustivo e deduplicado de **todo** texto visível da ferramenta (e do site piloto) em português, como base única para qualquer tradução futura.

**Escopo técnico (implementação, não documentação):**

- [ ] Evoluir `i18n-pipeline/scanner_deep.py` (ou equivalente no compiler) para cobertura **100%** por página/ferramenta: corpo HTML, atributos (`aria-label`, `title`, `placeholder`), metas, `tool-config` JSON, textos CKO em pt-BR
- [ ] Corpus global deduplicado: `extracted/corpus_pt.json` (ou path canônico único) com hash por string
- [ ] Relatório de cobertura: % por página, strings órfãs, strings só em HTML vs só em JSON
- [ ] Integração com Apgar piloto primeiro; depois extensível ao catálogo (`clinical_tools_catalog.json`)

**O que esta fase NÃO faz:**

- Não traduz para outros idiomas
- Não sobrescreve arquivos em `reference-website/` ou `i18n-pipeline/translations/`
- Não assume que traduções existentes estão erradas

**Critério de saída Fase 5 (100%):**

- [ ] Scanner reporta **100%** das strings da ferramenta piloto (Apgar) em pt-BR
- [ ] Corpus deduplicado versionado e reproduzível (`python3 … --tool apgar`)
- [ ] Gap report gerado (JSON/CSV) pronto para cruzar com inventário da Fase 6

---

## Fase 6 — Inventário de traduções e continuidade

**Objetivo:** cruzar o corpus pt-BR (Fase 5) com **tudo que já foi traduzido** (incluindo trabalho paralelo fora do repo) e continuar só o que falta.

### 🔒 Portão de autorização

> **Não iniciar a Fase 6 sem autorização explícita do responsável pelo conteúdo.**
>
> Motivo: há tradução em andamento em paralelo; o agente não deve retraduzir nem sobrescrever material já validado.

**Quando autorizado, executar nesta ordem:**

1. **Inventário do que existe** — varrer sem modificar:
   - `i18n-pipeline/translations/{lang}/`
   - `reference-website/{lang}/`
   - `NIFS/DELIVERY/i18n/`
   - CKO `localization` em ferramentas já publicadas
   - Artefatos externos que o responsável indicar (planilhas, ZIPs, branches)
2. **Cruzamento** — corpus pt-BR × traduções por locale: `covered`, `partial`, `missing`, `divergent`
3. **Plano de continuidade** — fila só de `missing`/`divergent` aprovados; reutilizar `covered` sem reprocessar
4. **Execução incremental** — idioma e ferramenta por prioridade acordada na autorização (ex.: es-419 → en)

**Critério de saída Fase 6 (100%):**

- [ ] Relatório de cobertura por idioma e por ferramenta (não necessariamente 29 idiomas × 97 calculadoras de uma vez — escopo definido na autorização)
- [ ] Zero retradução de strings já marcadas como `reviewed` ou equivalente
- [ ] Páginas entregues no escopo autorizado passam QA de responsividade no idioma alvo

---

## Fora do escopo atual (sem número de fase)

Itens da spec NIFS que **não** entram neste ciclo até nova decisão de produto:

- Runtime servidor (FastAPI + PostgreSQL/Neo4j)
- Export FHIR R4 em produção
- Nurse-PaLM com RAG e modelo dedicado

Podem ser retomados após Fases 1–6 no escopo acordado.

---

## Matriz: o que fazer por calculadora (particularizador)

Quando Fase 1–3 estiverem estáveis, cada **nova** escala exige apenas:

| Item | Tamanho estimado | Reutiliza |
|------|------------------|-----------|
| `CKO-{TOOL}-001.json` | 15–40 KB | schema, perfis, localization |
| `ontology/{tool}_edges.json` | 5–20 KB | tipos de aresta globais |
| Entrada no catálogo | 1 registro | `clinical_tools_catalog.json` |
| HTML shell | 0 (gerado) ou cópia mínima | partials, JS globais |
| Tradução | bloco `localization` no CKO | terminologia global já traduzida |

**Tradução em massa:** só após Fase 6 autorizada, usando corpus da Fase 5.

**Não fazer por calculadora:** copiar NANDA/NIC/NOC, traduzir menu/footer, reimplementar PDF, reescrever Nurse-PaLM do zero.

---

## Ordem de execução

```
Fase 1 (100%) → Fase 2 (100%) → Fase 3 (100%) → Fase 4 (100%)
                                                      │
                                                      ▼
                                            Fase 5 — scanner pt-BR 100%
                                                      │
                                                      ▼
                              Fase 6 — 🔒 só com autorização — inventário + continuidade
```

Não avançar de fase com checklist incompleto.

---

## Riscos honestos

| Risco | Mitigação |
|-------|-----------|
| `reference-website/` diverge do DELIVERY | DELIVERY é canônico; legado só para inventário na Fase 6 |
| Escopo NIFS (261 docs) vs entrega | Fases 1–4 = MVP replicável; 5–6 = i18n com gate |
| Retraduzir trabalho paralelo | Fase 6 bloqueada sem autorização; inventário antes de escrever |
| Tokens em chat para 97 calculadoras | Compiler + corpus; nunca gerar JSON clínico completo no chat |
| Layout quebrado em mobile | Responsividade no critério de saída de cada fase |

---

## Links

- [ESTRUTURA-REPOSITORIO.md](./ESTRUTURA-REPOSITORIO.md)
- [ARQUITETURA-PLATAFORMA-CLINICA.md](./ARQUITETURA-PLATAFORMA-CLINICA.md)
- `i18n-pipeline/PENDENCIAS_I18N.md`
- `NIFS/1500-ROADMAP/`
