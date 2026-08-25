# Avaliação: CKO-INS-AI-PROJECT-001 como constituição Day Zero

**Identificador:** `CKO-INS-AI-PROJECT-001`  
**Versão avaliada:** 1.0.0  
**Estado do documento:** `CONTROLLED_DRAFT`  
**Epistemic status desta avaliação:** misto (marcado por seção)

## Conclusão

A instrução **é adequada** para ser a constituição operacional inicial deste repositório. Ela estabelece o que a IA pode e não pode assumir quando o ambiente começa vazio, e corrige a arquitetura para:

```text
camada EXISTE no bootstrap
        ≠
camada POPULADA
        ≠
camada IMPLEMENTADA
        ≠
camada ASSURED
```

CKO-MD e CKO-REG não são “áreas posteriores”. Toda camada L instancia L-MD + L-REG + L-DOMAIN desde o registro.

Esta avaliação **não** declara o projeto completo, em produção, nem conforme.

## O que a constituição acerta

- Identidade antes de regulação (fonte-first ≠ REG-first).
- Um conceito → uma identidade → várias projeções.
- Estados epistemológicos obrigatórios; proibição de PASS por inferência.
- DOCUMENTADO ≠ IMPLEMENTADO ≠ VALIDADO ≠ ASSURED ≠ PUBLICADO.
- Recuperação antes de reconstrução.
- Proibição de inventar ID, hash, cláusula, DOI, URL oficial.
- Renderer PRESENTATION_ONLY; Studio não reescreve verdade clínica.
- 44 camadas como objetos governados no dia zero, inclusive SEO, A11Y, LGPD, sustentabilidade, APIs, CAAT, IPE, ALCOA++, twin, agentes, COSO/COBIT (como frameworks de controle, não autoridade clínica).
- Fail-closed e comunicação obrigatória de gaps.

## Admin e frontend

A constituição já separa Studio/Admin de verdade canônica. Neste repositório a comunicação é **direta e contratual**, não um CMS paralelo:

```text
GitHub JSON (cko_core, cko_md, cko_reg, cko_assurance, data/tools)
        │
        ├── renderer → frontend (index, tools)
        └── renderer → admin.html + admin/*.json
```

Admin lê os mesmos contratos que o frontend projeta. Não há POST, login nem escrita de fórmula. API admin autenticada: `UNKNOWN` neste repositório.

## GitHub first

Tudo o que este changeset afirma está versionado neste GitHub. Anexos de sessão (Supabase 172 entities, SQL v2.1.0, matriz 21/21 PASS) permanecem `SOURCE_DERIVED` / `EVIDENCE_PENDING` até bytes+hash e reperformance.

## Taxonomia 21 vs 44

`data/layers-21.json` é o corte de produto v0.1. `cko_core/layer_registry.json` é o registry constitucional de 44 camadas. Relação: `RELATED_TAXONOMY`, não substituição 1:1 silenciosa.

## Gaps que a constituição corretamente força a registrar

| Item | Status |
|---|---|
| Gerador UUIDv7 | HOLD — identidade operacional = `business_key` |
| 172 entities / SQL live | NÃO ENCONTRADO neste repo |
| Texto de cláusula COSO/COBIT/ISO licenciada | CLAUSE_TEXT_UNAVAILABLE |
| Bindings campo-norma | APPLICABILITY_UNVERIFIED |
| SAE clínica autônoma | NÃO IMPLEMENTADA |
| Digital twin sincronizado | population = 0 |
| Produção assegurada | HOLD |

## Redação permitida

> A constituição CKO-INS-AI-PROJECT-001 está adotada como CONTROLLED_DRAFT. As 44 camadas estão registradas (44/44 business keys únicos, uuid null). Admin e frontend compartilham os contratos GitHub. O lote clínico permanece HOLD.

Redação proibida: “base completa”, “produção pronta”, “conformidade COSO/COBIT”, “MD 100% completo”.
