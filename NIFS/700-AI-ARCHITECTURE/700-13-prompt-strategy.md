# NIFS-700-13: Prompt Strategy

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-13                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estratégia de prompt engineering do Nurse-PaLM para integrar LLMs no raciocínio clínico.

## 2. Prompt Architecture

```
System Prompt (role + constraints + safety)
    ↓
Clinical Context (patient state + observations)
    ↓
Retrieved Knowledge (RAG + graph data)
    ↓
Task Instruction (diagnose | plan | explain)
    ↓
Output Format (JSON schema enforced)
    ↓
LLM → Structured Output
```

## 3. Prompt Templates

O NKOS já define templates em `datasets/metadata/ai_prompt_templates.json`:

| Template | Purpose | Output |
|----------|---------|--------|
| `validate_dataset` | Validar dataset NKOS | JSON com errors/warnings |
| `validate_hub_seo` | Validar SEO de hub | JSON com score/recommendations |
| `generate_article_outline` | Gerar outline de artigo | JSON com sections |
| `generate_protocol_card` | Gerar card de protocolo | JSON com protocol card |
| `graph_relations_summary` | Sumarizar relações do grafo | JSON com summary |

## 4. Clinical Prompt Pattern

```
SYSTEM: You are a clinical nursing reasoning engine.
        Always cite evidence with GRADE level.
        Never recommend without confidence ≥ 0.60.
        Output strictly in the specified JSON schema.

CONTEXT:
  Patient: ICU, 67y, post-op day 2
  Braden: 12 (high risk)
  Comorbidities: diabetes, hypertension
  
KNOWLEDGE (from RAG + graph):
  NANDA 00047: Risk of Impaired Skin Integrity (def: ...)
  NIC 3540: Pressure Management (activities: ...)
  Evidence: "Braden≤12 → UP risk 87%" (GRADE A, DOI:...)
  Similar episode: Case #4823 (recovered with q2h turning)

TASK: Generate nursing care plan with NANDA, NIC, NOC, and explanation.

OUTPUT: { nanda: [...], nic: [...], noc: [...], explanation: "..." }
```

## 5. LLM Providers

| Provider | Model | Use Case | Latency |
|----------|-------|----------|---------|
| Groq | Llama 3.1 70B | Fast inference, templates | ~200ms |
| OpenAI | GPT-4o | Complex reasoning | ~2s |
| Local | Llama 3 8B | Privacy-sensitive | ~500ms |

O NKOS já referencia Groq nos templates (`ai_prompt_templates.json`).

## 6. Safety Guardrails

- **Temperature ≤ 0.3** para outputs clínicos (minimizar alucinação)
- **JSON schema validation** obrigatório no output
- **Confidence threshold** ≥ 0.60 para recomendações
- **Human-in-the-loop** para interventions safety-critical

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-01 | Foundation Model (LLM selection) |
| NIFS-700-19 | Hallucination Prevention |
| NIFS-700-14 | Tool Calling (LLM as tool caller) |
