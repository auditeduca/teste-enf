# Drive inbox (quarentena)

Arquivos baixados do Google Drive para este lote. **Não são CKO-MD.**

Procedimento: INTERNAL_FIRST → search Drive (fileId observado) → snapshot SHA-256 → COMPARE → GAP ONLY → changeset MD+REG antes de promoção.

Neste ciclo:

- `locales/` — extraído de `locales.zip` (19 códigos, somente `cookies.json` e `footer.json`)
- `INVENTORY.json` — catálogo observado, inclusive o que **não** foi ingerido

HTML histórico (`braden.html`, `pages_full.zip`, etc.) permanece no Drive. Não copiar para `data/tools`.
