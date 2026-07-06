/**
 * Valida entity_code do motor contra datasets/clinical e master proposal.
 */
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { nandaNodes } from '../diagnosis/nandaGraph.js';
import { availableInterventions } from '../control/interventionModel.js';
import { ENGINE_META, NANDA, NIC } from '../identifiers/nkosEntityCodes.js';
import { SAMPLE_ENGINE_EDGES } from '../identifiers/edgeRelations.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

function loadJson(rel) {
  const p = join(root, rel);
  if (!existsSync(p)) return null;
  return JSON.parse(readFileSync(p, 'utf8'));
}

const diagnoses = loadJson('datasets/clinical/nursing_diagnoses.json')?.records ?? [];
const interventions = loadJson('datasets/clinical/nursing_interventions.json')?.records ?? [];
const proposal = loadJson('datasets/metadata/master_code_sequence_proposal.json');

const diagCodes = new Set(diagnoses.map((d) => d.diagnosis_code?.replace('.', '_')));
const nicCodes = new Set(interventions.map((i) => i.intervention_code?.replace('.', '_')));

const proposalCodes = new Set();
if (proposal?.examples) {
  for (const code of Object.values(proposal.examples)) {
    if (typeof code === 'string') proposalCodes.add(code);
  }
}
if (Array.isArray(proposal?.concepts)) {
  for (const concept of proposal.concepts) {
    for (const art of concept.artifacts ?? []) {
      if (art.entity_code) proposalCodes.add(art.entity_code);
    }
  }
}

const engineCodes = [
  ENGINE_META.engine_id,
  ...Object.values(NANDA),
  ...Object.values(NIC),
  ...nandaNodes.map((n) => n.entity_code),
  ...availableInterventions.map((i) => i.entity_code).filter((c) => c !== 'NIC.NULL'),
];

let ok = true;
console.log('=== Validação entity_code (clinical-engine) ===\n');

for (const code of engineCodes) {
  const inClinical = diagCodes.has(code) || nicCodes.has(code) || code.includes('CAL_');
  const inProposal = proposalCodes.has(code);
  const status = inClinical || inProposal ? 'OK' : 'WARN';
  if (status === 'WARN') ok = false;
  console.log(`${status} ${code} clinical=${inClinical} proposal=${inProposal}`);
}

console.log('\nArestas demo (relation_type):');
for (const edge of SAMPLE_ENGINE_EDGES) {
  console.log(`  ${edge.from} --[${edge.relation_type}]--> ${edge.to}`);
}

process.exit(ok ? 0 : 1);
