# NIFS-300-23: Institutions

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-23                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir instituições de saúde como contexto organizacional que influencia decisões clínicas.

## 2. Institution Model

```
Institution
├── type: hospital | clinic | UBS | UPA | home_care
├── level: terciário | secundário | primário
├── ward_types[]: ICU, ER, general, pediatrics, neonatal
├── resources: equipment, beds, medications
├── staff: ratios, specialties available
├── protocols: institutional variants
├── jurisdiction: ni_legis.jurisdictions
└── compliance frameworks: LGPD, HIPAA, COFEN
```

## 3. World Model Integration

```
ni_world.hospital_states → hospital_identifier → institution
ni_world.ward_states → ward_identifier → institution
ni_world.resource_states → ward_identifier → institution
ni_world.staff_states → ward_identifier → institution
```

## 4. Institution-Aware Decisions

```
Institution: UBS (primary care, no ICU)
Patient: critical, needs vasopressor
    ↓
Decision: Stabilize + transfer to tertiary hospital
Protocol: Emergency transfer protocol activated
    ↓ vs
Institution: Hospital terciário (ICU available)
Patient: critical, needs vasopressor
    ↓
Decision: Start noradrenaline in ICU, full protocol
```

## 5. Jurisdiction Integration

Instituições estão vinculadas a jurisdições (`ni_legis.jurisdictions`):

```
Hospital São Paulo → JUR.BR.SP → CVE-SP guidelines
Hospital Salvador → JUR.BR.BA → SESAB guidelines
```

Cada jurisdição pode ter protocolos e notificações compulsórias específicas além das federais.

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-21 | Resources (institutional resources) |
| NIFS-300-22 | Professionals (staff context) |
| NIFS-600-07 | World Model (institution as context) |
