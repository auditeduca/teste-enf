# NIFS-300-11: States

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-11                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir estados clínicos do paciente e como o NIS os modela e transiciona.

## 2. State Hierarchy

```
Patient State (ni_world.patient_states)
├── Severity: stable | moderate | critical | terminal
├── Acuity: numeric score
├── Consciousness: alert | lethargic | stuporous | comatose
├── Mobility: independent | assisted | bedridden
└── Isolation: none | contact | droplet | airborne

Ward State (ni_world.ward_states)
├── Occupancy: beds in use / total
├── Nurse-patient ratio
└── Resources available
```

## 3. State Transitions

`ni_temporal.state_transitions` rastreia mudanças:

```
stable → moderate_risk → critical → stabilized → moderate_risk → stable
```

Cada transição tem:
- `from_state`, `to_state`
- `trigger_event_id` (what caused the transition)
- `timestamp`
- `intervention_applied` (what was done)

## 4. State in Reasoning

O motor de raciocínio usa o estado atual como contexto:

```
Patient state: critical + ICU + nurse_ratio 1:4
    → adjusts attention weights (critical signals get +0.3)
    → adjusts urgency thresholds (escalation sooner)
    → activates safety protocols (critical care bundle)
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-10 | Events (events trigger transitions) |
| NIFS-600-15 | Digital Twin (state simulation) |
