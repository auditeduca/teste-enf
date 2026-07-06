/**
 * Demo APGAR + MCTS + User Context — NKOS V9.
 */
import { runApgarMCTS } from '../apgar/orchestratorApgar.js';
import {
  demoModerateDistressComponents,
  demoSevereDistressComponents,
} from '../apgar/apgarScale.js';

function printScenario(title, components, userContext) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(title);
  console.log('='.repeat(60));
  console.log('User context:', JSON.stringify(userContext, null, 2));

  const out = runApgarMCTS(components, userContext);

  console.log('\n', out.clinicalSummary);
  console.log('\nObservação:', out.observation.entity_code, '→ score', out.observation.score);
  console.log('RULE:', out.rule_layer.clinical_state, `(${out.rule_layer.clinical_state_pt})`);

  console.log('\nDiagnósticos:');
  for (const d of out.probabilistic_layer.diagnoses) {
    console.log(`  ${d.entity_code} | ${d.title} | P=${(d.probability * 100).toFixed(1)}%`);
  }

  const nic = out.intervention_layer.selected_nic;
  console.log('\nMCTS → NIC:', nic.entity_code, `conf=${(nic.confidence * 100).toFixed(0)}%`);
  console.log(' ', nic.rationale);

  if (out.explainability) {
    console.log('\nCausal path:', out.explainability.causal_path.join(' → '));
    console.log('Drivers:', out.explainability.drivers.map((d) => d.feature).join(', '));
  }

  console.log('\nSafety:', out.safety_layer.status, out.safety_layer.rules_triggered);
  console.log('Content:', out.content.content_type, '/', out.content.render_mode);
  if (out.content.deck) {
    console.log('Flashcards:', out.content.deck.length, 'cards');
  }
}

console.log('=== APGAR + MCTS + User Context (NKOS V9 demo) ===');

printScenario('1. Clínico padrão — depressão moderada (score ~4)', demoModerateDistressComponents(), {
  mode: 'standard',
  device: 'desktop',
  urgency: 'medium',
  content_type: 'clinical',
});

printScenario('2. Emergência mobile — depressão severa (score ~3)', demoSevereDistressComponents(), {
  mode: 'emergency',
  device: 'mobile',
  urgency: 'critical',
  content_type: 'clinical',
});

printScenario('3. Educação flashcard — mesmo caso moderado', demoModerateDistressComponents(), {
  mode: 'education',
  device: 'mobile',
  urgency: 'low',
  content_type: 'flashcard',
  scale_mode: 'deep_clinical',
  interaction_goal: 'learn',
});

printScenario('4. Exame — deep clinical desktop', demoModerateDistressComponents(), {
  mode: 'exam',
  device: 'desktop',
  scale_mode: 'deep_clinical',
  content_type: 'simulation',
  interaction_goal: 'train',
});

console.log('\nDone.\n');
