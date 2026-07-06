/**
 * Demo V8 — gotejamento / sepse simulada com IDs NKOS.
 */
import { runV8 } from '../orchestrator.js';
import { resolveEntityCode } from '../identifiers/legacyAliasMap.js';

function buildVitalsSequence(hours = 8) {
  const sequence = [];
  let hr = 110;
  let sbp = 92;
  let dbp = 58;
  let rr = 22;
  let spo2 = 93;
  let temp = 38.1;
  let urine = 35;

  for (let h = 0; h < hours; h++) {
    if (h < 4) {
      hr += 2;
      sbp -= 2;
      spo2 -= 0.4;
      urine -= 2;
    }
    sequence.push({
      heartRate: Math.round(hr),
      systolicBP: Math.round(sbp),
      diastolicBP: Math.round(dbp),
      respiratoryRate: Math.round(rr),
      spo2: Math.round(spo2),
      temperature: Math.round(temp * 10) / 10,
      urineOutput: Math.round(urine),
      gcs: 14,
    });
  }
  return sequence;
}

const sequence = buildVitalsSequence(8);
const initial = sequence[0];
const rest = sequence.slice(1);

console.log('=== CAL-001 V8 Demo (NKOS entity_code) ===\n');
console.log('Legacy n1 →', resolveEntityCode('n1'));
console.log('Legacy i3 →', resolveEntityCode('i3'));
console.log('');

const output = runV8(initial, rest, { numParticles: 400 });

console.log('Resumo:', output.clinicalSummary);
console.log('\nDiagnósticos:');
for (const d of output.diagnoses) {
  console.log(
    `  ${d.entity_code} | ${d.title} | ${(d.probability * 100).toFixed(1)}% | conf ${(d.confidence * 100).toFixed(0)}%`
  );
  console.log(`    Evidências: ${d.evidence.join('; ')}`);
}
console.log('\nRisco (Expected Loss):', output.risk.expectedLoss);
for (const ev of output.risk.events) {
  console.log(`  - ${ev.entity_code}: ${ev.name} P=${(ev.probability * 100).toFixed(1)}% sev=${ev.severity}`);
}
console.log('\nIntervenção MPC:', output.recommendedIntervention.entity_code);
console.log(' ', output.recommendedIntervention.rationale);
