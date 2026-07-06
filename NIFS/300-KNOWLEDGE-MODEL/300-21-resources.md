# NIFS-300-21: Resources

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-21                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir recursos clínicos e institucionais que afetam decisões de enfermagem.

## 2. Resource Types

| Type | Example | NIS Table |
|------|---------|-----------|
| Equipment | Bomba de infusão, ventilador, monitor | `ni_world.resource_states` |
| Medication | Noradrenalina disponível? | `ni.medications_anvisa` |
| Bed | UTI leito disponível? | `ni_world.ward_states` |
| Staff | Enfermeiro especialista em plantão? | `ni_world.staff_states` |
| Content | Artigo, video, infográfico | `ni_content.items` |
| Asset | Ícones, imagens, SVGs | NKOS `assets.json` (1000) |

## 3. Resource-Aware Reasoning

```
Patient: critical, needs vasopressor
    ↓ World Model check
Ward: UTI, nurse_ratio 1:4
Resources: bomba_infusão = 2 available
    ↓
Decision: Start noradrenaline via infusion pump
    ↓ If no pump available
Fallback: Manual titration with enhanced monitoring frequency
```

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-07 | World Model (resource context) |
| NIFS-300-22 | Professionals (staff resources) |
| NIFS-300-23 | Institutions (institutional resources) |
