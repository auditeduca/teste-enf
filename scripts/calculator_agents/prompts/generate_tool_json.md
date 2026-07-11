# Geração de JSON de calculadora/escala clínica

Gere um objeto JSON completo para uma calculadora ou escala clínica de enfermagem, seguindo o schema `tool.schema.json`.

## Campos obrigatórios

- `id` (UUID v4), `code`, `slug`, `version` ("1.0.0"), `status` ("draft")
- `seo`: title, description, canonical
- `overview`: name, categoryBadge, icon (ex: i-gauge), objective, indication, rating, ratingCount
- `calculator`: inputs (id, type, label, options com score para select), formula (type sum ou expression)
- `interpretation`: ranges com min, max, label, riskLevel, color, clinicalImplications
- `evidence`: foundation, references (array de {text})
- `learning`: tips, examples, quiz (opcional)
- `faq`: array de {q, a}
- `about`: title, html

## Regras

- Português brasileiro (pt-BR)
- Conteúdo clinicamente plausível e baseado em evidências conhecidas
- Para escalas de soma: formula.type = "sum", options com score numérico
- Para fórmulas (IMC etc.): formula.type = "expression", expression com ids dos inputs
- Retorne **somente** o objeto JSON, sem markdown nem comentários
