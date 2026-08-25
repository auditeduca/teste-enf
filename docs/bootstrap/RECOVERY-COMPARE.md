# Recovery → Compare → Gap

**Epistemic status deste arquivo:** misto, marcado por linha.

## OBSERVED (neste repositório, working tree)

- Branch `cursor/cko-greenfield-app-2bf6` com motor `sum`/`expression`, 5 objetos em `data/tools`, dual-render, inspector, pytest.
- Constituição e registries Day Zero adicionados neste changeset.

## SOURCE_DERIVED (anexos da sessão; NÃO verificados ao vivo aqui)

- `CKO-MD-REG-Database-v2.1.0-2026-08-25-Live-State.md` alega Supabase com 172 entities, 44 layers, 10 instruments, RLS desabilitado.
- README do pacote SQL v2.1.0 cita schema, migration e manifesto SHA-256.

## NÃO ENCONTRADO neste workspace (EVIDENCE_PENDING)

- `CKO-MD-REG-Database-v2.1.0-2026-08-25-Canonical-Schema.sql`
- Additive migration SQL
- Manifesto de hashes do pacote SQL
- Consulta live ao Supabase nesta execução

## NÃO REPERFORMADO

- Matriz de fechamento v6.5.1-R5 que declara PASS estrutural 21/21: é **claim documental do anexo**, não reperformance deste repo. Não copiado como PASS.

## GAP ONLY

1. UUIDv7 generator HOLD — identidade operacional = business_key.
2. 44 camadas M0; população de domínio das camadas = 0 neste bootstrap (os 5 pilotos são candidatos de domínio, sem golden record MD).
3. Banco/Postgres não materializado neste GitHub.
4. RLS: finding SOURCE_DERIVED; nenhuma alteração de RLS feita.
5. COSO/COBIT: registry sem texto de cláusula.
6. Admin API autenticada: UNKNOWN.
7. Design System oficial: anexo JSON descreve outro runtime de estilos; tokens deste repo (`#1A3E74`) coincidem em navy mas **não** promovem o anexo a canonical token sem confirmação no DS governado.

## Próximo gate

Definir gerador UUIDv7 testado **ou** manter business_key. Não importar 172 entities sem os SQL/bytes/hash e sem COMPARE.
