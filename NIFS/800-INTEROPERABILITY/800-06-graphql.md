# NIFS-800-06: GraphQL

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-06                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a API GraphQL do NIS como alternativa ao REST para clientes que precisam de queries flexíveis.

## 2. GraphQL Schema Overview

```graphql
type Query {
  patient(id: ID!): Patient
  nanda(code: String!): NursingDiagnosis
  nic(code: String!): NursingIntervention
  searchNANDA(query: String!, limit: Int): [NursingDiagnosis]
  reasoningSession(id: ID!): ReasoningSession
}

type Mutation {
  createAssessment(input: AssessmentInput!): Assessment
  runReasoning(input: ReasoningInput!): ReasoningResult
  updateCarePlan(id: ID!, input: CarePlanInput!): CarePlan
}

type Subscription {
  reasoningUpdate(sessionId: ID!): ReasoningUpdate
  safetyAlert(patientId: ID!): SafetyAlert
}
```

## 3. Use Cases

| Client | Preferred API | Reason |
|--------|--------------|--------|
| Web app (NKOS Platform) | GraphQL | Flexible UI queries |
| External EHR integration | REST/FHIR | Standard compliance |
| Mobile app | GraphQL | Minimize data transfer |
| Analytics | REST + Bulk | Batch export |

## 4. NIS Implementation

GraphQL roda como camada sobre as mesmas entities do backend. Schema gerado automaticamente a partir do DDL.

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-05 | REST (primary API) |
| NIFS-900-03 | API Gateway |
