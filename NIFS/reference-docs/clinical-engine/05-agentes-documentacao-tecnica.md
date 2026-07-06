# Agentes de IA e documentação técnica necessária

Referência: [12-clinical-intelligence-engine.md](../12-clinical-intelligence-engine.md)

---

## 1. Arquitetura com agentes

**Regra:** agentes **não** ficam dentro do núcleo matemático (EKF, particle filter, GLM). O núcleo permanece determinístico/probabilístico auditável; agentes orquestram, explicam e buscam evidência.

```
                    AGENTES (orquestração)
                           |
     +----------+----------+----------+----------+
     |          |          |          |          |
 Clinical   Evidence    Safety    Education   Audit
  Agent      Agent      Agent      Agent     Agent
     |          |          |          |          |
     +----------+----------+----------+----------+
                           |
              Clinical Intelligence Engine
              (V8: belief + inference + control)
                           |
                    datasets/clinical/
                    nkp_api.py
```

### 1.1 Clinical Agent

- **Entrada:** belief, diagnoses, risk index
- **Saída:** hipóteses priorizadas, lacunas de dados (“confirmar lactato”)
- **Não faz:** alterar probabilidades do motor

### 1.2 Evidence Agent

- Busca guidelines, protocolos NKOS, literatura
- Fontes: `datasets/clinical/nursing_protocols.json`, `evidence_grades.json`, links externos curados
- Integração possível com RAG existente (`datasets/rag/`)

### 1.3 Safety Agent

- Aplica `safety_rules.json` + contraindicações
- Pode **bloquear** recomendação antes da UI
- Log de override humano

### 1.4 Education Agent

- Modo estudante: passo a passo, quizzes, contrafactual didático
- Alinhado à página `/sae` e simulados NKOS

### 1.5 Audit Agent

- Gera trilha legível para gestores
- Consolida `audit` do contrato API

---

## 2. Uso de agentes no CALENF-NKD (já existente)

| Componente | Caminho | Papel |
|------------|---------|-------|
| LangGraph code review | `scripts/review/graph.py` | Padrão de workflow agentico |
| DeepSeek client | `scripts/review/deepseek_client.py` | LLM OpenAI-compatible |
| API review | `POST /api/review/run` | Orquestração HTTP |
| UI | `platform/src/pages/CodeReviewPage.jsx` | Interface |

**Reuso para SAE:** criar `scripts/clinical_agents/` espelhando `scripts/review/`:

```
scripts/clinical_agents/
├── config.py
├── clinical_graph.py      # LangGraph: vitals → engine → explain
├── safety_node.py
├── evidence_node.py
└── run_clinical_session.py
```

---

## 3. LLM: papel correto (V9)

| Pode | Não pode |
|------|----------|
| Explicar reasoning em linguagem natural | Decidir probabilidade NANDA |
| Resumir prontuário para o enfermeiro | Prescrever ou substituir protocolo |
| Gerar texto educacional | Ignorar safety layer |
| Mapear texto livre → códigos (assistido) | Ser única fonte de verdade |

---

## 4. Documentação técnica necessária

Estrutura recomendada para avançar de spec → produto:

```
docs/
├── 12-clinical-intelligence-engine.md    ✅ criado
└── clinical-engine/
    ├── README.md                          ✅ índice
    ├── 02-evolucao-versoes.md             ✅
    ├── 03-pendencias-roadmap.md           ✅
    ├── 04-validacao-datasets.md           ✅
    ├── 05-agentes-documentacao-tecnica.md ✅ este arquivo
    ├── 06-avaliacao-mercado.md            ✅
    │
    └── technical/                         📋 a criar na implementação
        ├── 01_product/
        │   ├── visao.md
        │   ├── personas.md
        │   └── casos_uso.md
        ├── 02_architecture/
        │   ├── system_design.md
        │   ├── data_flow.md
        │   └── state_model.md
        ├── 03_ai/
        │   ├── model_card.md
        │   ├── algorithm_spec.md
        │   ├── uncertainty.md
        │   └── validation.md
        ├── 04_clinical/
        │   ├── nanda_mapping.md
        │   ├── nic_mapping.md
        │   ├── noc_mapping.md
        │   └── evidence_matrix.md
        ├── 05_security/
        │   ├── privacy.md
        │   ├── audit.md
        │   └── safety_rules.md
        ├── 06_data/
        │   ├── dataset_card.md
        │   ├── anonymization.md
        │   └── etl_pipeline.md
        └── 07_testing/
            ├── unit_tests.md
            ├── clinical_cases.md
            └── benchmark.md
```

### 4.1 Prioridade de criação

| Ordem | Documento | Quando |
|-------|-----------|--------|
| 1 | `algorithm_spec.md` | Antes de codar V4 MVP |
| 2 | `data_flow.md` | Antes da API |
| 3 | `nanda_mapping.md` | Ao conectar NKOS |
| 4 | `safety_rules.md` | Antes de UI profissional |
| 5 | `model_card.md` | Antes de MIMIC |
| 6 | `clinical_cases.md` | Testes de regressão |

---

## 5. Checklist — posso avançar?

| Pergunta | Resposta |
|----------|----------|
| Tenho taxonomia NANDA/NIC/NOC? | ✅ `datasets/clinical/` |
| Tenho grafo NNN? | ✅ 1500 linkages |
| Tenho arquitetura V3–V8 documentada? | ✅ docs/clinical-engine |
| Tenho motor runtime? | ❌ implementar V4 MVP |
| Tenho dados ICU reais? | 📋 MIMIC após credenciamento |
| Tenho agentes? | 📋 reutilizar padrão LangGraph |
| Tenho validação? | ❌ Fase C roadmap |

**Conclusão:** dá para avançar **agora** em MVP (V4 + API + UI SAE + agentes explicativos). Validação hospitalar exige V8.5 + MIMIC.

---

## 6. Endpoints API sugeridos

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/sae/run` | Entrada vitais + calc → diagnoses + NIC |
| POST | `/api/sae/simulate` | Counterfactual NIC |
| POST | `/api/sae/forecast` | Projeção 24h (V5.3+) |
| GET | `/api/sae/graph` | Subgrafo NNN por diagnóstico |
| POST | `/api/clinical/session` | Agente LangGraph completo |
| GET | `/api/clinical/audit/{id}` | Trilha de sessão |

Integrar em `scripts/nkp_api.py` seguindo padrão de `/api/review/*`.

---

## 7. Segurança de agentes

- Timeout e limite de tokens por sessão
- Não enviar PHI para LLM externo sem anonimização
- Prompts versionados em `datasets/metadata/` ou `scripts/clinical_agents/prompts/`
- Human-in-the-loop para modo **block** override

---

## 8. Próximo passo recomendado

1. Implementar **V4 MVP** em Python (`scripts/clinical_engine/sae_v4.py`) lendo NKOS.
2. Expor **`POST /api/sae/run`**.
3. Adicionar **Clinical Agent** mínimo (LangGraph: engine → explain via DeepSeek).
4. Documentar **`algorithm_spec.md`** e **`clinical_cases.md`** com 10 cenários fixos.
