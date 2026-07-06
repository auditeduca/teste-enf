# 15 — Grafo clínico, edge layer e caminho para 10/10

> Complementa [doc 13](13-master-data-banco-oficial.md) e [doc 14](14-master-data-sequencia-revisao.md).  
> **Status: `PENDING_REVIEW`** — arquitetura alvo, sem migração até aprovação.

Artefatos:

| Arquivo | Função |
|---------|--------|
| [`relation_dictionary.json`](../datasets/metadata/relation_dictionary.json) | Tipos de relação fixos (sem entidade REL) |
| [`schemas/entity_edge.schema.json`](../datasets/metadata/schemas/entity_edge.schema.json) | Schema de aresta |
| [`master_code_sequence_proposal.json`](../datasets/metadata/master_code_sequence_proposal.json) | Catálogo de entity_codes |

---

## 1. Decisão arquitetural: sem entidade REL

**Não** criar códigos como `REL_BRADEN_NANDA_001` ou sufixo `REL` em entity_codes.

| Camada | O que é | Exemplo |
|--------|---------|---------|
| **NODE** | Entidade clínica com código estável | `BRADEN_SCL_001`, `NANDA_00046`, `NIC_3540` |
| **EDGE** | Relação externa, JSON separado | `{ "from": "BRADEN_SCL_001", "to": "NANDA_00046", "relation_type": "supports_diagnosis" }` |

Identidade da aresta = `(from, relation_type, to)` — não um quarto código artificial.

Tipos permitidos: ver [`relation_dictionary.json`](../datasets/metadata/relation_dictionary.json).  
Proibido sinônimos ad hoc (`related_to`, `linked_with`, `uses`).

---

## 2. CAL vs PRT vs SCL (regra de classificação)

| Sufixo | Critério | Exemplo |
|--------|----------|---------|
| **SCL** | Instrumento validado com scoring clínico | `APGAR_SCL_001`, `BRADEN_SCL_001` |
| **CAL** | Fórmula numérica: inputs → output com unidade | `DRIP_RATE_CAL_001` → gtt/min |
| **PRT** | Checklist, protocolo, framework (sem fórmula) | `9RIGHTS_PRT_001`, `DUAL_CHECK_PRT_001` |

**Correção v2026.2.2:** `9RIGHTS` deixa de ser `CAL` — é protocolo de segurança medicamentosa (`tool_type: protocol`, `calculation_type: checklist`).

CAL exige: `inputs`, `formula`, `output` + unidade. Checklist booleano → **PRT**.

---

## 3. Evolução opcional de domínio (5–10 anos)

Padrão atual (mantido na v2026.2.2):

```
{CONCEPT}_{ARTIFACT}_{SEQ}
```

Extensão futura **opcional** (metadado ou prefixo quando necessário):

```
{DOMAIN}_{CONCEPT}_{ARTIFACT}_{SEQ}
```

| DOMAIN | Área |
|--------|------|
| CLIN | Clínica geral |
| MED | Medicina |
| NUR | Enfermagem |
| PHR | Farmácia |
| NUT | Nutrição |
| SAF | Segurança do paciente |

Campo `domain` no conceito — **sem alterar** entity_codes existentes até decisão explícita.

---

## 4. Metadados enterprise (sem expandir base)

Campos alvo por entidade (template no JSON de proposta):

```json
{
  "lifecycle": {
    "stage": "draft",
    "approved_by": null,
    "approved_date": null,
    "deprecated_reason": null
  },
  "clinical_version": {
    "instrument_version": "1.0",
    "validated_year": 1952,
    "last_review": 2026
  },
  "evidence": {
    "grade": "A",
    "source_type": "guideline",
    "organization": "WHO",
    "citation": "",
    "year": 2026
  },
  "i18n": {
    "pt-BR": { "name": "", "description": "" },
    "en-US": { "name": "", "description": "" }
  }
}
```

Estágios: `draft` → `review` → `validated` → `published` → `deprecated`.

---

## 5. Layout de diretórios (alvo pós-aprovação)

Não manter tudo em um JSON monolítico:

```
datasets/
  ontology/
    concepts.json
    edges.json              ← grafo (from → relation_type → to)
  artifacts/
    scales/
    calculators/
    protocols/
  content/
    flashcards/
    quizzes/
    articles/
  evidence/
    sources.json
  migrations/
    legacy_mapping.json
```

Hoje: proposta consolidada em `metadata/master_code_sequence_proposal.json` para revisão humana.

---

## 6. Caminho para 10/10 **sem** expandir base

Salto de maturidade = **vertical** (computabilidade), não horizontal (mais nós).

| Pilar | Ação |
|-------|------|
| **Triplas clínicas** | Tudo como `(subject) → (predicate) → (object)` |
| **Inference engine único** | IF threshold SCL THEN NANDA THEN NIC THEN NOC |
| **Interface semântica uniforme** | Todo artefato: inputs, outputs, logic/evidence, version |
| **Rule graph** | Decision trees viram grafo de regras composáveis |
| **Schema enforcement** | CAL exige formula+unit; NANDA exige ≥1 NIC; validação CI |
| **Separação de camadas** | Data → Logic → Inference → Output |

Exemplo de regra executável:

```
IF BRADEN_SCL_001.score <= 12
THEN triggers NANDA_00046
THEN maps_to NIC_3540
THEN impacts NOC_1101
```

---

## 7. Agentes clínicos (por que o modelo importa)

Com NODE + EDGE + regras:

- **Agente clínico:** paciente idoso + risco queda → busca `BRADEN`, `MORSE` → propõe NANDA/NIC/NOC com rastreio.
- **Agente documental:** usa `canonical_url`, `legacy_uuid`, `evidence` → gera flashcard/quiz/simulado sem perder proveniência.

---

## 8. Próximo passo técnico (pós-aprovação doc 14)

1. Aprovar padrão de códigos + edge layer.
2. Extrair `edges.json` a partir de `nursing_diagnoses.json` (tool ↔ NANDA).
3. Esboçar `inference_rules.json` para escalas com threshold conhecido (Braden, Morse, Apgar).
4. Validador CI: CAL sem formula, PRT classificado como CAL, aresta com tipo inválido → falha.

→ Regenerar proposta: `python scripts/draft_master_code_sequences.py`
