# NKOS 2026 — Validação de Arquivos (Lotes 1+2)

**Data:** 2026-07-05
**Total de arquivos:** 19 (9 + 10)
**Validador:** Solene (NIFS Agent)

---

## Lote 1 — User & Personalization (NKOS Fase 6, schema 2026.1.0)

| # | Arquivo | Entidade | Fase | Records | Status | NIFS Mapping |
|---|---------|----------|------|---------|--------|--------------|
| 1 | users.json | User | 6.1 | 0 (runtime) | ✅ ready | `ni_platform.consent` (user context) |
| 2 | personalization_profiles.json | UserPersonalizationProfile | 6.2 | 5 templates | ✅ complete | Novo: `ni_user.profiles` |
| 3 | user_paths.json | UserPath | 6.3 | 20 templates | ✅ complete | Novo: `ni_user.paths` |
| 4 | profile_questionnaires.json | ProfileQuestionnaire | 6.4 | 3 templates | ✅ complete | Novo: `ni_user.questionnaires` |
| 5 | user_consents.json | UserConsent | 6.5 | 15 templates | ✅ complete | `ni_platform.consent` |
| 6 | content_bookmarks.json | ContentBookmark | 6.6 | 0 (runtime) | ✅ ready | Novo: `ni_content.bookmarks` |
| 7 | content_ratings.json | ContentRating | 6.7 | 0 (runtime) | ✅ ready | Novo: `ni_content.ratings` |
| 8 | patient_context_schema.json | PatientContext | 2026.2.2 | schema only | ✅ ACTIVE | **Bridge DTO** → `ni_reasoning` + `ni_memory` + `ni_world` + `ni_prob` + `ni_temporal` + `ni_graph` |
| 9 | datasets_catalog.json (ANVISA) | AnvisaDataset | 2026.2.12 | 5 | ✅ complete | `ni.medications_anvisa` (data source) |

### Achados Lote 1

**Patient Context Schema é o arquivo mais estratégico.** É o DTO (Data Transfer Object) que conecta o frontend ao backend cognitivo. Mapeamento detalhado:

| Patient Context Field | NIFS Schema | Notas |
|----------------------|-------------|-------|
| demographics | `ni_world.patient_states` | age_group enum bate com `ni.populations` |
| clinical_state.current_diagnoses | `ni_reasoning.hypotheses` | probability field = P(x) ✅ |
| clinical_state.active_interventions | `ni_planner.plan_nodes` / `ni_memory.actions` | status enum aligns |
| clinical_state.risk_factors | `ni_attention.attention_signals` | severity enum aligns |
| clinical_state.contraindications | Safety layer | Novo conceito — adicionar ao safety |
| clinical_state.allergies | Safety layer / `ni.nine_rights_medication` | Cruzar com medicações |
| clinical_state.medications | `ni.medications_anvisa` | drug_code mapeia para ANVISA |
| tool_timeline | `ni_temporal.clinical_events` / `ni.assessment_log` | triggered_diagnoses = NANDA |
| reasoning_continuity.current_hypothesis | `ni_reasoning.hypotheses` | ✅ |
| reasoning_continuity.hypothesis_history | `ni_reasoning.hypotheses` + `ni_prob.belief_updates` | probability + timestamp + evidence |
| reasoning_continuity.decision_chain | `ni_reasoning.trace` | decision + rationale + outcome |
| reasoning_continuity.learning_points | `ni_memory.learnings` | ✅ |
| global_risk_assessment | `ni_reasoning.scores` (risk type) | overall_risk_score 0-1 ✅ |
| tool_intelligence_state.active_connections | `ni_graph.edges` (tool-to-tool) | activation_score = edge weight |
| tool_intelligence_state.suggested_tools | `ni_planner` + `ni_attention` | priority enum aligns |
| preferences | User profile + `ni_platform.consent` | profile_id enum: student, nurse, specialist, educator |
| governance.clinical_validation | `ni_epist.verification_log` | validation_status enum: pending, validated, rejected, requires_review ✅ |

**5 personas definidas:** Student, Academic, Professional, Manager, Enterprise — cada uma com priority_modules, questionnaires e user paths dedicados.

**20 user paths** cobrindo: fundamentos, SAE, simulados, pesquisa NNN, PBE, UTI, emergência, cardiologia, pneumologia, feridas, farmacologia, segurança, qualidade, etc.

**15 consent templates** cobrindo: LGPD (3), GDPR (3), HIPAA (2), COFEN (1), Terms (1), Privacy (1), Cookies (2), Research (1), Enterprise (1).

**5 datasets ANVISA:** DADOS_ABERTOS_MEDICAMENTOS (43K), FILA_ANALISE (23K), PRECOS (20K), RESTRICAO (16K), VIGIMED (5K) — total ~108K registros.

---

## Lote 2 — Legislation & Compliance + Channels (schema 2026.2.9 + NKOS Fase 9)

| # | Arquivo | Entidade | Schema | Records | Status | NIFS Mapping |
|---|---------|----------|--------|---------|--------|--------------|
| 10 | datasets_catalog.json (dup) | AnvisaDataset | 2026.2.12 | 5 | ✅ duplicate | Same as #9 |
| 11 | jurisdictions.json | Jurisdiction | 2026.2.9 | 28 | ✅ complete | Novo: `ni_legis.jurisdictions` |
| 12 | legislation_domains.json | LegislationDomain | 2026.2.9 | 4 | ✅ complete | Novo: `ni_legis.domains` |
| 13 | legislation_instruments.json | LegislationInstrument | 2026.2.9 | 20 | ✅ complete | Novo: `ni_legis.instruments` |
| 14 | legislation_corpus.json | LegislationCorpus | 2026.2.9 | 7 | ✅ complete | Novo: `ni_legis.corpus` |
| 15 | legal_provisions.json | LegalProvision | 2026.2.9 | 12 | ✅ complete | Novo: `ni_legis.provisions` |
| 16 | compulsory_notifications.json | CompulsoryNotificationEntry | 2026.2.9 | 54 | ✅ complete | Novo: `ni_legis.notifications` → cross com `ni.cid_diagnoses` |
| 17 | legislation_tool_links.json | LegislationToolLink | 2026.2.9 | 12 | ✅ complete | Novo: `ni_legis.tool_links` |
| 18 | channels.json | Channel | 2026.1.0 (fase 9.1) | 10 | ✅ complete | `ni_design.components` (output channels) |
| 19 | component_instances.json | ComponentInstance | 2026.1.0 (fase 9.3) | 0 (runtime) | ✅ ready | `ni_design.component_variants` |

### Achados Lote 2

**Legislation Layer é uma base de conhecimento jurídico-floresi completa:**

```
Jurisdiction (28)
  └── LegislationDomain (4)
       └── LegislationInstrument (20)
            ├── LegalProvision (12) — artigos com texto completo + nursing_relevance
            ├── LegislationCorpus (7) — coleções documentais
            ├── CompulsoryNotificationEntry (54) — agravos com CID-10 + SINAN
            └── LegislationToolLink (12) — ligações ferramentas↔leis
```

**Domínios legislativos:**
1. Constitution (CF/1988 — Arts. 196, 198)
2. SUS (Lei 8080/90, Lei 8142/90, Dec 7508/11, Lei 9632/98)
3. Professional (Lei 7498/86 — Arts. 11, 12; COFEN 688/2022)
4. Vigilance (PC4/2017 — Notificação Compulsória)

**54 notificações compulsórias** cobrindo: Cólera, Botulismo, COVID-19, Dengue (casos+óbitos), HIV/AIDS, Tuberculose, Meningite, Sífilis (adquirida+congênita), Violência interpessoal, Acidente trabalho biológico, Câncer ocupacional, HTLV, e mais.

**Cada notificação tem:**
- CID-10 code(s) — link para `ni.cid_diagnoses` ✅
- Periodicidade: immediate_24h ou weekly
- Esferas: MS, SES, SMS (tríplice ou SMS-only)
- Formulário SINAN
- **nursing_guidance_pt** — orientação de enfermagem específica
- evidence_grade: A

**10 canais de saída:**
- Ativos: Web (pt-BR), Web i18n, PDF, Email, RSS, Print (6)
- Prontos: Mobile, API, LMS, Chatbot (4)
- Formatos: HTML, JSON, PDF, SCORM, MJML, XML

---

## Gaps Identificados

### Críticos
1. **Patient Context Schema não tem campo para council_session_id** — falta link direto para `ni_council.sessions`
2. **Contraindications não têm schema no NIFS** — existe em patient_context mas não no DDL v5.0
3. **Allergies não têm tabela própria no NIFS** — apenas em nine_rights_medication

### Recomendados
4. **Criar schema `ni_user`** no NIFS para profiles, paths, questionnaires
5. **Criar schema `ni_legis`** no NIFS para toda a camada legislativa
6. **Adicionar `ni_content.bookmarks` e `ni_content.ratings`** às tabelas existentes
7. **Compulsory notifications deveriam ter NANDA mapping** — hoje só têm CID-10
8. **Channels deveriam integrar com `ni_design.components`** — hoje são separados

### Duplicação
9. **datasets_catalog.json** enviado duas vezes (arquivos #9 e #10 idênticos)

---

## Mapeamento para NIFS — Novos Schemas Recomendados

### `ni_user` (User Intelligence)
```sql
ni_user.profiles        — UserPersonalizationProfile (5 templates)
ni_user.paths           — UserPath (20 templates)
ni_user.questionnaires  — ProfileQuestionnaire (3 templates)
ni_user.bookmarks       — ContentBookmark (runtime)
ni_user.ratings         — ContentRating (runtime)
```

### `ni_legis` (Legislation & Compliance)
```sql
ni_legis.jurisdictions       — Jurisdiction (28)
ni_legis.domains             — LegislationDomain (4)
ni_legis.instruments         — LegislationInstrument (20)
ni_legis.corpus              — LegislationCorpus (7)
ni_legis.provisions          — LegalProvision (12)
ni_legis.notifications       — CompulsoryNotificationEntry (54)
ni_legis.tool_links          — LegislationToolLink (12)
```

### Extensões a schemas existentes
```sql
-- ni.cid_diagnoses: adicionar FK para ni_legis.notifications
-- ni.medications_anvisa: adicionar FK para ni_legis (ANVISA law)
-- ni_design: adicionar channels table
-- ni_platform.consent: já existe, mas expandir para 15 templates LGPD/GDPR/HIPAA
```

---

## Conclusão

O NKOS 2026 está muito mais maduro do que o Excel v4.2 sugeria. Estes 19 arquivos revelam:

1. **Camada de usuário completa** — 5 personas, 20 paths, 3 questionnaires, 15 consents
2. **Patient Context Schema** — DTO que bridgeia frontend ↔ backend cognitivo
3. **Camada legislativa robusta** — 54 notificações compulsórias com CID-10 e nursing guidance
4. **Multi-channel publishing** — 10 canais, 6 ativos
5. **Integração ANVISA** — 5 datasets, ~108K registros

**Para alinhar com NIFS v5.0**, recomendo:
- Adicionar `ni_user` e `ni_legis` como novos schemas no DDL
- Expandir patient_context_schema com campos do council e contraindications
- Adicionar NANDA mapping às compulsory notifications
- Integrar channels ao `ni_design` existente
