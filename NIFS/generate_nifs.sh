#!/bin/bash
# NIFS — Nursing Intelligence Foundation Specification
# Generator script: creates the complete document skeleton
# Version: 1.0.0 | Date: 2026-07-05

set -e

NIFS_ROOT="NIFS"

# ============================================================================
# TEMPLATE FUNCTION
# ============================================================================
generate_doc() {
  local filepath="$1"
  local doc_id="$2"
  local title="$3"
  local purpose="$4"

  mkdir -p "$(dirname "$filepath")"

  cat > "$filepath" << EOF
# ${doc_id}: ${title}

| Field         | Value         |
|---------------|---------------|
| Document ID   | ${doc_id}     |
| Status        | Draft         |
| Version       | 1.0.0         |
| Owner         | —             |
| Reviewers     | —             |
| Last Updated  | 2026-07-05    |

## 1. Purpose

${purpose}

## 2. Scope

[Define what this document covers and what it does not cover]

## 3. Definitions

| Term | Definition |
|------|-----------|
| —    | —         |

## 4. Specification

[The specification content goes here]

### 4.1 Requirements

[R-001] Requirement description

### 4.2 Constraints

[C-001] Constraint description

### 4.3 Data Model

[Entity definitions, if applicable]

## 5. Rationale

[Why this design decision was made]

## 6. Alternatives Considered

| Alternative | Pros | Cons | Decision |
|------------|------|------|----------|
| —          | —    | —    | —        |

## 7. Dependencies

| Document | Relationship |
|----------|-------------|
| —        | —           |

## 8. References

- [1] Reference

## 9. Change Log

| Version | Date       | Change          | Author |
|---------|------------|-----------------|--------|
| 1.0.0   | 2026-07-05 | Initial draft   | —      |
EOF
}

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================
echo "Creating NIFS directory structure..."

SECTIONS=(
  "000-INTRODUCTION"
  "100-FOUNDATION"
  "200-CLINICAL-SCIENCE"
  "300-KNOWLEDGE-MODEL"
  "400-DATA-MODEL"
  "500-KNOWLEDGE-GRAPH"
  "600-CLINICAL-REASONING"
  "700-AI-ARCHITECTURE"
  "800-INTEROPERABILITY"
  "900-PLATFORM"
  "1000-SECURITY"
  "1100-GOVERNANCE"
  "1200-QUALITY"
  "1300-DEVELOPER-GUIDE"
  "1400-DEPLOYMENT"
  "1500-ROADMAP"
  "APPENDIX"
)

for section in "${SECTIONS[@]}"; do
  mkdir -p "${NIFS_ROOT}/${section}"
done

# ============================================================================
# 000 — INTRODUCTION
# ============================================================================
echo "  000-INTRODUCTION..."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-01-vision.md" \
  "NIFS-000-01" "Vision" \
  "Define the long-term vision of the Nursing Intelligence System as a clinical reasoning platform."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-02-mission.md" \
  "NIFS-000-02" "Mission" \
  "Define the mission of the NIS platform in the nursing intelligence ecosystem."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-03-objectives.md" \
  "NIFS-000-03" "Objectives" \
  "List the strategic and tactical objectives of the platform."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-04-scope.md" \
  "NIFS-000-04" "Project Scope" \
  "Define the boundaries of the NIS platform."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-05-non-goals.md" \
  "NIFS-000-05" "Non-Goals" \
  "Explicitly state what the platform is NOT designed to do."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-06-target-audience.md" \
  "NIFS-000-06" "Target Audience" \
  "Identify the primary and secondary users of the platform."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-07-clinical-philosophy.md" \
  "NIFS-000-07" "Clinical Philosophy" \
  "Define the clinical principles that guide all design decisions."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-08-engineering-philosophy.md" \
  "NIFS-000-08" "Engineering Philosophy" \
  "Define the engineering principles that guide implementation decisions."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-09-definitions.md" \
  "NIFS-000-09" "Definitions" \
  "Provide canonical definitions for all key terms used across the specification."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-10-glossary.md" \
  "NIFS-000-10" "Glossary" \
  "Comprehensive glossary of clinical and technical terms."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-11-abbreviations.md" \
  "NIFS-000-11" "Abbreviations" \
  "Complete list of abbreviations and acronyms used in the specification."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-12-references.md" \
  "NIFS-000-12" "References" \
  "Authoritative references: standards, publications, regulations."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-13-document-structure.md" \
  "NIFS-000-13" "Document Structure" \
  "Explain how the NIFS specification is organized and how to navigate it."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-14-versioning.md" \
  "NIFS-000-14" "Versioning" \
  "Define the semantic versioning strategy for the specification."
generate_doc "${NIFS_ROOT}/000-INTRODUCTION/000-15-changelog.md" \
  "NIFS-000-15" "Change Log" \
  "Track all changes to the NIFS specification across versions."

# ============================================================================
# 100 — FOUNDATION
# ============================================================================
echo "  100-FOUNDATION..."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-01-architecture-principles.md" \
  "NIFS-100-01" "Architecture Principles" \
  "Define the foundational architecture principles for the platform."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-02-design-principles.md" \
  "NIFS-100-02" "Design Principles" \
  "Define the design principles that guide all component design."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-03-core-values.md" \
  "NIFS-100-03" "Core Values" \
  "Define the core values that the platform embodies."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-04-human-centered-ai.md" \
  "NIFS-100-04" "Human-Centered AI" \
  "Define how AI augments rather than replaces nursing judgment."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-05-evidence-based-nursing.md" \
  "NIFS-100-05" "Evidence-Based Nursing" \
  "Define how evidence-based practice is embedded in the platform."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-06-clinical-safety.md" \
  "NIFS-100-06" "Clinical Safety" \
  "Define safety requirements and guardrails for clinical recommendations."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-07-trustworthy-ai.md" \
  "NIFS-100-07" "Trustworthy AI" \
  "Define the trust framework for AI-generated clinical insights."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-08-explainability.md" \
  "NIFS-100-08" "Explainability" \
  "Define requirements for clinical explainability and decision tracing."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-09-interoperability.md" \
  "NIFS-100-09" "Interoperability" \
  "Define interoperability principles and standards adoption strategy."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-10-scalability.md" \
  "NIFS-100-10" "Scalability" \
  "Define scalability requirements and strategies."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-11-maintainability.md" \
  "NIFS-100-11" "Maintainability" \
  "Define maintainability standards and practices."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-12-extensibility.md" \
  "NIFS-100-12" "Extensibility" \
  "Define how the platform supports extension without modification."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-13-modularity.md" \
  "NIFS-100-13" "Modularity" \
  "Define the modular architecture and component boundaries."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-14-domain-driven-design.md" \
  "NIFS-100-14" "Domain-Driven Design" \
  "Define how DDD principles are applied to the nursing domain."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-15-data-driven-design.md" \
  "NIFS-100-15" "Data-Driven Design" \
  "Define how data shapes design decisions in the platform."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-16-event-driven-design.md" \
  "NIFS-100-16" "Event-Driven Design" \
  "Define the event-driven architecture for clinical events."
generate_doc "${NIFS_ROOT}/100-FOUNDATION/100-17-knowledge-driven-design.md" \
  "NIFS-100-17" "Knowledge-Driven Design" \
  "Define how the knowledge graph drives system behavior."

# ============================================================================
# 200 — CLINICAL SCIENCE
# ============================================================================
echo "  200-CLINICAL-SCIENCE..."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-01-nursing-science.md" \
  "NIFS-200-01" "Nursing Science" \
  "Establish the scientific foundation of nursing within the platform."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-02-nursing-process.md" \
  "NIFS-200-02" "Nursing Process" \
  "Define the nursing process (ADPIE) as the core clinical workflow."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-03-assessment.md" \
  "NIFS-200-03" "Assessment" \
  "Define the assessment phase: data collection, Gordon patterns, clinical observation."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-04-clinical-judgment.md" \
  "NIFS-200-04" "Clinical Judgment" \
  "Define the Tanner model of clinical judgment and its implementation."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-05-clinical-reasoning.md" \
  "NIFS-200-05" "Clinical Reasoning" \
  "Define clinical reasoning as the cognitive process the system models."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-06-decision-making.md" \
  "NIFS-200-06" "Decision Making" \
  "Define clinical decision-making frameworks supported by the platform."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-07-critical-thinking.md" \
  "NIFS-200-07" "Critical Thinking" \
  "Define how critical thinking is modeled in the reasoning engine."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-08-evidence-based-practice.md" \
  "NIFS-200-08" "Evidence-Based Practice" \
  "Define EBP integration: evidence sourcing, grading, and application."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-09-patient-safety.md" \
  "NIFS-200-09" "Patient Safety" \
  "Define patient safety requirements and safety goal integration."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-10-care-coordination.md" \
  "NIFS-200-10" "Care Coordination" \
  "Define how care coordination is modeled across shifts and teams."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-11-risk-management.md" \
  "NIFS-200-11" "Risk Management" \
  "Define risk stratification, prediction, and mitigation strategies."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-12-documentation.md" \
  "NIFS-200-12" "Documentation" \
  "Define nursing documentation standards and structured recording."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-13-ethics.md" \
  "NIFS-200-13" "Ethics" \
  "Define the ethical framework for AI-assisted nursing decisions."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-14-terminologies-nanda.md" \
  "NIFS-200-14" "Terminology: NANDA-I" \
  "Define NANDA-I taxonomy integration: diagnoses, domains, classes."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-15-terminologies-nic.md" \
  "NIFS-200-15" "Terminology: NIC" \
  "Define NIC taxonomy integration: interventions, domains, classes."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-16-terminologies-noc.md" \
  "NIFS-200-16" "Terminology: NOC" \
  "Define NOC taxonomy integration: outcomes, indicators, scales."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-17-terminologies-icnp.md" \
  "NIFS-200-17" "Terminology: ICNP" \
  "Define ICNP integration and cross-mapping strategy."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-18-terminologies-snomed.md" \
  "NIFS-200-18" "Terminology: SNOMED CT" \
  "Define SNOMED CT integration and concept mapping."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-19-terminologies-loinc.md" \
  "NIFS-200-19" "Terminology: LOINC" \
  "Define LOINC integration for observations and lab results."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-20-terminologies-icd.md" \
  "NIFS-200-20" "Terminology: ICD" \
  "Define ICD-10/ICD-11 integration for medical diagnoses cross-mapping."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-21-terminologies-rxnorm.md" \
  "NIFS-200-21" "Terminology: RxNorm" \
  "Define RxNorm integration for medication normalization."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-22-terminologies-atc.md" \
  "NIFS-200-22" "Terminology: ATC" \
  "Define ATC classification system for medications."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-23-terminologies-fhir.md" \
  "NIFS-200-23" "Terminology: FHIR" \
  "Define FHIR R4 terminology resources and code systems."
generate_doc "${NIFS_ROOT}/200-CLINICAL-SCIENCE/200-24-terminologies-iso18104.md" \
  "NIFS-200-24" "Terminology: ISO 18104" \
  "Define ISO 18104:2003 integration for nursing diagnoses and actions."

# ============================================================================
# 300 — KNOWLEDGE MODEL
# ============================================================================
echo "  300-KNOWLEDGE-MODEL..."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-01-universe-model.md" \
  "NIFS-300-01" "Universe Model" \
  "Define the complete universe of clinical entities the platform models."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-02-entity-catalog.md" \
  "NIFS-300-02" "Entity Catalog" \
  "Complete catalog of all entities in the knowledge model."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-03-relationship-catalog.md" \
  "NIFS-300-03" "Relationship Catalog" \
  "Complete catalog of all relationships between entities."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-04-concept-taxonomy.md" \
  "NIFS-300-04" "Concept Taxonomy" \
  "Define the hierarchical taxonomy of clinical concepts."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-05-clinical-ontology.md" \
  "NIFS-300-05" "Clinical Ontology" \
  "Define the formal ontology for nursing concepts."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-06-semantic-model.md" \
  "NIFS-300-06" "Semantic Model" \
  "Define the semantic model: meaning, context, and interpretation."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-07-inheritance.md" \
  "NIFS-300-07" "Inheritance" \
  "Define inheritance hierarchies in the knowledge model."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-08-composition.md" \
  "NIFS-300-08" "Composition" \
  "Define composition relationships (whole-part) in the model."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-09-aggregation.md" \
  "NIFS-300-09" "Aggregation" \
  "Define aggregation relationships in the model."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-10-events.md" \
  "NIFS-300-10" "Events" \
  "Define clinical events and their role in the temporal model."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-11-states.md" \
  "NIFS-300-11" "States" \
  "Define patient states and state transitions."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-12-observations.md" \
  "NIFS-300-12" "Observations" \
  "Define the observation model: vital signs, scores, findings."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-13-findings.md" \
  "NIFS-300-13" "Findings" \
  "Define clinical findings derived from observations."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-14-assessments.md" \
  "NIFS-300-14" "Assessments" \
  "Define structured assessments and assessment tools."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-15-diagnoses.md" \
  "NIFS-300-15" "Diagnoses" \
  "Define nursing diagnoses and the diagnostic process."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-16-interventions.md" \
  "NIFS-300-16" "Interventions" \
  "Define nursing interventions and intervention selection."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-17-goals.md" \
  "NIFS-300-17" "Goals" \
  "Define clinical goals and goal-setting mechanisms."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-18-outcomes.md" \
  "NIFS-300-18" "Outcomes" \
  "Define clinical outcomes and outcome measurement."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-19-evidence.md" \
  "NIFS-300-19" "Evidence" \
  "Define the evidence model: sources, grading, and application."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-20-protocols.md" \
  "NIFS-300-20" "Protocols" \
  "Define clinical protocols and their representation."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-21-resources.md" \
  "NIFS-300-21" "Resources" \
  "Define clinical resources: devices, equipment, medications."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-22-professionals.md" \
  "NIFS-300-22" "Professionals" \
  "Define the professional model: roles, competencies, responsibilities."
generate_doc "${NIFS_ROOT}/300-KNOWLEDGE-MODEL/300-23-institutions.md" \
  "NIFS-300-23" "Institutions" \
  "Define the institutional model: hospitals, wards, units."

# ============================================================================
# 400 — DATA MODEL
# ============================================================================
echo "  400-DATA-MODEL..."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-01-naming-convention.md" \
  "NIFS-400-01" "Naming Convention" \
  "Define naming conventions for all database artifacts."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-02-data-dictionary.md" \
  "NIFS-400-02" "Data Dictionary" \
  "The canonical data dictionary — the Excel v4.2 in specification form."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-03-tables.md" \
  "NIFS-400-03" "Tables" \
  "Complete table catalog with schemas and purposes."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-04-columns.md" \
  "NIFS-400-04" "Columns" \
  "Complete column catalog across all tables."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-05-data-types.md" \
  "NIFS-400-05" "Data Types" \
  "Define the type system used across the data model."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-06-constraints.md" \
  "NIFS-400-06" "Constraints" \
  "Define all constraints: primary keys, foreign keys, unique, check."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-07-indexes.md" \
  "NIFS-400-07" "Indexes" \
  "Define the indexing strategy for all tables."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-08-uuid-strategy.md" \
  "NIFS-400-08" "UUID Strategy" \
  "Define the UUID generation and usage strategy."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-09-version-fields.md" \
  "NIFS-400-09" "Version Fields" \
  "Define semantic versioning fields for all knowledge entities."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-10-audit-fields.md" \
  "NIFS-400-10" "Audit Fields" \
  "Define audit trail fields for all tables."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-11-metadata.md" \
  "NIFS-400-11" "Metadata" \
  "Define the metadata model: entity metadata, column metadata, table metadata."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-12-localization.md" \
  "NIFS-400-12" "Localization" \
  "Define the localization strategy for multilingual support."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-13-multilingual-support.md" \
  "NIFS-400-13" "Multilingual Support" \
  "Define how labels, descriptions, and content are stored in multiple languages."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-14-enumerations.md" \
  "NIFS-400-14" "Enumerations" \
  "Complete catalog of all enumerated types."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-15-code-systems.md" \
  "NIFS-400-15" "Code Systems" \
  "Define all external code systems and their internal representation."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-16-reference-data.md" \
  "NIFS-400-16" "Reference Data" \
  "Define reference data: standard values, lookup tables, fixed vocabularies."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-17-master-data.md" \
  "NIFS-400-17" "Master Data" \
  "Define master data: NANDA, NIC, NOC, ISO terms, medications, protocols."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-18-validation-rules.md" \
  "NIFS-400-18" "Validation Rules" \
  "Define data validation rules and integrity constraints."
generate_doc "${NIFS_ROOT}/400-DATA-MODEL/400-19-business-rules.md" \
  "NIFS-400-19" "Business Rules" \
  "Define clinical business rules that constrain data and behavior."

# ============================================================================
# 500 — KNOWLEDGE GRAPH
# ============================================================================
echo "  500-KNOWLEDGE-GRAPH..."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-01-node-types.md" \
  "NIFS-500-01" "Node Types" \
  "Define all node types in the clinical knowledge graph."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-02-edge-types.md" \
  "NIFS-500-02" "Edge Types" \
  "Define all edge types (relationship types) in the knowledge graph."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-03-properties.md" \
  "NIFS-500-03" "Properties" \
  "Define properties for nodes and edges."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-04-weights.md" \
  "NIFS-500-04" "Weights" \
  "Define the weighting system for edges in the knowledge graph."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-05-confidence.md" \
  "NIFS-500-05" "Confidence" \
  "Define confidence scoring for graph elements."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-06-evidence-links.md" \
  "NIFS-500-06" "Evidence Links" \
  "Define how evidence is linked to graph elements."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-07-clinical-pathways.md" \
  "NIFS-500-07" "Clinical Pathways" \
  "Define clinical pathways as graph traversals."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-08-ontology-mapping.md" \
  "NIFS-500-08" "Ontology Mapping" \
  "Define mappings between the knowledge graph and external ontologies."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-09-temporal-graph.md" \
  "NIFS-500-09" "Temporal Graph" \
  "Define the temporal dimension of the knowledge graph."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-10-probabilistic-graph.md" \
  "NIFS-500-10" "Probabilistic Graph" \
  "Define probabilistic edges and Bayesian network structure."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-11-reasoning-graph.md" \
  "NIFS-500-11" "Reasoning Graph" \
  "Define how reasoning traverses the knowledge graph."
generate_doc "${NIFS_ROOT}/500-KNOWLEDGE-GRAPH/500-12-inference-graph.md" \
  "NIFS-500-12" "Inference Graph" \
  "Define inference rules and graph-based inference."

# ============================================================================
# 600 — CLINICAL REASONING
# ============================================================================
echo "  600-CLINICAL-REASONING..."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-01-clinical-workflow.md" \
  "NIFS-600-01" "Clinical Workflow" \
  "Define the end-to-end clinical reasoning workflow."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-02-reasoning-pipeline.md" \
  "NIFS-600-02" "Reasoning Pipeline" \
  "Define the cognitive pipeline: Observation → Hypothesis → Evidence → Diagnosis → Plan → Monitor → Reassess."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-03-assessment-pipeline.md" \
  "NIFS-600-03" "Assessment Pipeline" \
  "Define the structured assessment pipeline and data collection."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-04-hypothesis-generation.md" \
  "NIFS-600-04" "Hypothesis Generation" \
  "Define how the system generates diagnostic hypotheses from observations."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-05-differential-diagnosis.md" \
  "NIFS-600-05" "Differential Diagnosis" \
  "Define the differential diagnosis ranking and elimination process."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-06-evidence-ranking.md" \
  "NIFS-600-06" "Evidence Ranking" \
  "Define how evidence is ranked and weighted in reasoning."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-07-decision-trees.md" \
  "NIFS-600-07" "Decision Trees" \
  "Define decision tree structures for clinical decisions."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-08-bayesian-network.md" \
  "NIFS-600-08" "Bayesian Network" \
  "Define the Bayesian network for probabilistic reasoning."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-09-risk-prediction.md" \
  "NIFS-600-09" "Risk Prediction" \
  "Define risk prediction models and scoring systems."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-10-clinical-attention.md" \
  "NIFS-600-10" "Clinical Attention" \
  "Define the attention mechanism for prioritizing observations."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-11-goal-planning.md" \
  "NIFS-600-11" "Goal Planning" \
  "Define how clinical goals are set and pursued."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-12-intervention-selection.md" \
  "NIFS-600-12" "Intervention Selection" \
  "Define how interventions are selected and prioritized."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-13-outcome-prediction.md" \
  "NIFS-600-13" "Outcome Prediction" \
  "Define outcome prediction models and confidence estimation."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-14-simulation.md" \
  "NIFS-600-14" "Simulation" \
  "Define the simulation engine for testing clinical plans."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-15-digital-twin.md" \
  "NIFS-600-15" "Digital Twin" \
  "Define the patient digital twin model."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-16-clinical-memory.md" \
  "NIFS-600-16" "Clinical Memory" \
  "Define episodic memory: storing and retrieving clinical experiences."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-17-learning-loop.md" \
  "NIFS-600-17" "Learning Loop" \
  "Define the feedback learning loop: plan → outcome → update."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-18-consensus-engine.md" \
  "NIFS-600-18" "Consensus Engine" \
  "Define the multi-agent consensus mechanism for clinical decisions."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-19-explainability.md" \
  "NIFS-600-19" "Explainability" \
  "Define the explainability framework for all clinical recommendations."
generate_doc "${NIFS_ROOT}/600-CLINICAL-REASONING/600-20-reasoning-trace.md" \
  "NIFS-600-20" "Reasoning Trace" \
  "Define the reasoning trace format and storage."

# ============================================================================
# 700 — AI ARCHITECTURE
# ============================================================================
echo "  700-AI-ARCHITECTURE..."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-01-foundation-model.md" \
  "NIFS-700-01" "Foundation Model" \
  "Define the foundation model strategy for Nurse-PaLM."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-02-rag.md" \
  "NIFS-700-02" "RAG" \
  "Define Retrieval-Augmented Generation for clinical knowledge."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-03-embeddings.md" \
  "NIFS-700-03" "Embeddings" \
  "Define the embedding strategy for clinical content."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-04-vector-search.md" \
  "NIFS-700-04" "Vector Search" \
  "Define vector search for semantic similarity retrieval."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-05-knowledge-retrieval.md" \
  "NIFS-700-05" "Knowledge Retrieval" \
  "Define the knowledge retrieval pipeline."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-06-memory.md" \
  "NIFS-700-06" "Memory" \
  "Define the AI memory architecture: episodic, semantic, working."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-07-planning.md" \
  "NIFS-700-07" "Planning" \
  "Define the AI planning module for intervention sequencing."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-08-agents.md" \
  "NIFS-700-08" "Agents" \
  "Define the agent architecture for the clinical council."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-09-multi-agent.md" \
  "NIFS-700-09" "Multi-Agent" \
  "Define the multi-agent coordination and communication."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-10-consensus.md" \
  "NIFS-700-10" "Consensus" \
  "Define the consensus protocol for multi-agent decisions."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-11-reflection.md" \
  "NIFS-700-11" "Reflection" \
  "Define the self-reflection mechanism for quality improvement."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-12-verification.md" \
  "NIFS-700-12" "Verification" \
  "Define the verification layer for AI outputs."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-13-prompt-strategy.md" \
  "NIFS-700-13" "Prompt Strategy" \
  "Define prompt engineering strategies for clinical reasoning."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-14-tool-calling.md" \
  "NIFS-700-14" "Tool Calling" \
  "Define the tool/function calling architecture."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-15-fine-tuning.md" \
  "NIFS-700-15" "Fine-Tuning" \
  "Define the fine-tuning strategy for domain adaptation."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-16-model-registry.md" \
  "NIFS-700-16" "Model Registry" \
  "Define the model registry and versioning for AI components."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-17-evaluation.md" \
  "NIFS-700-17" "Evaluation" \
  "Define the evaluation framework for AI components."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-18-safety-layer.md" \
  "NIFS-700-18" "Safety Layer" \
  "Define the safety layer that guards all AI outputs."
generate_doc "${NIFS_ROOT}/700-AI-ARCHITECTURE/700-19-hallucination-prevention.md" \
  "NIFS-700-19" "Hallucination Prevention" \
  "Define strategies to prevent AI hallucination in clinical contexts."

# ============================================================================
# 800 — INTEROPERABILITY
# ============================================================================
echo "  800-INTEROPERABILITY..."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-01-fhir.md" \
  "NIFS-800-01" "FHIR" \
  "Define FHIR R4 resource profiles and conformance."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-02-hl7.md" \
  "NIFS-800-02" "HL7 v2" \
  "Define HL7 v2 message support and mapping."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-03-openehr.md" \
  "NIFS-800-03" "OpenEHR" \
  "Define OpenEHR archetype support."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-04-smart.md" \
  "NIFS-800-04" "SMART on FHIR" \
  "Define SMART on FHIR app launch support."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-05-rest.md" \
  "NIFS-800-05" "REST" \
  "Define the REST API design standards."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-06-graphql.md" \
  "NIFS-800-06" "GraphQL" \
  "Define the GraphQL schema and resolver strategy."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-07-grpc.md" \
  "NIFS-800-07" "gRPC" \
  "Define gRPC service definitions for internal communication."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-08-webhooks.md" \
  "NIFS-800-08" "Webhooks" \
  "Define webhook events and subscription model."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-09-import.md" \
  "NIFS-800-09" "Import" \
  "Define data import pipelines and formats."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-10-export.md" \
  "NIFS-800-10" "Export" \
  "Define data export pipelines and formats."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-11-terminology-services.md" \
  "NIFS-800-11" "Terminology Services" \
  "Define terminology services: lookup, mapping, validation."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-12-code-mapping.md" \
  "NIFS-800-12" "Code Mapping" \
  "Define cross-terminology code mapping strategy."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-13-bulk-data.md" \
  "NIFS-800-13" "Bulk Data" \
  "Define bulk data transfer capabilities."
generate_doc "${NIFS_ROOT}/800-INTEROPERABILITY/800-14-synchronization.md" \
  "NIFS-800-14" "Synchronization" \
  "Define data synchronization with external systems."

# ============================================================================
# 900 — PLATFORM
# ============================================================================
echo "  900-PLATFORM..."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-01-backend.md" \
  "NIFS-900-01" "Backend" \
  "Define the backend architecture."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-02-frontend.md" \
  "NIFS-900-02" "Frontend" \
  "Define the frontend architecture."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-03-architecture.md" \
  "NIFS-900-03" "Architecture" \
  "Define the overall platform architecture."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-04-modules.md" \
  "NIFS-900-04" "Modules" \
  "Define the module decomposition of the platform."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-05-services.md" \
  "NIFS-900-05" "Services" \
  "Define the service catalog."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-06-microservices.md" \
  "NIFS-900-06" "Microservices" \
  "Define microservices boundaries and communication."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-07-monolith.md" \
  "NIFS-900-07" "Monolith Strategy" \
  "Define when to use monolithic vs. modular deployment."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-08-api-gateway.md" \
  "NIFS-900-08" "API Gateway" \
  "Define the API gateway pattern and routing."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-09-scheduler.md" \
  "NIFS-900-09" "Scheduler" \
  "Define the task scheduling system."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-10-queues.md" \
  "NIFS-900-10" "Queues" \
  "Define the message queue architecture."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-11-caching.md" \
  "NIFS-900-11" "Caching" \
  "Define the caching strategy across layers."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-12-search-engine.md" \
  "NIFS-900-12" "Search Engine" \
  "Define the search engine architecture."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-13-analytics.md" \
  "NIFS-900-13" "Analytics" \
  "Define the analytics and reporting platform."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-14-logging.md" \
  "NIFS-900-14" "Logging" \
  "Define the logging strategy and standards."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-15-monitoring.md" \
  "NIFS-900-15" "Monitoring" \
  "Define the monitoring and alerting system."
generate_doc "${NIFS_ROOT}/900-PLATFORM/900-16-observability.md" \
  "NIFS-900-16" "Observability" \
  "Define the observability stack: traces, metrics, logs."

# ============================================================================
# 1000 — SECURITY
# ============================================================================
echo "  1000-SECURITY..."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-01-authentication.md" \
  "NIFS-1000-01" "Authentication" \
  "Define authentication mechanisms and identity management."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-02-authorization.md" \
  "NIFS-1000-02" "Authorization" \
  "Define authorization models and access control."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-03-rbac.md" \
  "NIFS-1000-03" "RBAC" \
  "Define Role-Based Access Control for the platform."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-04-abac.md" \
  "NIFS-1000-04" "ABAC" \
  "Define Attribute-Based Access Control extensions."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-05-encryption.md" \
  "NIFS-1000-05" "Encryption" \
  "Define encryption at rest, in transit, and in use."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-06-audit.md" \
  "NIFS-1000-06" "Audit" \
  "Define the audit trail and tamper-proof logging."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-07-consent.md" \
  "NIFS-1000-07" "Consent" \
  "Define patient consent management."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-08-privacy.md" \
  "NIFS-1000-08" "Privacy" \
  "Define privacy requirements and data protection."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-09-lgpd.md" \
  "NIFS-1000-09" "LGPD" \
  "Define LGPD (Brazilian GDPR) compliance requirements."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-10-hipaa.md" \
  "NIFS-1000-10" "HIPAA" \
  "Define HIPAA compliance considerations."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-11-gdpr.md" \
  "NIFS-1000-11" "GDPR" \
  "Define GDPR compliance considerations."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-12-secrets.md" \
  "NIFS-1000-12" "Secrets Management" \
  "Define secrets management and rotation."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-13-backups.md" \
  "NIFS-1000-13" "Backups" \
  "Define backup strategy and retention."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-14-disaster-recovery.md" \
  "NIFS-1000-14" "Disaster Recovery" \
  "Define disaster recovery and business continuity."
generate_doc "${NIFS_ROOT}/1000-SECURITY/1000-15-threat-model.md" \
  "NIFS-1000-15" "Threat Model" \
  "Define the threat model and mitigation strategies."

# ============================================================================
# 1100 — GOVERNANCE
# ============================================================================
echo "  1100-GOVERNANCE..."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-01-knowledge-governance.md" \
  "NIFS-1100-01" "Knowledge Governance" \
  "Define how clinical knowledge is governed, reviewed, and approved."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-02-clinical-governance.md" \
  "NIFS-1100-02" "Clinical Governance" \
  "Define clinical governance and oversight structures."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-03-technical-governance.md" \
  "NIFS-1100-03" "Technical Governance" \
  "Define technical governance and architecture review."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-04-versioning.md" \
  "NIFS-1100-04" "Versioning" \
  "Define versioning strategy for all platform artifacts."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-05-approval-workflow.md" \
  "NIFS-1100-05" "Approval Workflow" \
  "Define the approval workflow for knowledge changes."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-06-review-process.md" \
  "NIFS-1100-06" "Review Process" \
  "Define the review process for specifications and implementations."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-07-ownership.md" \
  "NIFS-1100-07" "Ownership" \
  "Define ownership model for each domain and component."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-08-change-requests.md" \
  "NIFS-1100-08" "Change Requests" \
  "Define the change request process."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-09-deprecation.md" \
  "NIFS-1100-09" "Deprecation" \
  "Define the deprecation process for knowledge and features."
generate_doc "${NIFS_ROOT}/1100-GOVERNANCE/1100-10-release-management.md" \
  "NIFS-1100-10" "Release Management" \
  "Define the release management process."

# ============================================================================
# 1200 — QUALITY
# ============================================================================
echo "  1200-QUALITY..."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-01-testing.md" \
  "NIFS-1200-01" "Testing" \
  "Define the testing strategy: unit, integration, e2e."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-02-clinical-validation.md" \
  "NIFS-1200-02" "Clinical Validation" \
  "Define clinical validation methodology and acceptance criteria."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-03-benchmark.md" \
  "NIFS-1200-03" "Benchmark" \
  "Define performance and accuracy benchmarks."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-04-performance.md" \
  "NIFS-1200-04" "Performance" \
  "Define performance requirements and SLAs."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-05-coverage.md" \
  "NIFS-1200-05" "Coverage" \
  "Define coverage requirements: code, knowledge, clinical scenarios."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-06-data-quality.md" \
  "NIFS-1200-06" "Data Quality" \
  "Define data quality metrics and monitoring."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-07-knowledge-quality.md" \
  "NIFS-1200-07" "Knowledge Quality" \
  "Define knowledge quality metrics and review cycles."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-08-evidence-quality.md" \
  "NIFS-1200-08" "Evidence Quality" \
  "Define evidence quality grading (GRADE) and requirements."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-09-acceptance-criteria.md" \
  "NIFS-1200-09" "Acceptance Criteria" \
  "Define acceptance criteria for clinical content and features."
generate_doc "${NIFS_ROOT}/1200-QUALITY/1200-10-certification.md" \
  "NIFS-1200-10" "Certification" \
  "Define certification requirements and processes."

# ============================================================================
# 1300 — DEVELOPER GUIDE
# ============================================================================
echo "  1300-DEVELOPER-GUIDE..."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-01-folder-structure.md" \
  "NIFS-1300-01" "Folder Structure" \
  "Define the standard folder structure for all repositories."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-02-naming-standards.md" \
  "NIFS-1300-02" "Naming Standards" \
  "Define naming standards for all code artifacts."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-03-coding-standards.md" \
  "NIFS-1300-03" "Coding Standards" \
  "Define coding standards for all languages used."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-04-git-workflow.md" \
  "NIFS-1300-04" "Git Workflow" \
  "Define the Git branching and workflow strategy."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-05-ci-cd.md" \
  "NIFS-1300-05" "CI/CD" \
  "Define continuous integration and delivery pipelines."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-06-branch-strategy.md" \
  "NIFS-1300-06" "Branch Strategy" \
  "Define branch naming, protection, and lifecycle."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-07-commit-convention.md" \
  "NIFS-1300-07" "Commit Convention" \
  "Define commit message conventions (Conventional Commits)."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-08-documentation.md" \
  "NIFS-1300-08" "Documentation" \
  "Define documentation standards and generation."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-09-code-review.md" \
  "NIFS-1300-09" "Code Review" \
  "Define the code review process and standards."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-10-generators.md" \
  "NIFS-1300-10" "Generators" \
  "Define code generation from the NIFS specification."
generate_doc "${NIFS_ROOT}/1300-DEVELOPER-GUIDE/1300-11-templates.md" \
  "NIFS-1300-11" "Templates" \
  "Define project and code templates."

# ============================================================================
# 1400 — DEPLOYMENT
# ============================================================================
echo "  1400-DEPLOYMENT..."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-01-docker.md" \
  "NIFS-1400-01" "Docker" \
  "Define Docker containerization standards."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-02-kubernetes.md" \
  "NIFS-1400-02" "Kubernetes" \
  "Define Kubernetes orchestration configuration."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-03-infrastructure.md" \
  "NIFS-1400-03" "Infrastructure" \
  "Define infrastructure as code."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-04-cloud.md" \
  "NIFS-1400-04" "Cloud" \
  "Define cloud provider strategy and multi-cloud considerations."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-05-monitoring.md" \
  "NIFS-1400-05" "Monitoring" \
  "Define production monitoring and alerting."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-06-scaling.md" \
  "NIFS-1400-06" "Scaling" \
  "Define horizontal and vertical scaling strategies."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-07-high-availability.md" \
  "NIFS-1400-07" "High Availability" \
  "Define HA architecture and failover."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-08-backups.md" \
  "NIFS-1400-08" "Backups" \
  "Define production backup strategy."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-09-migration.md" \
  "NIFS-1400-09" "Migration" \
  "Define database migration strategy and tooling."
generate_doc "${NIFS_ROOT}/1400-DEPLOYMENT/1400-10-release-pipeline.md" \
  "NIFS-1400-10" "Release Pipeline" \
  "Define the release pipeline from commit to production."

# ============================================================================
# 1500 — ROADMAP
# ============================================================================
echo "  1500-ROADMAP..."
generate_doc "${NIFS_ROOT}/1500-ROADMAP/1500-01-milestones.md" \
  "NIFS-1500-01" "Milestones" \
  "Define project milestones and target dates."
generate_doc "${NIFS_ROOT}/1500-ROADMAP/1500-02-releases.md" \
  "NIFS-1500-02" "Releases" \
  "Define release plan and versioning schedule."
generate_doc "${NIFS_ROOT}/1500-ROADMAP/1500-03-feature-matrix.md" \
  "NIFS-1500-03" "Feature Matrix" \
  "Define the feature matrix across releases."
generate_doc "${NIFS_ROOT}/1500-ROADMAP/1500-04-future-research.md" \
  "NIFS-1500-04" "Future Research" \
  "Define research directions and open investigations."
generate_doc "${NIFS_ROOT}/1500-ROADMAP/1500-05-known-limitations.md" \
  "NIFS-1500-05" "Known Limitations" \
  "Document known limitations of the current platform."
generate_doc "${NIFS_ROOT}/1500-ROADMAP/1500-06-open-questions.md" \
  "NIFS-1500-06" "Open Questions" \
  "Document open questions awaiting resolution."
generate_doc "${NIFS_ROOT}/1500-ROADMAP/1500-07-research-agenda.md" \
  "NIFS-1500-07" "Research Agenda" \
  "Define the research agenda for Nurse-PaLM evolution."

# ============================================================================
# APPENDIX
# ============================================================================
echo "  APPENDIX..."
generate_doc "${NIFS_ROOT}/APPENDIX/A-glossary.md" \
  "NIFS-APP-A" "Glossary" \
  "Complete glossary of all terms used in the specification."
generate_doc "${NIFS_ROOT}/APPENDIX/B-clinical-dictionary.md" \
  "NIFS-APP-B" "Clinical Dictionary" \
  "Dictionary of clinical terms with definitions and mappings."
generate_doc "${NIFS_ROOT}/APPENDIX/C-ontology.md" \
  "NIFS-APP-C" "Ontology Reference" \
  "Complete ontology reference document."
generate_doc "${NIFS_ROOT}/APPENDIX/D-reference-tables.md" \
  "NIFS-APP-D" "Reference Tables" \
  "All reference tables and lookup data."
generate_doc "${NIFS_ROOT}/APPENDIX/E-evidence-matrix.md" \
  "NIFS-APP-E" "Evidence Matrix" \
  "GRADE evidence matrix and grading criteria."
generate_doc "${NIFS_ROOT}/APPENDIX/F-mathematical-models.md" \
  "NIFS-APP-F" "Mathematical Models" \
  "Mathematical formulas for probability, attention, and learning."
generate_doc "${NIFS_ROOT}/APPENDIX/G-algorithms.md" \
  "NIFS-APP-G" "Algorithms" \
  "Algorithm specifications for reasoning, attention, and consensus."
generate_doc "${NIFS_ROOT}/APPENDIX/H-examples.md" \
  "NIFS-APP-H" "Examples" \
  "Worked examples of clinical reasoning scenarios."
generate_doc "${NIFS_ROOT}/APPENDIX/I-clinical-cases.md" \
  "NIFS-APP-I" "Clinical Cases" \
  "Reference clinical cases for validation and testing."
generate_doc "${NIFS_ROOT}/APPENDIX/J-json-schemas.md" \
  "NIFS-APP-J" "JSON Schemas" \
  "JSON Schema definitions for all API payloads."
generate_doc "${NIFS_ROOT}/APPENDIX/K-sql-templates.md" \
  "NIFS-APP-K" "SQL Templates" \
  "SQL templates generated from the data dictionary."
generate_doc "${NIFS_ROOT}/APPENDIX/L-fhir-profiles.md" \
  "NIFS-APP-L" "FHIR Profiles" \
  "FHIR R4 profile definitions."
generate_doc "${NIFS_ROOT}/APPENDIX/M-erd.md" \
  "NIFS-APP-M" "ERD" \
  "Entity-Relationship Diagram reference."
generate_doc "${NIFS_ROOT}/APPENDIX/N-knowledge-graph.md" \
  "NIFS-APP-N" "Knowledge Graph Visualization" \
  "Knowledge graph structure and visualization."
generate_doc "${NIFS_ROOT}/APPENDIX/O-sequence-diagrams.md" \
  "NIFS-APP-O" "Sequence Diagrams" \
  "Sequence diagrams for key clinical workflows."
generate_doc "${NIFS_ROOT}/APPENDIX/P-state-machines.md" \
  "NIFS-APP-P" "State Machines" \
  "State machine definitions for clinical states."
generate_doc "${NIFS_ROOT}/APPENDIX/Q-bpmn.md" \
  "NIFS-APP-Q" "BPMN" \
  "BPMN process diagrams for clinical workflows."
generate_doc "${NIFS_ROOT}/APPENDIX/R-c4-model.md" \
  "NIFS-APP-R" "C4 Model" \
  "C4 architecture model: Context, Container, Component, Code."
generate_doc "${NIFS_ROOT}/APPENDIX/S-adr.md" \
  "NIFS-APP-S" "Architecture Decision Records" \
  "Index of all Architecture Decision Records."

# ============================================================================
# DONE
# ============================================================================
TOTAL=$(find "${NIFS_ROOT}" -name "*.md" | wc -l)
echo ""
echo "✅ NIFS skeleton created: ${TOTAL} documents across ${#SECTIONS[@]} sections"
echo "   Root: ${NIFS_ROOT}/"
