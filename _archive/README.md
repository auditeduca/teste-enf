# Arquivo — cópias e experimentos

Esta pasta guarda artefatos **fora do caminho canônico** de desenvolvimento. Não apague sem revisar — serve como histórico e pacotes de exportação.

## Conteúdo

| Pasta | O que é | Caminho canônico equivalente |
|-------|---------|------------------------------|
| `exports/apgar-completo/` | Pacote portável Apgar (snapshot para clone/download) | `NIFS/DELIVERY/` |
| `root-snapshots/` | HTML/DDL duplicados que estavam na raiz do repo | `NIFS/DELIVERY/preview_apgar.html`, `NIFS/NIFS_Cognitive_Layers_v5.0_DDL.sql` |
| `delivery-experiments/` | Protótipos de página não usados em produção | `NIFS/DELIVERY/preview_apgar.html` |
| `scripts-iteracao-apgar/` | Scripts one-shot já aplicados (migração CKO/clínico/slim) | `scripts/build_apgar_cko.py`, `scripts/sync_cko_apgar_v3.py` |

## Regra

- **Editar sempre** em `NIFS/DELIVERY/` e `scripts/` (scripts ativos).
- **Não commitar** novas duplicatas na raiz — gerar ZIP em `artifacts/` via `python3 scripts/package_apgar_zip.py`.
