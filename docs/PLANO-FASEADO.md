# Plano faseado — globais primeiro, particularizadores depois

Roadmap **honesto** para evoluir o repositório atual até a arquitetura NIFS completa, minimizando retrabalho, tokens e duplicação de dados. Inclui estratégia de internacionalização do website (30 locales: pt-BR + 29).

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

**Critério de saída:** novo colaborador sabe onde editar em &lt; 5 min (`docs/ESTRUTURA-REPOSITORIO.md`).

---

## Fase 1 — Dados globais e contratos (prioridade máxima)

**Objetivo:** congelar camada de conhecimento compartilhado antes de adicionar calculadoras.

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

### 1.4 i18n global (chrome + terminologia)

**Não traduzir 205 páginas × 29 idiomas manualmente como estratégia final.**

| Sub-fase | Ação | Economia |
|----------|------|----------|
| 1.4a | Extrair dicionário **global** único: `i18n/global/{lang}.json` (menu, botões, labels comuns) | ~1.500 strings × 1 vez |
| 1.4b | Migrar `lang-selector.js` para consumir JSON (já preparado em `i18n-loader.js`) | Remove hardcode duplicado |
| 1.4c | Terminologia: `localized_labels` nos datasets clínicos | NANDA “Ansiedade” traduzida 1× |
| 1.4d | Alinhar `reference-datasets/global/languages.json` com `i18n-pipeline` (29 locales) | Uma lista autoritativa |

**Idiomas (29 + pt-BR):** en, es, fr, de, it, zh-CN, ja, ar, hi-IN, ru-RU, ko-KR, tr-TR, pl-PL, nl-NL, sv-SE, no-NO, da-DK, fi-FI, cs-CZ, hu-HU, ro-RO, bg-BG, hr-HR, sr-RS, sl-SI, uk-UA, vi-VN, th-TH, id-ID.

**Prioridade de tradução clínica:** es-419 → en → demais (por audiência).

**Critério de saída Fase 1:** Apgar consome NANDA/NIC/NOC **somente por ID**; chrome do DELIVERY troca de idioma sem HTML paralelo; schemas validados no CI.

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

**Critério de saída:** `python3 compiler/build_all.py` regenera DELIVERY a partir de fontes.

---

## Fase 3 — CIR mínimo (inferência clínica)

**Objetivo:** score → recomendações usando grafo + datasets, não strings fixas no JS.

- [ ] Conectar `apgar-edges.json` / `ToolCKO.edges` em `calc-engine-v2.js`
- [ ] Extrair regras Nurse-PaLM para módulo `cir/inference-apgar.js` (testável)
- [ ] Resolver NANDA/NIC/NOC via IDs → labels localizados em runtime
- [ ] Testes unitários com casos clínicos (score 3, 7, 10…)

**Critério de saída:** alterar uma aresta em `apgar_edges.json` muda o plano sem editar HTML.

---

## Fase 4 — Presentation e PDF

**Objetivo:** uma shell; N calculadoras como particularizadores.

- [ ] Template calculadora único (`templates/calculator-shell.html`) + `#tool-config` + CKO
- [ ] IDs DOM estáveis documentados (`#calcNandaText`, `#calcSafetyIpsgList`, …)
- [ ] `populatePrintReport()` + botão Imprimir → `window.print()` **ou** API
- [ ] Segunda calculadora (ex.: Glasgow) só com CKO novo + edges — **sem copiar Apgar HTML**

**Critério de saída:** Glasgow publicada com &lt; 20% do esforço do Apgar.

---

## Fase 5 — Runtime servidor (opcional, escala)

- [ ] API FastAPI: `/calculate`, `/report`, `/terminology/{lang}`
- [ ] PostgreSQL ou Neo4j para grafo (conforme NIFS-500)
- [ ] Autenticação e perfis (datasets `users/`)

**Critério de saída:** browser pode ser só presentation; lógica clínica no servidor.

---

## Fase 6 — Interoperabilidade e IA

- [ ] Export FHIR R4 (Observation, CarePlan) a partir do payload do relatório
- [ ] Nurse-PaLM: RAG sobre datasets + prompts em `metadata/ai_prompt_templates.json`
- [ ] Revisão humana e governança (NIFS-1100)

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

**Não fazer por calculadora:** copiar NANDA/NIC/NOC, traduzir menu/footer, reimplementar PDF, reescrever Nurse-PaLM do zero.

---

## Ordem de execução recomendada (próximas 4 sprints técnicas)

```
Sprint A │ Fase 1.1–1.3  │ schemas + labels localizados em datasets
Sprint B │ Fase 1.4      │ i18n global JSON + migrar lang-selector
Sprint C │ Fase 2 + 3    │ compiler + edges na inferência Apgar
Sprint D │ Fase 4        │ PDF/API wire + piloto Glasgow
```

Paralelizável: revisão humana es-419 no `i18n-pipeline` (Fase 1.4d) enquanto desenvolve compiler.

---

## Riscos honestos

| Risco | Mitigação |
|-------|-----------|
| `reference-website/` diverge do DELIVERY | DELIVERY é canônico; legado só para injetor histórico |
| Escopo NIFS (261 docs) vs entrega | Este plano implementa **subconjunto** alinhado ao site atual |
| Tradução LLM sem revisão | `review_status: machine` até revisão clínica |
| Tokens em chat para 97 calculadoras | Nunca gerar JSON clínico completo no chat — usar compiler + datasets |

---

## Links

- [ESTRUTURA-REPOSITORIO.md](./ESTRUTURA-REPOSITORIO.md)
- [ARQUITETURA-PLATAFORMA-CLINICA.md](./ARQUITETURA-PLATAFORMA-CLINICA.md)
- `i18n-pipeline/PENDENCIAS_I18N.md`
- `NIFS/1500-ROADMAP/`
