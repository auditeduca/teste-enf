# Clinical Engine V8 — Referência

Motor probabilístico de referência para **CAL-001 / DRIP_RATE_CAL_001**, alinhado ao Master Data NKOS v2026.2.2.

## Requisitos

- Node.js 18+

## Execução

```bash
cd clinical-engine
npm run demo          # simulação 8h com Particle Filter + MPC
npm run demo:apgar    # APGAR + MCTS + User Context (V9 demo)
npm run test:ids      # valida entity_code vs datasets
```

## Estrutura

| Pasta | Função |
|-------|--------|
| `identifiers/` | `entity_code`, aliases legados, arestas demo |
| `core/` | tipos, distribuições |
| `inference/` | Particle Filter, likelihood |
| `physiology/` | modelo generativo |
| `diagnosis/` | CPTs NANDA com entity_code |
| `control/` | NIC + MPC |
| `apgar/` | APGAR + MCTS + User Context (`runApgarMCTS`) |
| `orchestrator.js` | `runV8()` |

## API

```javascript
import { runV8 } from './orchestrator.js';

const output = runV8(initialVitals, vitalsSequence, { numParticles: 300 });
```

Campos principais: `belief`, `diagnoses[]`, `risk.expectedLoss`, `recommendedIntervention.entity_code`.

## Documentação completa

- [07-v8-implementacao-referencia.md](../docs/clinical-engine/07-v8-implementacao-referencia.md)
- [08-identificadores-nkos.md](../docs/clinical-engine/08-identificadores-nkos.md)
- [09-v9-proximos-passos.md](../docs/clinical-engine/09-v9-proximos-passos.md)
- [10-evidencia-validacao-externa.md](../docs/clinical-engine/10-evidencia-validacao-externa.md)
- [11-apgar-mcts-user-context.md](../docs/clinical-engine/11-apgar-mcts-user-context.md)

## Aviso clínico

Saída **educacional/simulação**. Não usar para decisão clínica real sem calibração e validação (Grau A).
