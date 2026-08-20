# Architecture

Greenfield NIS follows NIFS-900: JSON is the source of truth; HTML is generated; the browser only recalculates.

```
data/tools/{slug}.json
        │  (Draft-07: data/schemas/tool.schema.json)
        ▼
nis_engine.validate  → schema errors
nis_engine.score     → sum | expression
nis_engine.generate  → apps/web/tools/{slug}.html
        │
        ▼
calc-engine.js reads #tool-config and updates the result + clinical steps
```

## Formula types

- `sum` — each select option has a `score`; total is the sum (Apgar, Braden, Glasgow).
- `expression` — identifiers from input ids, arithmetic only (IMC, gotejamento).

Python (`score.safe_eval`) and JavaScript (`calc-engine.safeEval`) both reject anything except digits and `+ - * / ( ) .`.

## Clinical page flow (NIFS-900-02, simplified)

1. Assessment inputs (always visible)
2. Result + interpretation (live)
3. NANDA / NIC / NOC (revealed on submit)
4. Action plan from the matched range (revealed on submit)
5. About, tips, quiz, FAQ, references

Profiles (Urgência / Estudante / Gestor / Acadêmico) and the 10 resource cards are **not** in v0. They come back after the engine and schema are stable.

## Legacy

`NIFS/` is the specification archive. `reference-website/` is the frozen production dump. Do not add calculators there.
