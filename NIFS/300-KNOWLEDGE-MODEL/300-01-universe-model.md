# NIFS-300-01: Universe Model

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-01                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o universo clínico que o NIS modela. Este documento não fala de banco de dados — fala do **mundo**.

## 2. Philosophy

Antes de uma única tabela, antes de um schema, antes de um tipo de dado — precisamos definir **o que existe no mundo** que estamos modelando.

O universo clínico de enfermagem é composto por entidades, relações, eventos e contextos que existem independentemente de qualquer implementação técnica.

## 3. The Clinical Universe

### 3.1 Entities (Who and What)

| Entity | Description | Examples |
|--------|-------------|----------|
| **Paciente** | Sujeito do cuidado | João, 67a, pós-operatório |
| **Família** | Contexto social do paciente | Esposa, filha cuidadora |
| **Enfermeiro** | Agente do cuidado | Enf. Ana, UTI adulto, plantão noturno |
| **Equipe** | Coletivo multidisciplinar | Médico, fisioterapeuta, nutricionista |
| **Hospital** | Instituição de saúde | Hospital Municipal, UTI 3º andar |
| **Enfermaria** | Unidade de cuidado | UTI adulto, 10 leitos, 7 ocupados |
| **Consulta** | Episódio de cuidado | Internação #1234, 5 dias |
| **Avaliação** | Coleta estruturada de dados | Braden = 12, Glasgow = 11 |
| **Observação** | Dado clínico individual | PA = 90x60, SpO2 = 88% |
| **Achado** | Interpretação de observação | "Hipotensão", "Hipoxemia" |
| **Diagnóstico** | Conclusão clínica NANDA-I | 00047: Risco de Úlcera por Pressão |
| **Intervenção** | Ação terapêutica NIC | 3540: Reduzir Pressão |
| **Meta** | Objetivo clínico | "Manter integridade tissular" |
| **Desfecho** | Resultado medido NOC | 1101: Integridade Tissular = 3 |
| **Evidência** | Suporte científico | GRADE A, Cochrane 2023 |
| **Protocolo** | Sequência padronizada | Protocolo de Sepse 2024 |
| **Medicamento** | Farmaco terapêutico | Noradrenalina 4mg/4mL |
| **Dispositivo** | Recurso técnico | Bomba de infusão, ventilador |
| **Risco** | Probabilidade de dano | Risco de queda = alto |
| **Evento** | Ocorrência clínica | Queda às 03:15, code blue |
| **Sintoma** | Manifestação subjetiva | "Dor 7/10" |
| **Sinal** | Manifestação objetiva | Taquicardia, palidez |
| **Recurso** | Meio disponível | Leito UTI, equipo, gaze |
| **Cultura** | Contexto sociocultural | PT-BR, família presente, religião |

### 3.2 Relationships (How They Connect)

```
Paciente —has—→ Observações
Paciente —has—→ História Clínica
Paciente —located_in—→ Enfermaria
Enfermaria —part_of—→ Hospital
Enfermeiro —assigned_to—→ Enfermaria
Enfermeiro —cares_for—→ Paciente
Observação —indicates—→ Achado
Achado —supports—→ Diagnóstico
Achado —contradicts—→ Diagnóstico
Diagnóstico —treated_by—→ Intervenção
Intervenção —improves—→ Desfecho
Diagnóstico —measured_by—→ Desfecho (NOC)
Diagnóstico —evidenced_by—→ Evidência
Intervenção —part_of—→ Protocolo
Protocolo —applies_to—→ População
Medicamento —interacts_with—→ Medicamento
Medicamento —contraindicated_for—→ Condição
Evento —causes—→ Evento
Evento —preceded_by—→ Evento
Risco —mitigated_by—→ Intervenção
```

### 3.3 Events (What Happens Over Time)

| Event Type | Examples | Temporal Pattern |
|------------|----------|-----------------|
| **Admissão** | Internação, transferência | Point in time |
| **Observação** | Aferição de PA, escala de dor | Continuous/periodic |
| **Avaliação** | Braden, Glasgow, NEWS2 | Periodic (6h, 12h, 24h) |
| **Diagnóstico** | Confirmação NANDA | Event + revision |
| **Intervenção** | Mudança de decúbito, medicação | Discrete actions |
| **Evento adverso** | Queda, flebite, úlcera | Unpredictable |
| **Estabilização** | Recuperação de crise | Gradual trend |
| **Deterioração** | Sepse, parada | Rapid decline |
| **Alta** | Transferência, alta hospitalar | Terminal event |
| **Reavaliação** | Nova sessão de raciocínio | Triggered by deviation |

### 3.4 Contexts (What Modifies Decisions)

O universo não é só entidades. É também **contexto** — o que muda a decisão mesmo com os mesmos dados clínicos:

```
Paciente grave (PA 80x40, Glasgow 8)
    + UTI lotada (10/10, ratio 1:4)
    + Sem bomba de infusão disponível
    + Plantão noturno (2 enfermeiros)
    + Sem especialista em neurologia
    = DECISÃO DIFERENTE do mesmo paciente
      em UTI com 3 vagas, 6 enfermeiros, e bomba disponível
```

## 4. Populations

O universo se segmenta por populações com características distintas:

| Population | Code | Unique Considerations |
|-----------|------|----------------------|
| Adulto | ADULT | Padrão de referência |
| Pediatria | PED | Doseagem, parâmetros vitais diferentes |
| Neonatal | NEO | APGAR, temperatura, alimentação |
| Gestante | PREG | Fisiologia alterada, segurança fetal |
| UTI | ICU | Gravidade, monitorização contínua |
| APS | APS | Ambulatorial, prevenção, crônicos |
| Geriatria | GERI | Polifarmácia, fragilidade, delirium |
| Oncologia | ONCO | Imunossupressão, dor, cuidados paliativos |
| Pós-operatório | POSTOP | Risco cirúrgico, dor, mobilização |

Cada população tem **priors bayesianos diferentes**. P(Úlcera por Pressão|Braden 12) é diferente em UTI vs. APS.

## 5. The Universe vs. The Model

Este documento define o **universo** — o mundo real. Os documentos seguintes definem como este universo é **modelado**:

| NIFS Section | What It Models |
|--------------|---------------|
| NIFS-300 (Knowledge Model) | Entidades como conceitos formais |
| NIFS-400 (Data Model) | Entidades como tabelas e colunas |
| NIFS-500 (Knowledge Graph) | Relacionamentos como arestas |
| NIFS-600 (Reasoning) | Processo cognitivo sobre o universo |
| NIFS-700 (AI) | IA operando sobre o universo |

## 6. Boundary Definition

### Inside the Universe (Modeled)

- Pacientes anônimos (hash, sem PII)
- Observações clínicas estruturadas
- Diagnósticos NANDA-I, intervenções NIC, desfechos NOC
- Protocolos clínicos de enfermagem
- Contexto hospitalar (enfermaria, recursos, equipe)
- Evidências científicas
- Eventos temporais clínicos

### Outside the Universe (Not Modeled)

- Prescrição médica de medicamentos (verificado, não prescrito)
- Diagnóstico médico (CID é cross-mapped, não diagnosticado)
- Faturamento e gestão administrativa
- Prontuário eletrônico completo (integração via FHIR)
- Imagens médicas (DICOM — referenciado, não interpretado)
- Regulação de leitos (sistema externo)

## 7. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — complete universe definition | Leivis Melo |
