# Avaliação de mercado, notas e inovação

Referência: [12-clinical-intelligence-engine.md](../12-clinical-intelligence-engine.md)

---

## 1. Nota geral

| Contexto | Nota | Comentário |
|----------|------|------------|
| **Arquitetura V8 (spec)** | **8,7 / 10** | Acima de 90% dos sistemas acadêmicos de enfermagem digital |
| **Como protótipo research** | **8,5–9 / 10** | Próximo de Digital Twin / POMDP simplificado |
| **Como produto hospitalar hoje** | **6 / 10** | Falta validação, safety formal, regulatório |
| **Potencial de mercado** | **9 / 10** | Diferencial NANDA como sistema dinâmico + controle |

---

## 2. Notas por categoria

| Categoria | Nota | Comentário |
|-----------|------|------------|
| Arquitetura de IA | 9,5 | State-space + Bayes + controle — muito maduro |
| Modelagem fisiológica | 8,5 | Boa abstração; precisa calibração em dados reais |
| Probabilidade clínica | 9,0 | Superior a regras fixas e scores isolados |
| Explicabilidade | 9,5 | Causal + contrafactual — ponto forte |
| Integração NANDA/NIC/NOC | 9,5 | Diferencial enorme vs mercado |
| Controle / intervenção | 8,5 | NIC como controle — inovação real |
| **Validação clínica** | **5,0** | Maior gargalo |
| Escalabilidade | 8,0 | Depende de pipeline de dados |
| **Segurança regulatória** | **6,0** | Precisa governança tipo software médico |
| Aprendizado automático | 5,5 | Expert-calibrado, não aprendido ainda |
| Produto / UX | 8,5 | NKOS + site + potencial modo UTI |

---

## 3. Comparação com concorrentes

### 3.1 Calculadoras e scores (NEWS2, MEWS, Braden)

```
Entrada → Regra fixa → Score → Resultado
```

| | Eles | CAL-001 V8 |
|---|------|------------|
| Nota | 5/10 | 8,7/10 (spec) |
| Contexto | Snapshot | Estado latente + tempo |
| Incerteza | Não | Belief + variância |
| Intervenção | Não simula | MPC / counterfactual |

### 3.2 Sistemas NANDA/NIC/NOC comerciais

```
Sinais → Checklist → Diagnóstico sugerido → NIC padrão
```

| | Eles | CAL-001 |
|---|------|---------|
| Nota | 6,5/10 | 9/10 (taxonomia) |
| Fisiologia | Fraca | Camada latente |
| NNN | Lista | Grafo 1500 linkages NKOS |
| Previsão | Pouca | Forecast 24h |

### 3.3 CDSS hospitalares (Epic, Oracle Health, Cerner)

| | Eles | CAL-001 |
|---|------|---------|
| Nota | 8/10 | 7/10 hoje, 9+ potencial |
| Força | Dados reais, integração EHR | Modelo causal explícito |
| Fraqueza | Alert fatigue, pouca fisiologia | Sem validação em produção |

### 3.4 IA clínica LLM (Copilot, Med-PaLM)

| | Eles | CAL-001 |
|---|------|---------|
| Nota | 8,5/10 | Complementar |
| Força | Texto, documentação | Dinâmica fisiológica, controle |
| Fraqueza | Alucinação, sem simulação | Precisa camada linguística V9 |

**Ideal:** `V8 Engine + LLM explicador + EHR`

### 3.5 Digital Twin / ICU analytics (research)

| | Research ICU | CAL-001 V8 |
|---|--------------|------------|
| Nota | 9/10 | 8,7/10 spec |
| Paridade | POMDP, filtros, simulação | Mesma classe de modelo |
| Diferencial CAL | — | **NANDA-NIC-NOC integrado** |

---

## 4. Onde a inovação é real

### 4.1 NANDA como sistema dinâmico

Mercado: `Paciente → Diagnóstico`

CAL-001: `Paciente → Estado fisiológico → Diagnósticos competindo → NIC altera trajetória`

### 4.2 NIC como variável de controle

```
S_{t+1} = f(S_t, u_t)
```

Aproxima enfermagem de engenharia de controle e medicina de precisão — **raro em produtos de enfermagem**.

### 4.3 Incerteza operacional

Não apenas “risco 80%”, mas:

- probabilidade 80%
- confiança 62%
- variância alta → solicitar nova observação

### 4.4 NKOS como base de conhecimento

244 NANDA + 1500 linkages NNN + 50 árvores de decisão — **ativo já materializado no repo**, não só slide de arquitetura.

---

## 5. Onde melhorar (notas baixas)

| Nota baixa | Causa | Melhoria | Nota alvo |
|------------|-------|----------|-----------|
| Validação 5 | Sem MIMIC/calibração | ETL + Brier + model card | 8,5 |
| Segurança 6 | Sem safety layer formal | `safety_rules.json` + block | 9 |
| ML 5,5 | Pesos manuais | Physics + NN residual | 9 |
| Regulatório 5 | Sem AI safety file | Docs + auditoria | 8 |

Detalhes: [03-pendencias-roadmap.md](03-pendencias-roadmap.md)

---

## 6. Potencial por segmento

| Segmento | Estrelas | Observação |
|----------|----------|------------|
| Acadêmico / pesquisa | ⭐⭐⭐⭐⭐ | Arquitetura publicável |
| Produto educacional enfermagem | ⭐⭐⭐⭐⭐ | NKOS + SAE + simulação |
| Startup HealthTech | ⭐⭐⭐⭐ | Diferencial claro |
| Hospital produção | ⭐⭐⭐ | Exige V8.5 + estudo clínico |

---

## 7. Evolução de classe de produto

| Versão | Classe |
|--------|--------|
| V4 | Rule engine + probabilidade |
| V5 | Simulador clínico heurístico-causal-temporal |
| V6–V7 | Observador de estado + controlador (POMDP approx) |
| V8 | Gêmeo digital clínico probabilístico |
| V8.5 | CDSS confiável (calibrado + safe) |
| V9 | Neuro-symbolic + RL offline |

---

## 8. Conclusão para investidor / banca

> O CAL-001 não compete em “mais uma calculadora com IA”. Compete em **transformar NANDA-NIC-NOC em um sistema probabilístico causal controlável** — proximidade com Digital Twin clínico, com taxonomia de enfermagem nativa.

**Maior risco:** não é técnico — é **validação, dados e governança**.

**Maior ativo já existente:** **NKOS v4.4** materializado em JSON (terminologias + NNN + ferramentas + site).

---

## 9. Nota projetada pós-V8.5

| Área | Hoje | V8.5 |
|------|------|------|
| IA | 9,5 | 10 |
| Fisiologia | 8,5 | 9,5 |
| NANDA/NIC/NOC | 9,5 | 10 |
| Segurança | 6 | 9 |
| Validação | 5 | 8,5 |
| Aprendizado | 7 | 9 |
| **Média produto** | **7,8** | **~9,4** |
