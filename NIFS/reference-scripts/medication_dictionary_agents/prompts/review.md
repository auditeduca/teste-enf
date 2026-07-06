Revise a proposta de entrada DICT de medicamento.

Checklist:
1. parent_entity_code === drug_ref_code e começa com DRUG.
2. entity_code === {concept_code}_DICT_001
3. definition_pt adequada para enfermagem, sem prescrever dose específica sem contexto
4. evidence_grade A com fonte plausível
5. Sem credenciais ou API keys

Retorne JSON:
{
  "decision": "approve" | "revise" | "reject",
  "notes_pt": "...",
  "blockers": []
}
